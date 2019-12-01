import rpyc
import os

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

        if not os.path.isdir('downloads'):
            os.mkdir('downloads')

    def connect(self, ip, port):
        with rpyc.connect(ip, port) as cnn:
            cnn.root.receive_urls(self.urls, self.ip, self.port)    

        