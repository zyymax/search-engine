import os
import re
import urlparse
from lxml import etree
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup
from items import Topic, Article
from util.spider import BaseSpiderV3


class Base36krSpider(BaseSpiderV3):

    """
            Base spider for crawling 36kr.com
    """

    def parse_artical(self, cur_url, data):
        # save data
        pathname = self._saveweb(cur_url, data)
        if pathname is None:
            print 'error to save %s...' % cur_url
            # error to save
            return False
        print '[Article]\tDoc.%s\t saved from %s' \
            % (len(self._item_list)+1, cur_url)
        # parse data
        article = Article()
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
            article['path'] = os.path.abspath(pathname)
            article['tag_list'] = ''
            article['cat_url'] = ''
            article['category'] = ''
            self._item_list.append(article)
            self._kept_list.append(article['url'])
        except Exception as e:
            print 'error to parse html:', e
            return False
        return True

    def parse_topic(self, cur_url, data):
        """
                used to parse topic page in 36kr.com
        """
        nexturl_dict = {}
        # parse html
        try:
            soup = BeautifulSoup(data, fromEncoding='utf-8')
        except Exception as e:
            print 'open soup error', e
            return nexturl_dict
        for tag in soup.find('table', attrs={'class': 'table'}).findAll('a'):
            if 'href' not in tag:
                continue
            next_url = urlparse.urljoin(cur_url, tag['href'])
            # check next_url
            if next_url in self._url_dict:
                continue
            nexturl_dict[next_url] = 1
        if not re.search('\?page=', cur_url):
            # try to build page_url_list
            pagination = soup.find('div', attrs={'class': 'pagination'})
            if pagination is not None:
                # has page toolbar
                li_list = pagination.findAll('li')
                try:
                    max_num = int(li_list[-2].a.text)
                    for pageno in xrange(2, max_num+1):
                        nexturl = urlparse.urljoin(
                            cur_url,
                            '?page=%s' %
                            pageno)
                        # print cur_url, nexturl
                        nexturl_dict[nexturl] = 1
                except Exception as e:
                    print 'error to get max pageno', e
        return nexturl_dict


class Gen36krSpider(Base36krSpider):

    """
            general 36kr spider of Base36krSpider
    """

    def parse_nexturl_list(self, cur_url, data):
        nexturl_dict = {}
        if re.compile('p/\d+\.html?').search(cur_url):
            cur_url = cur_url.split('?')[0].split('#')[0]
            # got artical page
            if self.parse_artical(cur_url, data):
                nexturl_dict[cur_url] = 1
            return nexturl_dict
        try:
            soup = BeautifulSoup(data, fromEncoding='utf-8')
        except Exception as e:
            print 'open soup error', e
            return nexturl_dict
        # add real_url to already crawled url list
        for tag in soup.findAll('a'):
            if not tag.has_key('href'):
                continue
            next_url = urlparse.urljoin(
                cur_url,
                tag['href'].encode('utf-8'))  # .rstrip()
            # check next_url
            if self.bad_domain(next_url) or next_url in self._url_dict:
                continue
            nexturl_dict[next_url] = 1
        return nexturl_dict


class Topic36krSpider(Base36krSpider):

    """
            topic 36kr spider of Base36krSpider
    """

    def parse_nexturl_list(self, cur_url, data):
        nexturl_dict = {}
        try:
            soup = BeautifulSoup(data, fromEncoding='utf-8')
        except Exception as e:
            print 'open soup error', e
            return nexturl_dict
        # add real_url to already crawled url list
        for div in soup.findAll('div',attrs={'class':'category-topic__title cf'}):
            topic = Topic()
            topic['name'] = div.contents[1].span.text
            next_url = urlparse.urljoin(
                cur_url,
                div.contents[3].a['href'].encode('utf-8'))
            topic['url'] = next_url
            # check next_url
            self._item_list.append(topic)
            self._kept_list.append(next_url)
        return nexturl_dict


class Article36krSpider(Base36krSpider):

    """
            article 36kr spider of Base36krSpider
    """

    def parse_nexturl_list(self, cur_url, data):
        nexturl_dict = {}
        if re.compile('p/\d+\.html?').search(cur_url):
            cur_url = cur_url.split('?')[0].split('#')[0]
            # got artical page
            if self.parse_artical(cur_url, data):
                nexturl_dict[cur_url] = 1
        elif re.compile('topic').search(cur_url):
            # got topic page
            return self.parse_topic(cur_url, data)
        return nexturl_dict


if __name__ == "__main__":
    '''
    # generally crawl articles in 36kr
    start_urls = ['http://www.36kr.com']
    allowed_domains = ['36kr.com']
    spd = Gen36krSpider(
        start_urls=start_urls,
        allowed_domains=allowed_domains,
        maxdept=3,
        maxkeptnum=5,
        output_file='gen_articles.xml')
    spd.start(isBFS=True)
    '''
    #crawl topics in 36kr
    start_urls = ['http://www.36kr.com/explore']
    allowed_domains = ['36kr.com']
    spd = Topic36krSpider(
                    start_urls=start_urls,
                    allowed_domains=allowed_domains,
                    maxdept=2,
                    maxkeptnum=300,
                    output_file='topics.xml')
    spd.start(isBFS=True)
    '''
    #crawl article with topics in 36kr
    at_spd = Artical36krSpider(
                    start_urls=spd._kept_list,
                    allowed_domains=allowed_domains,
                    maxdept=3,
                    maxkeptnum=1000,
                    delay=0.5,
                    output_file='articles.xml')
    #print len(at_spd._item_list)
    at_spd.start(isBFS=False)
    '''
