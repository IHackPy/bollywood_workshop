import scrapy


class Movie(scrapy.Item):
    imdb_code = scrapy.Field()
    title = scrapy.Field()
    year = scrapy.Field()
