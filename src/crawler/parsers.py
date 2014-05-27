'''
Created on 20130420

@author:    zyy_max
@desc:    parsers needed by crawler.py

Modified on 20130516
@brief:    1. make classes: KRContentParser for parseing content from html; KRTokenizer for tokenizing from content
        2. KRContentParser and KRTokenizer are based on KRBaseFilter
        3. data is transmitted by XML-format file
'''

import os
import sys
import re
from BeautifulSoup import BeautifulSoup
from StringIO import StringIO
from lxml import etree
from items import Article, Question
from util.ItemUtils import ItemUtils
from util.tokenizer import WhitespaceTokenizer, PorterStemmerTokenizer, JiebaCutTokenizer, JiebaSearchTokenizer


class BaseFilter(object):

    """
        base filter Class for ContentParser/Tokenizer/DeStopword
    """

    def __init__(self, src_fname=None):
        if src_fname is not None:
            self._item_list = list(self._load_items(src_fname))

    def _load_items(self, src_fname):
        raise NotImplementedError

    def parse(self, src_fname=None):
        if src_fname is not None:
            self._item_list = list(self._load_items(src_fname))
        count = 0
        for item in self._item_list:
            self._parse_item(item)
            count += 1
            print '\r%s%% finished' % (count*100/len(self._item_list)),

    def _parse_item(self, article):
        raise NotImplementedError

    def save(self, dst_fname):
        raise NotImplementedError


class BaseDeStopword(object):

    """
        base Class for DeStopword
    """

    def add_stopwordlist(self, **kwargs):
        self.stop_dict = kwargs.get('stopdict', {})
        if len(self.stop_dict) == 0:
            fname = kwargs.get('stopfname', None)
            if fname is not None:
                with open(fname, 'r') as ins:
                    for line in ins.readlines():
                        self.stop_dict[line.rstrip().decode('gbk')] = 1

    def filter_stopword(self, data_list):
        result_list = []
        for data in data_list:
            if data not in self.stop_dict:
                result_list.append(data)
        return result_list


class KRBaseFilter(BaseFilter):
    def _load_items(self, src_fname):
        return ItemUtils(ItemClass=Article)._parse_items(src_fname)

    def save(self, dst_fname):
        ItemUtils(ItemClass=Article)._save(self._item_list, dst_fname)


class KRContentParser(KRBaseFilter):
    def _parse_item(self, article):
        try:
            data = open(article['path'], 'r').read()
        except Exception, e:
            print 'error to open file %s' % article['path'], e
            return
        try:
            soup = BeautifulSoup(data, fromEncoding='utf-8')
            content = soup.find("div", attrs={"class": "content-wrapper"})
            content_list = []
            for tag in content.findAll("p"):
                if tag.text != '':
                    content_list.append(tag.text)
            article['content'] = ''.join(content_list)
        except Exception, e:
            print 'error to parse file %s' % article['path'], e


class KRTokenizer(KRBaseFilter):
    def _parse_item(self, article):
        jbc_token = JiebaCutTokenizer()
        jbs_token = JiebaSearchTokenizer()
        wtsp_token = WhitespaceTokenizer()
        article['token_content'] = jbs_token.token(article['content']).tostring()
        article['token_title'] = jbs_token.token(article['title']).tostring()
        article['token_taglist'] = jbc_token.token(article['tag_list']).tostring()
        article['token_author'] = wtsp_token.token(article['author']).tostring()


class KRDeStopword(BaseDeStopword, KRBaseFilter):
    def _parse_item(self, article):
        article['token_content'] = '/'.join(self.filter_stopword(article['token_content'].split('/')))


class STOFBaseFilter(BaseFilter):
    def _load_items(self, src_fname):
        return ItemUtils(ItemClass=Question)._parse_items(src_fname)

    def save(self, dst_fname):
        ItemUtils(ItemClass=Question)._save(self._item_list, dst_fname)


class STOFContentParser(STOFBaseFilter):
    def _parse_item(self, question):
        try:
            data = open(question['path'], 'r').read()
        except Exception, e:
            print 'error to open file %s' % question['path'], e
            return
        try:
            soup = BeautifulSoup(data, fromEncoding='utf-8')
            content_list = []
            for code in soup.findAll('code'):
                code.extract()
            for post in soup.findAll("div", {"class": "post-text"}):
                term_list = []
                for tag in post.contents:
                    if isinstance(tag, unicode):
                        term_list.append(tag)
                    elif tag.name == u'p':
                        term_list.append(tag.text)
                    elif tag.name == u'ol':
                        ol_list = []
                        for li in tag.findAll('li'):
                            ol_list.append(li.text)
                        term_list.append(' '.join(ol_list))
                content_list.append(''.join(term_list))
            question['content'] = ''.join(content_list).replace('\n', ' ')
        except Exception, e:
            print 'error to parse file %s' % question['path'], e


class STOFTokenizer(STOFBaseFilter):
    def _parse_item(self, question):
        ps_token = PorterStemmerTokenizer()
        question['token_content'] = ps_token.token(question['content']).tostring()
        question['token_title'] = ps_token.token(question['title']).tostring()


class STOFDeStopword(BaseDeStopword, STOFBaseFilter):
    def _parse_item(self, question):
        question['token_content'] = '/'.join(self.filter_stopword(question['token_content'].split('/')))


if __name__ == "__main__":
    # if len(sys.argv) < 4:
    #     print "usage:\tbase_fname, content_fname, token_fname, stp_fname"
    #     exit(0)
    base_fname = 'questions.xml'
    content_fname = 'par_questions.xml'
    token_fname = 'token_questions.xml'
    stp_fname = 'stop_questions.xml'

    parser = STOFContentParser()
    print "parsing contents from file:%s to file:%s" % (base_fname, content_fname)
    parser.parse(base_fname)
    # os.system('pause')
    parser.save(content_fname)
    print 'successfully saved to %s' % content_fname

    token = STOFTokenizer()
    print "tokening from file:%s to file:%s" % (content_fname, token_fname)
    token.parse(content_fname)
    token.save(token_fname)
    print 'successfully saved to %s' % token_fname

    dstp = STOFDeStopword()
    dstp.add_stopwordlist(
        stopfname='eng_stopword.txt'
        )
    print "deleting stop word from file:%s to file:%s" % (token_fname, stp_fname)
    dstp.parse(token_fname)
    dstp.save(stp_fname)
    print 'successfully saved to %s' % stp_fname




