from scrapy import Request
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider, Rule
from scrapy.linkextractors import LinkExtractor
from hashlib import sha256
import os

from bs4 import BeautifulSoup
from re import match
from utils import put_name, extract_tags

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
        le_url = LinkExtractor(allow=(r'\.css$', r'\.js$', r'\.jpg$', r'\.png$', r'\.ico$'),
                           tags=('a', 'area', 'script', 'link', 'img' ),
                           attrs=('src', 'href'),
                           deny_extensions= ['html', 'asp', 'mng', 'pct', 'pst', 'psp', 'ai', 'drw', 'dxf', 'eps', 'ps', 'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff', '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv', 'm4a', 'm4v', 'flv', 'xls', 'xlsx', 'ppt', 'pptx', 'pps', 'doc', 'docx', 'odt', 'ods', 'odg', 'odp', 'pdf', 'exe', 'bin', 'rss', 'zip', 'rar']).extract_links(response)

        soup_tag = BeautifulSoup(response.body, 'lxml').find_all(extract_tags)

        filename = sha256(response.url.encode('utf-8')).hexdigest()
        page = 'index.html'

        if not os.path.isdir(filename):
            os.mkdir(filename)

        for indx in range(len(le_url)):
            name = ''

            if soup_tag[indx].has_attr('href'):
                name = put_name(soup_tag[indx]['href'])
                soup_tag[indx]['href'] = name

            if soup_tag[indx].has_attr('src'):
                name = put_name(soup_tag[indx]['src'])
                soup_tag[indx]['src'] = name

            yield response.follow(le_url[indx], callback=self.parse_urlink, errback=self.errback_httpbin, dont_filter=True, cb_kwargs={'home': filename, 'name': name})

        with open(os.path.join(filename, page), 'wb') as f:
            f.write(response.body)

    def parse_urlink(self, response, home, name):
        with open(os.path.join(home, name), 'wb') as f:
            f.write(response.body)

    def errback_httpbin(self, failure):
        self.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def closed(self, reason):
        print(reason)

#cr = CrawlerProcess()
#cr.crawl(WebSpider)
#cr.start()
