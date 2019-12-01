from scrapy import Request
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider, Rule
from scrapy.linkextractors import LinkExtractor
from hashlib import sha256
import os
import re

class WebSpider(Spider):

    def __init__(self):
        self.name = "hi"
        self.urls = ['file:///media/hi/New%20Volume/univ/00.websites!!/W3Schools/W3Schools/index.html']
        #self.urls = ['http://quotes.toscrape.com/page/1/', 'http://quotes.toscrape.com/page/2/']
        #self.urls = ['https://www.w3schools.com/']

    def start_requests(self):
        for url in self.urls:
            yield Request(url=url, callback=self.parse_url, errback=self.errback_httpbin)

    def parse_url(self, response):
        filename = sha256(response.url.encode('utf-8')).hexdigest()
        page = '-'.join(response.url.split('/')[2:])

        if not os.path.isdir(filename):
            os.mkdir(filename)

        with open(os.path.join(filename, page), 'wb') as f:
            f.write(response.body)

        le = LinkExtractor(allow=(r'\.css$', r'\.js$', r'\.jpg$', r'\.png$', r'\.ico$'),
                           tags=('a', 'area', 'script', 'link', 'img' ),
                           attrs=('src', 'href'),
                           deny_extensions= ['html', 'asp', 'mng', 'pct', 'pst', 'psp', 'ai', 'drw', 'dxf', 'eps', 'ps', 'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff', '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv', 'm4a', 'm4v', 'flv', 'xls', 'xlsx', 'ppt', 'pptx', 'pps', 'doc', 'docx', 'odt', 'ods', 'odg', 'odp', 'pdf', 'exe', 'bin', 'rss', 'zip', 'rar']).extract_links(response)

        for link in le:
            yield response.follow(link, callback=self.parse_urlink, errback=self.errback_httpbin, dont_filter=True, cb_kwargs={'home':filename, 'url_mother':response.url} )

    def parse_urlink(self, response, home, url_mother):
        page = '-'.join(response.url.split('/')[2:])

        with open(os.path.join(home, page), 'wb') as f:
            f.write(response.body)

    def errback_httpbin(self, failure):
        self.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

cr = CrawlerProcess()
cr.crawl(WebSpider)
cr.start()
