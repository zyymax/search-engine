#!/usr/bin/env python
"""
Created at 2013-05-29

author:	zyy_max
desc:	main entry of project: SearchEngin
"""
from crawler.crawler import KRCrawlApp, STOFCrawlApp
from search_module.IndexArticles import IndexApp
from search_module.KNN import KNNBuilder
from search_module.KMeans import CluserApp
from crawler.parsers import KRContentParser, KRTokenizer, KRDeStopword, \
    STOFContentParser, STOFTokenizer, STOFDeStopword
from crawler.items import Article, Question
from pprint import pprint

if __name__ == "__main__":
    # 36kr
    # crawler application
    kr_crawler = KRCrawlApp(
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
    kr_crawler.run()
    # indexer application
    kr_indexer = IndexApp(
        '../data/36kr/stop_articles.xml',
        '../data/36kr/index_all',
        Article)
    kr_indexer.run()

    # knn application
    kr_kb = KNNBuilder(
        ItemClass=Article,
        xmlpath='../data/36kr/stop_articles.xml',
        field='token_content',
        vector_path='../data/36kr/vectors.txt',
        knn_path='../data/36kr/knn_lists.txt',
        naive_matrix='../data/36kr/naive_matrix.txt',
        knn_show='../data/36kr/knn_show.txt',
        df_path='../data/36kr/df_show.txt',
        k=1,
        )
    kr_kb.run()

    # KMeans cluster application
    kr_cluster = CluserApp('../data/36kr/vectors.txt', '../data/36kr/cluster')
    kr_cluster.run()

    # stackoverflow
    stof_crawler = STOFCrawlApp(
        pre_dir='../data/stackoverflow',
        wordcount_file='wordcount.txt',
        base_fname='questions.xml',
        content_fname='par_questions.xml',
        token_fname='token_questions.xml',
        stp_fname='stop_questions.xml',
        stop_list='crawler/eng_stopword.txt',
        ContentParser=STOFContentParser,
        Tokenizer=STOFTokenizer,
        DeStopword=STOFDeStopword,
        )
    stof_crawler.run()

    stof_indexer = IndexApp(
        '../data/stackoverflow/stop_questions.xml',
        '../data/stackoverflow/index_all',
        Question)
    stof_indexer.run()

    stof_kb = KNNBuilder(
        ItemClass=Question,
        xmlpath='../data/stackoverflow/stop_questions.xml',
        field='token_content',
        vector_path='../data/stackoverflow/vectors.txt',
        knn_path='../data/stackoverflow/knn_lists.txt',
        naive_matrix='../data/stackoverflow/naive_matrix.txt',
        knn_show='../data/stackoverflow/knn_show.txt',
        df_path='../data/stackoverflow/df_show.txt',
        k=1,
        )
    stof_kb.run()

    stof_cluster = CluserApp(
        '../data/stackoverflow/vectors.txt',
        '../data/stackoverflow/cluster')
    stof_cluster.run()
