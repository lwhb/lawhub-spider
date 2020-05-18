import re

import pandas as pd
import scrapy


class EgovSpider(scrapy.Spider):
    name = "egov"

    start_urls = ['https://elaws.e-gov.go.jp/download/lawdownload.html']

    def parse(self, response):
        records = []
        table = response.xpath('//table[@id="sclTbl"]')[0]
        for row in table.xpath('./tbody/tr'):
            try:
                year = re.search(r'([0-9]{4})年', row.get()).group(1)
                zip = re.search(r'([0-9]+.zip)', row.get()).group(1)
                records.append({'year': year, 'zip': zip})
            except AttributeError:
                pass
        meta_df = pd.DataFrame(records, columns=['year', 'zip'])
        meta_fp = './data/egov/zip.meta'
        meta_df.to_csv(meta_fp, sep='\t', index=False)
        self.log(f'saved meta data to {meta_fp}')

        for zip_fp in meta_df['zip']:
            yield response.follow(f'/download/{zip_fp}', callback=self.save_zip)

    def save_zip(self, response):
        zip_fp = response.request.url.split("/")[-1]
        with open(f'./data/egov/{zip_fp}', 'wb') as f:
            f.write(response.body)
