import rpyc
import os
from hashlib import sha256

class Client(rpyc.Service):

    def start(self, ip, port):
        self.ip = ip
        self.port = port
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
        for url in self.urls:
            with rpyc.connect(ip, port) as cnn:
                hash_url = int(sha256(url.encode()).hexdigest(), 16)%2**(160)
                _, ip_ask, port_ask = cnn.root.find_successor(hash_url)

            with rpyc.connect(ip_ask, port_ask) as cnn:
                try:
                    for page_html in cnn.root.download(url):

                        dir = os.path.join('downloads', page_html[0])
                        if not os.path.isdir(dir):
                            os.makedirs(dir)

                        with open(os.path.join(dir,page_html[1]), 'wb') as f:
                            f.write(page_html[2])

                except Exception:
                    pass
