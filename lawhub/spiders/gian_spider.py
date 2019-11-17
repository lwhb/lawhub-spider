import json
import logging
from pathlib import Path

import scrapy


class GianSpider(scrapy.Spider):
    name = "gian"
    start_urls = [
        'http://www.shugiin.go.jp/internet/itdb_gian.nsf/html/gian/menu.htm'
    ]

    def parse(self, response):
        for table, category in zip(response.xpath('//table')[:3], ('syuhou', 'sanhou', 'kakuhou')):
            for row in table.xpath('./tr')[1:]:  # skip header
                meta = {'category': category}
                try:
                    meta['kaiji'] = int(row.xpath('./td[@headers="GIAN.KAIJI"]/span/text()').get())
                    meta['number'] = int(row.xpath('./td[@headers="GIAN.NUMBER"]/span/text()').get())
                except TypeError as e:
                    self.log(f'failed to parse KAIJI and NUMBER from row:\n{row.get()}', level=logging.ERROR)
                    continue

                keika_link = row.xpath('./td[@headers="GIAN.KLINK"]//a/@href').get()
                if keika_link:
                    yield response.follow(keika_link, callback=self.parse_keika, meta=meta)
                else:
                    self.log(f'failed to parse KEIKA link from row:\n{row.get()}', level=logging.WARNING)

                honbun_link = row.xpath('./td[@headers="GIAN.HLINK"]//a/@href').get()
                if honbun_link:
                    yield response.follow(honbun_link, callback=self.parse_honbun, meta=meta)
                else:
                    self.log(f'failed to parse HONBUN link from row:\n{row.get()}', level=logging.WARNING)

    def parse_keika(self, response):
        def build_json(response):
            data = dict()
            for row in response.xpath('//table/tr[position()>1]'):  # skip header
                try:
                    td1, td2 = row.xpath('td')
                    key = td1.xpath('.//text()').get()
                    val = td2.xpath('.//text()').get() or ''
                    data[key] = val
                except ValueError as e:
                    self.log(f'failed to parse key-value:\n{row.get()}')
            return data

        directory = Path('./data/{0}/{1}/{2}'.format(response.meta['category'], response.meta['kaiji'], response.meta['number']))
        directory.mkdir(parents=True, exist_ok=True)

        html_path = directory / 'keika.html'
        with open(html_path, 'wb') as f:
            f.write(response.body)
        self.log(f'saved {html_path}')

        json_path = directory / 'keika.json'
        with open(json_path, 'w') as f:
            json.dump(build_json(response), f, ensure_ascii=False)
        self.log(f'saved {json_path}')

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
        def build_json(response):
            data = dict()
            try:
                data['title'] = response.xpath('//div[@id="mainlayout"]/div[@class="WordSection1"]/p[3]/text()').get().strip()
            except AttributeError as e:
                self.log(f'failed to parse title from {response.url}: {e}', level=logging.ERROR)
            try:
                content = [text.strip() for text in response.xpath('//div[@id="mainlayout"]/p//text()').getall()]
                supple_idx = content.index('附　則')
                reason_idx = content.index('理　由')
                if supple_idx > reason_idx:
                    raise ValueError('REASON comes before HUSOKU')
                data['main'] = '\n'.join(content[:supple_idx])
                data['supple'] = '\n'.join(content[supple_idx + 1:reason_idx])
                data['reason'] = '\n'.join(content[reason_idx + 1:])
            except ValueError as e:
                self.log(f'failed to parse MAIN, HUSOKU, REASON from {response.url}: {e}', level=logging.ERROR)
            return data

        directory = Path('./data/{0}/{1}/{2}'.format(response.meta['category'], response.meta['kaiji'], response.meta['number']))
        directory.mkdir(parents=True, exist_ok=True)

        html_path = directory / 'houan.html'
        with open(html_path, 'wb') as f:
            f.write(response.body)
        self.log(f'saved {html_path}')

        json_path = directory / 'houan.json'
        with open(json_path, 'w') as f:
            json.dump(build_json(response), f, ensure_ascii=False)
        self.log(f'saved {json_path}')
