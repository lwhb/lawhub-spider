import scrapy


class GiinSpider(scrapy.Spider):
    name = "giin"
    start_urls = [
        'http://www.shugiin.go.jp/Internet/itdb_annai.nsf/html/statics/syu/1giin.htm',
        'http://www.shugiin.go.jp/Internet/itdb_annai.nsf/html/statics/syu/2giin.htm',
        'http://www.shugiin.go.jp/Internet/itdb_annai.nsf/html/statics/syu/3giin.htm',
        'http://www.shugiin.go.jp/Internet/itdb_annai.nsf/html/statics/syu/4giin.htm',
        'http://www.shugiin.go.jp/Internet/itdb_annai.nsf/html/statics/syu/5giin.htm',
        'http://www.shugiin.go.jp/Internet/itdb_annai.nsf/html/statics/syu/6giin.htm',
        'http://www.shugiin.go.jp/Internet/itdb_annai.nsf/html/statics/syu/7giin.htm',
        'http://www.shugiin.go.jp/Internet/itdb_annai.nsf/html/statics/syu/8giin.htm',
        'http://www.shugiin.go.jp/Internet/itdb_annai.nsf/html/statics/syu/9giin.htm',
        'http://www.shugiin.go.jp/Internet/itdb_annai.nsf/html/statics/syu/10giin.htm',
    ]

    def parse(self, response):
        table = response.xpath('//table//table')
        for row in table.xpath('./tr')[1:]:  # skip header
            tds = row.xpath('./td')
            yield {
                'url': response.urljoin(tds[0].xpath('.//a/@href').get()),
                'name_kan': tds[0].xpath('.//a/text()').get().strip()[:-1].split(),
                'name_hira': tds[1].xpath('.//text()').get().strip().split(),
                'party': tds[2].xpath('.//text()').get().strip(),
                'zone': tds[3].xpath('.//text()').get().strip(),
                'num_elected': tds[4].xpath('.//text()').get().strip()
            }
