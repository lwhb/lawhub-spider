import scrapy


class HouanItem(scrapy.Item):
    meta = scrapy.Field()
    title = scrapy.Field()
    main = scrapy.Field()
    sub = scrapy.Field()
    reason = scrapy.Field()


class KeikaItem(scrapy.Item):
    meta = scrapy.Field()
    data = scrapy.Field()


class HouanHtmlItem(scrapy.Item):
    meta = scrapy.Field()
    html = scrapy.Field()


class KeikaHtmlItem(scrapy.Item):
    meta = scrapy.Field()
    html = scrapy.Field()
