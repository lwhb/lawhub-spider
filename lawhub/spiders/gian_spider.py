"""
衆議院の議案一覧ページから各議案の内容（経過、本文）を取得し、$LAWHUB_DATA/gian以下に保存する

index.tsv: gian_idとメタデータの対応表
$category/$kaiji/$number以下に各議案の内容を保存する
"""

import logging
from urllib.parse import urljoin

import pandas as pd
import scrapy

from lawhub.items import HouanItem, KeikaItem, KeikaHtmlItem, HouanHtmlItem
from lawhub.settings import LAWHUB_DATA


class GianSpider(scrapy.Spider):
    name = "gian"
    start_urls = ['http://www.shugiin.go.jp/internet/itdb_gian.nsf/html/gian/menu.htm']
    directory = LAWHUB_DATA / 'gian'
    custom_settings = {
        'ITEM_PIPELINES': {'lawhub.pipelines.GianPipeline': 0}
    }

    def parse(self, response):
        records = []
        for table, category in zip(response.xpath('//table')[:3], ('syu', 'san', 'kaku')):
            for row in table.xpath('./tr')[1:]:  # skip header
                try:
                    record = {
                        'category': category,
                        'kaiji': int(row.xpath('./td[@headers="GIAN.KAIJI"]/span/text()').get()),
                        'number': int(row.xpath('./td[@headers="GIAN.NUMBER"]/span/text()').get()),
                        'keika': urljoin(response.url, row.xpath('./td[@headers="GIAN.KLINK"]//a/@href').get()),
                        'honbun': urljoin(response.url, row.xpath('./td[@headers="GIAN.HLINK"]//a/@href').get())
                    }
                    record['gian_id'] = '-'.join([record['category'], str(record['kaiji']), str(record['number'])])
                    record['directory'] = self.directory / record['category'] / str(record['kaiji']) / str(record['number'])
                except Exception as e:
                    self.log(f'failed to instantiate gian record from row:\n{row.get()}\n{e}', level=logging.ERROR)
                    continue
                records.append(record)

        self.directory.mkdir(parents=True, exist_ok=True)
        index_fp = self.directory / 'index.tsv'
        index_df = pd.DataFrame(records, columns=['gian_id', 'category', 'kaiji', 'number', 'keika', 'honbun', 'directory'])
        index_df.to_csv(index_fp, sep='\t', index=False)
        self.log(f'saved index in {index_fp}')

        for record in records:
            meta = {
                'gian_id': record['gian_id'],
                'directory': record['directory']
            }
            if record['keika']:
                yield response.follow(record['keika'], callback=self.parse_keika, meta=meta)
            if record['honbun']:
                yield response.follow(record['honbun'], callback=self.parse_honbun, meta=meta)

    def parse_keika(self, response):
        def build_keika_item(response):
            data = dict()
            for row in response.xpath('//table/tr')[1:]:  # skip header
                try:
                    td1, td2 = row.xpath('./td')
                    key = td1.xpath('.//text()').get()
                    val = td2.xpath('.//text()').get() or ''
                    data[key] = val
                except ValueError:
                    self.log(f'failed to parse key-value:\n{row.get()}')
            return KeikaItem(meta=response.meta, data=data)

        def build_keika_html_item(response):
            return KeikaHtmlItem(meta=response.meta, html=response.body)

        yield build_keika_item(response)
        yield build_keika_html_item(response)

    def parse_honbun(self, response):
        houan_link = None
        for a in response.xpath('//a'):
            text = a.xpath('./text()').get()
            if isinstance(text, str) and '提出時法律案' in text:
                houan_link = a.xpath('./@href').get()
                break
        if houan_link:
            yield response.follow(houan_link, callback=self.parse_houan, meta=response.meta)
        else:
            self.log(f'failed to parse HONBUN link from {response.url}', level=logging.WARNING)

    def parse_houan(self, response):
        def build_houan_item(response):
            item = HouanItem(meta=response.meta)

            item['title'] = ''.join(response.xpath('//div[@id="mainlayout"]/div[@class="WordSection1"]/p[3]//text()').getall()).strip()
            if item['title'] == '':
                self.log(f'failed to parse title from {response.url}', level=logging.ERROR)

            try:
                ps = response.xpath('//div[@id="mainlayout"]/p')
                if not ps:
                    ps = response.xpath('//div[@id="mainlayout"]/div[@class="WordSection1"]/p[position()>3]')
                content = [''.join(p.xpath('.//text()').getall()).strip() for p in ps]
                sub_idx = content.index('附　則')
                reason_idx = content.index('理　由')
                if sub_idx > reason_idx:
                    raise ValueError('REASON comes before HUSOKU')
                item['main'] = '\n'.join(content[:sub_idx])
                item['sub'] = '\n'.join(content[sub_idx + 1:reason_idx])
                item['reason'] = '\n'.join(content[reason_idx + 1:])
            except ValueError as e:
                self.log(f'failed to parse MAIN, HUSOKU, REASON from {response.url}: {e}', level=logging.ERROR)
            return item

        def build_houan_html_item(response):
            return HouanHtmlItem(meta=response.meta, html=response.body)

        yield build_houan_item(response)
        yield build_houan_html_item(response)
