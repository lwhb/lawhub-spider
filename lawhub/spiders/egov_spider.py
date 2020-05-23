"""
EGovの法令データ一括ダウンロードページから交付年ごとに圧縮されたZipファイルを取得し、$LAWHUB_DATA/egov以下に保存する

zip.meta: 交付年とzipファイル名の対応表
[0-9]+.zip: 交付年ごとのzipファイル
"""

import re
import shutil

import pandas as pd
import scrapy

from lawhub.settings import LAWHUB_DATA


class EgovSpider(scrapy.Spider):
    name = "egov"
    start_urls = ['https://elaws.e-gov.go.jp/download/lawdownload.html']
    directory = LAWHUB_DATA / 'egov'

    def parse(self, response):
        records = []
        table = response.xpath('//table[@id="sclTbl"]')[0]
        for row in table.xpath('./tbody/tr'):
            try:
                yid = re.search(r'(?:明治|大正|昭和|平成|令和)[0-9元]+年', row.get()).group()
                zid = re.search(r'([0-9]+).zip', row.get()).group(1)
                records.append({'yid': yid, 'zid': zid})
            except AttributeError:
                pass
        meta_df = pd.DataFrame(records, columns=['yid', 'zid'])

        # clean directory
        if self.directory.exists():
            shutil.rmtree(self.directory)
        self.directory.mkdir(parents=True)

        meta_fp = self.directory / 'zip.meta'
        meta_df.to_csv(meta_fp, sep='\t', index=False)
        self.log(f'saved meta data to {meta_fp}')

        for zid in meta_df['zid']:
            yield response.follow(f'/download/{zid}.zip', callback=self.save_zip)

    def save_zip(self, response):
        fp = self.directory / response.request.url.split("/")[-1]
        with open(fp, 'wb') as f:
            f.write(response.body)
