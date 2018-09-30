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
            header = item.css('h3.lister-item-header')
            content = item.css('div.lister-item-content')

            votes_and_gross = (content.css('span[name="nv"]::attr(data-value)')
                                      .extract())
            votes = votes_and_gross[0] if votes_and_gross else None
            gross = votes_and_gross[1] if len(votes_and_gross) > 1 else None

            # TODO add field on whether the person is the director or an actor
            cast = []
            for person in content.css('p')[2].css('a'):
                cast.append({'name': person.css('::text').extract_first(),
                             'link': person.css('::attr(href)')
                                           .extract_first()})

            genre = content.css('span.genre::text').extract_first()
            if genre is not None:
                genre = genre.strip()

            link = header.css('a::attr(href)').extract_first()

            yield {
                'imdb_id': header.css('a::attr(href)')
                                 .re('/title/(tt\d+)/.*')[0],
                'source': 'list',
                'link': link,
                'title': header.css('a::text').extract_first(),
                'image': item.css('div.lister-item-image img::attr(src)')
                             .extract_first(),
                'year': header.css('span.lister-item-year::text')
                              .extract_first(),
                'certificate': content.css('span.certificate::text')
                                      .extract_first(),
                'runtime': content.css('span.runtime::text').extract_first(),
                'genre': genre,
                'rating': item.css('div.ratings-bar')
                              .css('div[name="ir"]::attr(data-value)')
                              .extract_first(),
                'summary': content.css('p.text-muted')[1] .css('::text')
                              .extract_first().strip(),
                'votes': votes,
                'gross': gross[0] if gross else None,
                'cast': cast,
            }
            yield response.follow(link, self.parse_movie)

        next_page = (response.css('div.desc a.lister-page-next::attr(href)')
                             .extract_first())
        if next_page is not None:
            yield response.follow(next_page, self.parse_list)

    def _detail(self, selector, name, tag='a', multi=False, seemore=False):
        """
        Extract a detail from the movies list of details.

        For example, it can extract the value from `Name: value`.

        Parameters
        ----------
        selector : scrapy.Selector
            The selector for the block where to extract from.
        name : str
            The name of the element (the text in the h4 section).
            For example in `Country: India` would be `Country:`
        tag : str, default 'a'
            The tag where the text to extract is found. By default is an 'a'
            tag, as most values are in links. If the text is not a link, the
            empty string can be used ''.
        multi : bool, default False
            Whether a list with multiple elements is expected as a return.
        seemore : bool, default False
            Wheter the last link should be understood as a "See more" link.
        """
        for h4 in selector.css('h4'):
            if h4.css('::text').extract_first().strip() == name:
                item = h4.xpath('../{}/text()'.format(tag))

                if multi:
                    values = [v.strip() for v in item.extract()]
                    if seemore:
                        values = values[:-1]
                    return values
                else:
                    return ''.join(item.extract()).strip()

    def _cast(self, selector):
        for row in selector.css('table.cast_list tr'):
            cols = row.css('td')
            if len(cols) > 1:
                col = cols[1].css('a')
                link = col.css('::attr(href)').extract_first()
                yield {'imdb_id': link.split('/')[2],
                       'name': col.css('::text').extract_first().strip(),
                       'link': link}

    def parse_movie(self, response):
        storyline = response.css('#titleStoryLine')
        details = response.css('#titleDetails')
        cast = list(self._cast(response.css('#titleCast')))
        rating = response.css('div.imdbRating')

        storyline_text = (storyline.css('div')[0]
                                   .css('p span::text').extract_first())
        if storyline_text:
            storyline_text = storyline_text.strip()

        rate = num_ratings = None
        if rating:
            rate = rating[0].css('strong span::text').extract_first()
            num_ratings = rating[0].css('a span::text').extract_first()

        yield {
            'imdb_id': response.url.split('/')[4],
            'source': 'movie',
            'storyline': storyline_text,
            'plot_keywords': self._detail(storyline, 'Plot Keywords:',
                                          'a/span', multi=True),
            'certificate': self._detail(storyline, 'Certificate:', 'span'),
            'genres': self._detail(storyline, 'Genres:', multi=True),
            'country': self._detail(details, 'Country:', multi=True),
            'language': self._detail(details, 'Language:', multi=True),
            'release_date': self._detail(details, 'Release Date:', '.'),
            'production_co': self._detail(details, 'Production Co:',
                                          multi=True, seemore=True),
            'runtime': self._detail(details, 'Runtime:', 'time'),
            'color': self._detail(details, 'Color:'),
            'cast': cast,
            'rate': rate,
            'num_ratings': num_ratings,
            'photo': response.css('div.poster a img::attr(src)')
                             .extract_first(),
        }
        for person in cast:
            yield response.follow(person['link'], self.parse_person)

    def parse_person(self, response):
        overview = response.css('#overview-top')

        birth_date = birth_place = None
        born_info = response.css('#name-born-info')
        if born_info:
            birth_date = born_info.css('time::attr(datetime)').extract_first()
            birth_place = born_info.css('a::text').extract()[-1]

        awards = response.css('#maindetails_center_bottom span.awards-blurb::text')
        if awards:
            awards = awards.extract_first().strip()

        height = self._detail(response.css('#details-height'), 'Height:', '.')
        if height:
            height = height.replace('\xa0', ' ')

        bio_link = (response.css('#name-bio-text span.see-more a::attr(href)')
                            .extract_first())

        yield {
            'imdb_id': response.url.split('/')[4],
            'source': 'person',
            'name': overview.css('h1 span::text').extract_first(),
            'jobs': [v.strip() for v in
                     response.css('#name-job-categories a span::text')
                             .extract()],
            'bio': response.css('#name-bio-text div.inline::text')
                           .extract_first().strip(),
            'bio_link': bio_link,
            'awards': awards,
            'height': height,
            'birth_date': birth_date,
            'birth_place': birth_place,
            'photo': response.css('#name-poster::attr(src)').extract_first(),
        }

        if bio_link:
            yield response.follow(bio_link, self.parse_bio)

    def parse_bio(self, response):
        # TODO get overview data
        # TODO get structured content of spouses and salary
        section = None
        for item in response.css('#bio_content > *'):
            texts = []
            tag = item.re_first('^<(\w+) ')
            if tag == 'h4':
                section = item.css('::text').re_first('(.*) \(\d+\)')
                continue
            if not section or section == 'Overview':
                continue

            class_ = item.css('::attr(class)').extract_first()
            if tag == 'div' and class_.startswith('soda'):
                text = ' '.join(item.css('*::text').extract())
                if text:
                    texts = [text]

            if tag == 'table':
                for row in item.css('tr'):
                    text = ' '.join(row.css('*::text').extract())
                    if text:
                        texts.append(text)

            for text in texts:
                yield {
                    'imdb_id': response.url.split('/')[4],
                    'source': 'bio',
                    'section': section,
                    'text': ' '.join(text.split()) if text else None,
                }
