from scrapy import FormRequest, Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class Yellow(CrawlSpider):
    start_urls = ['https://yellowpages.com']
    rules = [Rule(LinkExtractor(allow='yellowpages.com'), follow=True)]
    name = 'gr33n'
    counter = 0

    def __init__(self, search_keywords, country, town, state, num_of_leads, sort_by='default'):
        self.search_keywords = search_keywords
        self.country = country
        self.town = town
        self.state = state
        self.num_of_leads = num_of_leads
        self.sort_by = sort_by

    def parse(self, response):
        formdata = {'search_terms': self.search_keywords,
                    'geo_location_terms': '{}, {}, {}'.format(self.country,
                                                              self.town,
                                                              self.state)}
        yield FormRequest.from_response(
            response,
            formid='search-form',
            formdata=formdata,
            callback=self.get_response
        )

    def get_response(self, response):
        if self.sort_by == 'default' or self.sort_by in response.url:
            if self.num_of_leads < self.counter:
                test = response.css('#content-container>#content>div>div>.scrollable-pane>.search-results'
                                    '>div>div>div>.info>h2')
                for a in test:
                    link = a.css('a::attr(href)').extract()[0]
                    yield Request(url='https://www.yellowpages.com' + link, callback=self.get_data, priority=1)

                # TODO: Pagination, if for some reason this won't work. Get the query param from the url
                # TODO: And append it to the response.url
                # try:
                    # pagination = response.css('.container>div>.scrollable-pane>.pagination>ul>li:last-child():attr(href)').extract()[0]
		#	yield Request(url='https://www.yellowpages.com' + pagination, callback=self.get_response)
                # except IndexError:
                #   pass

        else:
            yield Request(url=response.url + '&s=' + self.sort_by, callback=self.get_response)

    def get_data(self, response):
        self.counter += 1
        start = response.css('#content-container>#bpp>header')
        for i in start:
            lead = {'title': i.css('article>.sales-info>h1::text').extract_first(),
                    'address': i.css('article>.primary-info>.contact>h2::text').extract_first(),
                    'phone': i.css('article>.primary-info>.contact>.phone::text').extract_first(),
                    'time': i.css('article>.primary-info>.contact>.time-info>div:nth-child(2)::text').extract_first(),
                    'website': i.css('.business-card-footer>.website-link::attr(href)').extract_first(),
                    'email': i.css('.business-card-footer>.email-business::attr(href)').extract_first(),
                    'portfolio_item': ''}
            if lead['email'] is not None:
                lead['email'] = lead['email'].split(':')[-1]
            if lead['email'] and lead['website'] is not None:
                yield lead

