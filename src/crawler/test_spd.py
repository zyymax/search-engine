from urllib2 import urlopen
from lxml import etree
from StringIO import StringIO
import urlparse
import sys

cur_url = 'http://www.36kr.com/p/211993.html'
cur_url = 'http://www.36kr.com/p/212326.html?ref=related'
cur_url = sys.argv[1]
data = urlopen(cur_url).read()
article = {}

if __name__=="__main__":
    def test():
        try:
            tree = etree.parse(
                StringIO(data),
                etree.HTMLParser(
                    encoding='utf-8'))
            idx1 = cur_url.index('p/')
            idx2 = cur_url.rindex('.htm')
            article['id'] = cur_url[idx1+2:idx2]
            article['url'] = cur_url
            title_elem = tree.xpath(
                '//*[@id="article"]/div[1]/div[1]/div[1]/div/article/section[1]/header/h1')[0]
            title = ''
            for text in title_elem.itertext():
                title += text
            article['title'] = title
            author_info = tree.xpath(
                '//*[@id="article"]/div[1]/div[1]/div[1]/div/article/section[1]/header/div/a')[0]
            article['author'] = author_info.text
            article['author_url'] = urlparse.urljoin(
                cur_url,
                author_info.get('href'))
            print article
        except Exception as e:
            print 'error to parse html:', e
            return False
    test()
