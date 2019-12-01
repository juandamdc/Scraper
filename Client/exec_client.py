import client

cnn = client.Client()
cnn.start('127.0.0.1', 8079)
cnn.connect('127.0.0.1', 8000)
