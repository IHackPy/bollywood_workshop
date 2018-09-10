import urllib.parse
import scrapy


BASE_URL = 'https://www.imdb.com'


class ImdbSpider(scrapy.Spider):
    name = 'imdb'
    allowed_domains = ['imdb.com']

    def start_requests(self):
        params = {'title_type': 'feature',
                  'release_date': '1970-01-01,',
                  'countries': 'in',
                  'languages': 'hi',
                  'page': 1}
        url = '{}/search/title?{}'.format(BASE_URL,
                                          urllib.parse.urlencode(params))
        yield scrapy.Request(url, callback=self.parse_list)

    def parse_list(self, response):
        """
        Extract information from the list of movies.

        With the current selection of India / Hindi, there are 197 page, with
        50 movies in each, for a total of 9,852 movies.
        """
        for item in response.css('div.lister-item'):
            votes_and_gross = item.css('div.lister-item-content span[name="nv"]::attr(data-value)').extract()  # noqa: E501
            votes = votes_and_gross[0] if votes_and_gross else None
            gross = votes_and_gross[1] if len(votes_and_gross) > 1 else None

            # TODO add field on whether the person is the director or an actor
            cast_selector = item.css('div.lister-item-content p')[2].css('a')
            cast = []
            for person in cast_selector:
                cast.append({'name': person.css('::text').extract_first(),
                             'link': person.css('::attr(href)').extract_first()})  # noqa: E501

            genre = item.css('div.lister-item-content span.genre::text').extract_first()  # noqa: E501
            if genre is not None:
                genre = genre.strip()

            # TODO get partial selectors to make the next code simpler/shorter:
            # >>> item_header = item.css('h3.lister-item-header')
            # >>> link = item_header.css('a::attr(href)').extract_first()
            yield {
                'imdb_id': item.css('h3.lister-item-header a::attr(href)').re('/title/(tt\d+)/.*')[0],  # noqa: E501
                'link': item.css('h3.lister-item-header a::attr(href)').extract_first(),  # noqa: E501
                'title': item.css('h3.lister-item-header a::text').extract_first(),  # noqa: E501
                'image': item.css('div.lister-item-image img::attr(src)').extract_first(),  # noqa: E501
                'year': item.css('h3.lister-item-header span.lister-item-year::text').extract_first(),  # noqa: E501
                'certificate': item.css('div.lister-item-content span.certificate::text').extract_first(),  # noqa: E501
                'runtime': item.css('div.lister-item-content span.runtime::text').extract_first(),  # noqa: E501
                'genre': genre,
                'rating': item.css('div.ratings-bar div[name="ir"]::attr(data-value)').extract_first(),  # noqa: E501
                'summary': item.css('div.lister-item-content p.text-muted')[1].css('::text').extract_first().strip(),  # noqa: E501
                'votes': votes,
                'gross': gross[0] if gross else None,
                'cast': cast,
            }
        next_page = response.css('div.desc a.lister-page-next::attr(href)').extract_first()  # noqa: E501
        if next_page is not None:
            yield response.follow(next_page, self.parse_list)

    def parse_movie(self, response):
        pass
