```
scrapy crawl gian --loglevel DEBUG &> $LAWHUB_DATA/log/crawl_gian.log
scrapy crawl egov --loglevel DEBUG &> $LAWHUB_DATA/log/crawl_egov.log
scrapy crawl giin --loglevel DEBUG -o $LAWHUB_DATA/giin/giin.json
```
