import scrapy


class ImdbSpider(scrapy.Spider):
    name = 'imdb'
    allowed_domains = ['imdb.com']

    def start_requests(self):
        # 197
        for page in range(1, 197):
            yield scrapy.Request('https://www.imdb.com/search/title?title_type=feature&release_date=1970-01-01,&countries=in&languages=hi&page={}'.format(page),
                                 callback=self.parse_list)

    def parse_list(self, response):
        for item in response.css('h3.lister-item-header'):
            text = item.css('a::text').extract_first()
            link = item.css('a::attr(href)').extract_first()
            id_ = item.css('a::attr(href)').re('/title/(tt\d+)/.*')[0]
            yield {'title': text,
                   'id': id_}
            #yield response.follow(link, self.parse_movie)

    def parse_movie(self, response):
        pass
