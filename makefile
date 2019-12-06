.PHONY = install

all = install

install:
			@pip install beautifulsoup4==4.6.0
			@pip install lxml==4.4.1
			@pip install rpyc==4.1.2
			@pip install urllib3==1.22
