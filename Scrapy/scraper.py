from re import match
import urllib
from bs4 import BeautifulSoup
from hashlib import sha256
import os
import time

class Scraper():
    def __init__(self, url):
        self.url = url

    def start_requests(self):
        wait = 0
        while True:
            try:
                print(f'INFO: GET {self.url}')
                with urllib.request.urlopen(self.url) as response:
                    html = response.read()

                break

            except Exception:
                print(f'ERROR: an error ocurred when try to get {self.url}')

                if wait == 2:
                    print(f'ERROR: download failed: {self.url}')
                    return [(0,0,0)]

                print(f'INFO: trying again in {2**wait} seconds')
                time.sleep(2**wait)
                wait = wait + 1


        base_url = form_url(self.url)
        links = []

        soup = BeautifulSoup(html, 'lxml')
        soup_tag = soup.find_all(extract_tags)

        for indx in range(len(soup_tag)):
            if soup_tag[indx].has_attr('href'):
                name = put_name(soup_tag[indx]['href'])
                links.append((urllib.parse.urljoin(base_url, soup_tag[indx]['href']), name))
                soup_tag[indx]['href'] = name

            if soup_tag[indx].has_attr('src'):
                name = put_name(soup_tag[indx]['src'])
                links.append((urllib.parse.urljoin(base_url, soup_tag[indx]['src']), name))
                soup_tag[indx]['src'] = name

        filename = sha256(self.url.encode('utf-8')).hexdigest()
        dir = os.path.join('downloads', filename)
        page = 'index.html'

        if not os.path.isdir(dir):
            os.makedirs(dir)

        with open(os.path.join(dir, page), 'wb') as f:
            f.write(soup.prettify(formatter='html').encode('utf-8'))

        yield filename, page, soup.prettify(formatter='html').encode('utf-8')

        for (tag_url, name_url) in links:

            scheme, netloc, path, query, fragment = urllib.parse.urlsplit(tag_url)
            path = urllib.parse.quote(path)
            link = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))

            wait = 0
            while True:
                try:
                    print(f'INFO: GET {link}')
                    with urllib.request.urlopen(link) as response:
                        html = response.read()

                    break

                except Exception:
                    print(f'ERROR: an error ocurred when try to get {link}')

                    if wait == 2:
                        print(f'ERROR: download failed: {link}')
                        break

                    print(f'INFO: trying again in {2**wait} seconds')
                    time.sleep(2**wait)
                    wait = wait + 1

            with open(os.path.join(dir, name_url), 'wb') as f:
                f.write(html)

            yield filename, name_url, html

def extract_tags(tag):
    return (tag.has_attr('href') and (match(r'.*\.php', tag['href']) or match(r'.*\.css', tag['href']) or match(r'.*\.js', tag['href']) or match(r'.*\.jpg', tag['href']) or match(r'.*\.png', tag['href']) or match(r'.*\.ico', tag['href']))) or (tag.has_attr('src') and (match(r'.*\.php', tag['src']) or match(r'.*\.css', tag['src']) or match(r'.*\.js', tag['src']) or match(r'.*\.jpg', tag['src']) or match(r'.*\.png', tag['src']) or match(r'.*\.ico', tag['src'])))

def put_name(name):
    split_name = name.replace('?', '').replace('=', '').split('/')
    split_name = split_name[max(0, len(split_name) - 4):]
    return '-'.join(split_name)

def form_url(url):
    # url = url.split('?')[0]
    split_url = url.split('/')

    if split_url[0]=='file:':
        return '/'.join(split_url[0:-1])
    else:
        return '/'.join(split_url[0:3])
