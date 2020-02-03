import logging

import scrapy

from lawhub.items import HouanItem, KeikaItem, KeikaHtmlItem, HouanHtmlItem


class GianSpider(scrapy.Spider):
    name = "gian"
    start_urls = [
        'http://www.shugiin.go.jp/internet/itdb_gian.nsf/html/gian/menu.htm'
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'lawhub.pipelines.GianPipeline': 0}
    }

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
        def build_keika_item(response):
            data = dict()
            for row in response.xpath('//table/tr')[1:]:  # skip header
                try:
                    td1, td2 = row.xpath('./td')
                    key = td1.xpath('.//text()').get()
                    val = td2.xpath('.//text()').get() or ''
                    data[key] = val
                except ValueError as e:
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
            try:
                item['title'] = response.xpath('//div[@id="mainlayout"]/div[@class="WordSection1"]/p[3]//text()').get().strip()
            except AttributeError as e:
                self.log(f'failed to parse title from {response.url}: {e}', level=logging.ERROR)
            try:
                content = [text.strip() for text in response.xpath('//div[@id="mainlayout"]/p//text()').getall()]
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
