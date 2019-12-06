import sys
import client

cnn = client.Client()
cnn.start()
cnn.connect(sys.argv[1], int(sys.argv[2]))
