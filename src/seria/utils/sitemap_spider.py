import scrapy

class SitemapSpider(scrapy.Spider):
    name = 'sitemap'
    
    # Enter your sitemap URL here
    start_urls = ['http://dfoarchive.blogspot.com/sitemap.xml']
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)
            
    