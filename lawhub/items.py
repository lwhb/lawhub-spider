import scrapy


class BaseItem(scrapy.Item):
    meta = scrapy.Field()

    def __repr__(self):
        return f'<{self.__class__.__name__} {self["meta"]["gian_id"]}>'


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
