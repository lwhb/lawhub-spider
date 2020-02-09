import json
from logging import getLogger
from pathlib import Path

from lawhub.items import HouanItem, KeikaItem, HouanHtmlItem, KeikaHtmlItem

logger = getLogger('pipelines')


class GianPipeline(object):
    def process_item(self, item, spider):
        def build_output_directory_path(meta):
            return Path('./data/{0}/{1}/{2}'.format(meta['category'], meta['kaiji'], meta['number']))

        directory = build_output_directory_path(item['meta'])
        directory.mkdir(parents=True, exist_ok=True)
        if isinstance(item, HouanItem):
            self.save_houan_item(item, directory / 'houan.json')
        elif isinstance(item, KeikaItem):
            self.save_keika_item(item, directory / 'keika.json')
        elif isinstance(item, HouanHtmlItem):
            self.save_html_item(item, directory / 'houan.html')
        elif isinstance(item, KeikaHtmlItem):
            self.save_html_item(item, directory / 'keika.html')

        # adhoc fix to ignore decoding error in scrapinghub
        if isinstance(item, HouanHtmlItem) or isinstance(item, KeikaHtmlItem):
            item['html'] = ''

        return item

    @staticmethod
    def save_houan_item(item, path):
        data = dict(item)
        if 'meta' in data:
            del data['meta']
        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        logger.debug(f'saved json in {path}')

    @staticmethod
    def save_keika_item(item, path):
        with open(path, 'w') as f:
            json.dump(item['data'], f, ensure_ascii=False)
        logger.debug(f'saved json in {path}')

    @staticmethod
    def save_html_item(item, path):
        with open(path, 'wb') as f:
            f.write(item['html'])
        logger.debug(f'saved {path}')
