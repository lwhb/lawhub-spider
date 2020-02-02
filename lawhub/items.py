import scrapy


class BaseItem(scrapy.Item):
    meta = scrapy.Field()

    def __repr__(self):
        id_ = '-'.join(map(str, [self['meta']['category'], self['meta']['kaiji'], self['meta']['number']]))
        return f'<{self.__class__.__name__} {id_}>'


class HouanItem(BaseItem):
    title = scrapy.Field()
    main = scrapy.Field()
    sub = scrapy.Field()
    reason = scrapy.Field()


class KeikaItem(BaseItem):
    data = scrapy.Field()


class HouanHtmlItem(BaseItem):
    html = scrapy.Field()


class KeikaHtmlItem(BaseItem):
    html = scrapy.Field()
