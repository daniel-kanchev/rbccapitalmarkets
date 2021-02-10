import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from rbccapitalmarkets.items import Article


class RbcSpider(scrapy.Spider):
    name = 'rbc'
    start_urls = ['https://www.rbccm.com/en/insights.page']

    def parse(self, response):
        links = response.xpath('//div[@class="news-listing"]/div/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get().strip()
        date = response.xpath('//div[@class="news-date"]/text()[last()]').get()
        if date:
            date = " ".join(date.strip().split()[1:-1])
        date = datetime.strptime(date, '%B %d, %Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//div[@class="article-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()
        author = response.xpath('//span[@class="title"]/text()').getall()
        if author:
            author = ", ".join(author)

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('author', author)

        return item.load_item()
