#!/usr/bin/env python
'''
Created on 20130508

@author:    zyy_max
@desc:  main entry of project 'SearchEngine'
'''
import os
import sys
from parsers import KRContentParser, KRTokenizer,\
    KRDeStopword, STOFContentParser, STOFTokenizer, STOFDeStopword
from spdkr import Topic36krSpider, Article36krSpider
from spdso import TagSTOFSpider, QuestionSTOFSpider


def direc(path):
    if path.endswith('/') or path.endswith('\\'):
        path = path[:-1]
    return path+os.sep


class BaseCrawlApp(object):

    """
        necessary args:
            pre_dir : base root for crawled data '36kr'
            wordcount_file : file to hold word count 'wordcount.txt'
            base_fname : basic item data from crawler 'articles.xml'
            content_fname : item data with content 'par_articles.xml'
            token_fname : item data with tokenized fields 'token_articles.xml'
            stp_fname : item data after deleting stop words 'stop_articles.xml'
            stop_list : file to hold stop list or stop_list itself 'chi_stopword.txt'
            CotentParser : user-defined ContentParser class 'KRContentParser'
            Tokenizer : user-defined Tokenizer class 'KRTokenizer'
            DeStopword : user-defined DeStopword class 'KRDeStopword'
    """

    def __init__(self, **kwargs):
        pre_dir = kwargs.get('pre_dir')
        if not os.path.exists(pre_dir):
            os.mkdir(pre_dir)
        self.pre_dir = pre_dir
        self.wordcount_file = os.path.join(
            pre_dir,
            kwargs.get('wordcount_file'))
        self.base_fname = os.path.join(pre_dir, kwargs.get('base_fname'))
        self.content_fname = os.path.join(pre_dir, kwargs.get('content_fname'))
        self.token_fname = os.path.join(pre_dir, kwargs.get('token_fname'))
        self.stp_fname = os.path.join(pre_dir, kwargs.get('stp_fname'))
        self.stop_list = kwargs.get('stop_list')
        self.ContentParser = kwargs.get('ContentParser')
        self.Tokenizer = kwargs.get('Tokenizer')
        self.DeStopword = kwargs.get('DeStopword')

    def run(self):
        self.start_crawl()
        self.start_parse_content()
        self.start_tokenize()
        self.start_del_stop()

    def start_crawl(self):
        raise NotImplementedError

    def start_parse_content(self):
        """
            parsing content
        """
        parser = self.ContentParser()
        print "parsing contents from file:%s to file:%s" % (self.base_fname, self.content_fname)
        parser.parse(self.base_fname)
        parser.save(self.content_fname)
        print 'successfully saved to %s' % self.content_fname

    def start_tokenize(self):
        """
            tokenizing
        """
        token = self.Tokenizer()
        print "tokening from file:%s to file:%s" % (self.content_fname, self.token_fname)
        token.parse(self.content_fname)
        token.save(self.token_fname)
        print 'successfully saved to %s' % self.token_fname

    def start_del_stop(self):
        """
            deleting stop word
        """
        dstp = self.DeStopword()
        dstp.add_stopwordlist(
            stopfname=self.stop_list
            )
        print "deleting stop word from file:%s to file:%s" % (self.token_fname, self.stp_fname)
        dstp.parse(self.token_fname)
        dstp.save(self.stp_fname)
        print 'successfully saved to %s' % self.stp_fname


class KRCrawlApp(BaseCrawlApp):

    def start_crawl(self):
        """
            crawling
        """
        # crawl topics in 36kr
        start_urls = ['http://www.36kr.com/explore']
        allowed_domains = ['36kr.com']
        spd = Topic36krSpider(
            start_urls=start_urls,
            allowed_domains=allowed_domains,
            maxdept=1,
            maxkeptnum=300,
            output_file=os.path.join(self.pre_dir, 'topics.xml'),
            pre_dir=self.pre_dir)
        spd.start(isBFS=True)
        # crawl article with topics in 36kr
        at_spd = Article36krSpider(
            start_urls=spd._kept_list,
            allowed_domains=allowed_domains,
            maxdept=3,
            maxkeptnum=100,
            delay=0.1,
            output_file=self.base_fname,
            pre_dir=self.pre_dir)
        at_spd.start(isBFS=False)


class STOFCrawlApp(BaseCrawlApp):

    def start_crawl(self):
        """
            crawling
        """
    # crawl tags in stackoverflow
        start_urls = ['http://stackoverflow.com/tags']
        allowed_domains = ['stackoverflow.com']
        spd = TagSTOFSpider(
            start_urls=start_urls,
            allowed_domains=allowed_domains,
            maxdept=3,
            maxkeptnum=300,
            output_file=os.path.join(self.pre_dir, 'tags.xml'),
            pre_dir=self.pre_dir,
            )
        spd.start(isBFS=True)
        # crawl question with tags in stackoverflow
        at_spd = QuestionSTOFSpider(
            start_urls=spd._kept_list,
            allowed_domains=allowed_domains,
            maxdept=3,
            maxkeptnum=1000,
            delay=0.1,
            output_file=self.base_fname,
            pre_dir=self.pre_dir,
            )
        # print len(at_spd._item_list)
        at_spd.start(isBFS=False)

if __name__ == "__main__":
    ca = KRCrawlApp(
        pre_dir='../data/36kr',
        wordcount_file='wordcount.txt',
        base_fname='articles.xml',
        content_fname='par_articles.xml',
        token_fname='token_articles.xml',
        stp_fname='stop_articles.xml',
        stop_list='crawler/chi_stopword.txt',
        ContentParser=KRContentParser,
        Tokenizer=KRTokenizer,
        DeStopword=KRDeStopword,
        )
    ca.run()
    # stof_crawler = STOFCrawlApp(
    #         pre_dir = 'stackoverflow',
    #         wordcount_file = 'wordcount.txt',
    #         base_fname = 'questions.xml',
    #         content_fname = 'par_questions.xml',
    #         token_fname = 'token_questions.xml',
    #         stp_fname = 'stop_questions.xml',
    #         stop_list = 'eng_stopword.txt',
    #         ContentParser = STOFContentParser,
    #         Tokenizer = STOFTokenizer,
    #         DeStopword = STOFDeStopword,
    #     )
    # stof_crawler.run()
