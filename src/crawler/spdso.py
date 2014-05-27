import os, sys, time, re
import urlparse
from lxml import etree
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup
from items import Question, Tag
#from spider import BaseSpider
from util.spider import BaseSpiderV2, BaseSpiderV3

class BaseSTOFSpider(BaseSpiderV3):
    """
        Base spider for crawling stackoverflow.com
    """
    def parse_question(self, cur_url, data):
        """
            used to parse question page in stackoverflow.com
        """
        #save data
        pathname = self._saveweb(cur_url+'.html', data)
        if pathname is None:
            #error to save
            return False
        print '[Question]\tDoc.%s\t saved from %s' %(len(self._kept_list)+1, cur_url)
        #parse data
        question = Question()
        try:
            tree = etree.parse(StringIO(data), etree.HTMLParser())
            question['id'] = cur_url.split('/')[-2]
            question['url'] = cur_url
            question['title'] = tree.xpath('//*[@id="question-header"]/h1/a/text()')[0]
            try:
                # edit by someone
                user_info = tree.xpath('//*[@id="question"]/table/tr[1]/td[2]/div/table/tr/td[3]/div/div[3]/a')[0]
            except:
                # not edit by someone
                user_info = tree.xpath('//*[@id="question"]/table/tr[1]/td[2]/div/table/tr/td[2]/div/div[3]/a')[0]
            question['author'] = user_info.text
            question['author_url'] = urlparse.urljoin(cur_url, user_info.get('href'))
            question['path'] = os.path.abspath(pathname)
            self._item_list.append(question)
            self._kept_list.append(question['url'])
        except Exception,e:
            print 'error to parse html',e
            return False
        return True



class GenSTOFSpider(BaseSTOFSpider):
    """
        general STOF spider of BaseSTOFSpider
    """

    def parse_nexturl_list(self, cur_url, data):
        nexturl_dict = {}
        if re.compile('questions/\d+').search(cur_url):
            cur_url = cur_url.split('?')[0].split('#')[0]
            #got artical page
            if self.parse_question(cur_url, data):
                nexturl_dict[cur_url] = 1
            return nexturl_dict
        try:
            soup = BeautifulSoup(data, fromEncoding='utf-8')
        except Exception,e:
            print 'open soup error',e
            return nexturl_dict
        #add real_url to already crawled url list
        for tag in soup.findAll('a'):
            if not tag.has_key('href'):
                continue
            next_url = urlparse.urljoin(cur_url, tag['href'].encode('utf-8'))#.rstrip()
            #check next_url
            if self.bad_domain(next_url) or next_url in self._url_dict:
                continue
            nexturl_dict[next_url] = 1
        return nexturl_dict

class TagSTOFSpider(BaseSTOFSpider):
    """
        tag STOF spider of BaseSTOFSpider
    """

    def parse_nexturl_list(self, cur_url, data):
        nexturl_dict = {}
        try:
            soup = BeautifulSoup(data, fromEncoding='utf-8')
            self.parse_tag(cur_url, soup)
            #add real_url to already crawled url list
            for tag in soup.findAll('a'):
                if not tag.has_key('href') or not 'tags' in tag['href']:
                    continue
                next_url = urlparse.urljoin(cur_url, tag['href'].encode('utf-8'))#.rstrip()
                #check next_url
                if self.bad_domain(next_url) or next_url in self._url_dict:
                    continue
                nexturl_dict[next_url] = 1
        except Exception,e:
            print 'open soup error',e
        finally:
            return nexturl_dict

    def parse_tag(self, cur_url, soup):
        """
            used to parse tag page in stackoverflow.com
        """
        item_list = []
        kept_list = []
        tag_cells = soup.findAll('td', {'class':'tag-cell'})
        for tag_cell in tag_cells:
            tag = Tag()
            tag['name'] = tag_cell.find('a').text
            # print 'name', tag['name']
            tag['url'] = urlparse.urljoin(cur_url, tag_cell.find('a').get('href').encode('utf-8'))
            # print 'url', tag['url']
            try:
                tag['count'] = tag_cell.find('span', {'class':'item-multiplier-count'}).text
            except:
                tag['count'] = '0'
            # print 'count', tag['count']
            print "[Tag]\tNo.%s:%s with Url:%s" %(len(self._kept_list)+len(kept_list)+1, tag['name'], tag['url'])
            item_list.append(tag)
            kept_list.append(tag['url'])
        self._item_list.extend(item_list)
        self._kept_list.extend(kept_list)

class QuestionSTOFSpider(BaseSTOFSpider):
    def parse_nexturl_list(self, cur_url, data):
        nexturl_dict = {}
        if re.compile('questions/\d+').search(cur_url):
            cur_url = cur_url.split('?')[0].split('#')[0]
            #got artical page
            if self.parse_question(cur_url, data):
                nexturl_dict[cur_url] = 1
            return nexturl_dict
        try:
            soup = BeautifulSoup(data, fromEncoding='utf-8')
            #add real_url to already crawled url list
            for tag in soup.findAll('a'):
                if not tag.has_key('href') or not re.compile('questions/\d+').search(tag['href']):
                    continue
                next_url = urlparse.urljoin(cur_url, tag['href'].encode('utf-8'))#.rstrip()
                #check next_url
                if self.bad_domain(next_url) or next_url in self._url_dict:
                    continue
                nexturl_dict[next_url] = 1
        except Exception,e:
            print 'open soup error',e
        finally:
            return nexturl_dict

if __name__ == "__main__":
    #crawl tags in stackoverflow 
    start_urls = ['http://stackoverflow.com/tags']
    allowed_domains = ['stackoverflow.com']
    spd = TagSTOFSpider(
            start_urls=start_urls, 
            allowed_domains=allowed_domains, 
            maxdept=3,
            maxkeptnum=300,
            output_file='tags.xml')
    spd.start(isBFS=True)
    #crawl question with tags in stackoverflow
    at_spd = QuestionSTOFSpider(
            start_urls=spd._kept_list,
            allowed_domains=allowed_domains,
            maxdept=3,
            maxkeptnum=1000,
            delay=0.5,
            output_file='questions.xml')
    #print len(at_spd._item_list)
    at_spd.start(isBFS=False)
    
    # generally crawl questions in stackoverflow
    # start_urls = ['http://stackoverflow.com/questions?sort=featured']
    # allowed_domains = ['stackoverflow.com']
    # spd = GenSTOFSpider(
    #         start_urls=start_urls, 
    #         allowed_domains=allowed_domains, 
    #         maxdept=3, 
    #         maxkeptnum=5,
    #         output_file='stackoverflow.com/gen_questions.xml')
    # spd.start(isBFS=True)
    
    
    
    
    
    