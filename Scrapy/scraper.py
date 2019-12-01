from re import match
import urllib
from bs4 import BeautifulSoup
from hashlib import sha256
import os

class Hi():
    def __init__(self, url):
        self.url = url
        self.retry = []

    def start_requests(self):
        try:
            with urllib.request.urlopen(self.url) as response:
                html = response.read()

            base_url = form_url(self.url)
            print(base_url)
            links = []

            soup_tag = BeautifulSoup(html, 'lxml').find_all(extract_tags)
            for indx in range(len(soup_tag)):
                name = ''

                if soup_tag[indx].has_attr('href'):
                    name = put_name(soup_tag[indx]['href'])
                    links.append((os.path.join(base_url, soup_tag[indx]['href']), name))
                    soup_tag[indx]['href'] = name

                if soup_tag[indx].has_attr('src'):
                    name = put_name(soup_tag[indx]['src'])
                    links.append((os.path.join(base_url, soup_tag[indx]['src']), name))
                    soup_tag[indx]['src'] = name

            filename = sha256(response.url.encode('utf-8')).hexdigest()
            page = 'index.html'

            if not os.path.isdir(filename):
                os.mkdir(filename)

            with open(os.path.join(filename, page), 'wb') as f:
                f.write(html)

            for (tag_url, name_url) in links:
                try:
                    with urllib.request.urlopen(tag_url) as response:
                        html = response.read()

                    with open(os.path.join(filename, name_url), 'wb') as f:
                        f.write(html)
                except Exception as d:
                    print(d)

        except Exception as e:
            raise e

def extract_tags(tag):
    return (tag.has_attr('href') and (match(r'.*\.css$', tag['href']) or match(r'.*\.js$', tag['href']) or match(r'.*\.jpg$', tag['href']) or match(r'.*\.png$', tag['href']) or match(r'.*\.ico$', tag['href']))) or (tag.has_attr('src') and (match(r'.*\.css$', tag['src']) or match(r'.*\.js$', tag['src']) or match(r'.*\.jpg$', tag['src']) or match(r'.*\.png$', tag['src']) or match(r'.*\.ico$', tag['src'])))

def put_name(name):
    return '.'.join(name.split('/'))

def form_url(url):
    url = url.split('?')[0]
    split_url = url.split('/')

    temp = ''
    if split_url[0]=='file:':
        for idx in range(len(split_url)- 1):
            temp = os.path.join(temp, split_url[idx])
    else:
        for idx in range(3):
            temp = os.path.join(temp, split_url[idx])

    return temp
