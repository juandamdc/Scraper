from concurrent.futures import ThreadPoolExecutor
import rpyc
import os
import time
from hashlib import sha256

class Client(rpyc.Service):

    def start(self):
        self.urls = []

        print('URLs iniciales (presione ENTER para terminar):')

        while(True):
            url = input()
            if url == '':
                if len(self.urls) == 0:
                    print("Debe escribir alguna url")
                    print()
                    print()
                    print('URLs iniciales (presione ENTER para terminar):')
                    continue
                else:
                    break

            self.urls.append(url)

    def connect(self, ip, port):
        with ThreadPoolExecutor(max_workers=3) as tpe:
            for url in self.urls:
                tpe.submit(lambda p: start_download(*p), [url, ip, port])
            # download(url, ip, port)

def start_download(url, ip, port):
    with rpyc.connect(ip, port) as cnn:
        hash_url = int(sha256(url.encode()).hexdigest(), 16)%2**(160)

        wait = 0
        while wait != 3:
            try:
                _, ip_ask, port_ask = cnn.root.find_successor(hash_url)
                download(url, ip_ask, port_ask)
                break
            except Exception:
                time.sleep(2**wait)
                wait  = wait + 1

def download(url, ip, port):
    with rpyc.connect(ip, port) as cnn:
        print(f'INFO: {url} as {sha256(url.encode()).hexdigest()}')
        print(f'INFO: ask {url} to ({ip}, {port})')

        for page_html in cnn.root.download(url):
            dir = os.path.join('downloads', page_html[0])

            if not os.path.isdir(dir):
                os.makedirs(dir)

            with open(os.path.join(dir,page_html[1]), 'wb') as f:
                f.write(page_html[2])

            if page_html==(0,0,0):
                print(f'INFO: error in url {url}')
            elif page_html[1] == 'index.html':
                print(f'INFO: iniciando descarga {url}')

    print(f'INFO: finalizando descarga {url}')
    print()
