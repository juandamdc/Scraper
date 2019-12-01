from re import match 

def put_name(name):
    return '.'.join(name.split('/'))

def extract_tags(tag):
    return (tag.has_attr('href') and (match(r'.*\.css$', tag['href']) or match(r'.*\.js$', tag['href']) or match(r'.*\.jpg$', tag['href']) or match(r'.*\.png$', tag['href']) or match(r'.*\.ico$', tag['href']))) or (tag.has_attr('src') and (match(r'.*\.css$', tag['src']) or match(r'.*\.js$', tag['src']) or match(r'.*\.jpg$', tag['src']) or match(r'.*\.png$', tag['src']) or match(r'.*\.ico$', tag['src'])))
