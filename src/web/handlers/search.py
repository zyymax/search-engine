# -*- coding:utf-8 -*-
from base import BaseHandler
import tornado.web
from datetime import datetime
import jieba
import os
import sys
root_path = os.path.abspath('..')
if root_path not in sys.path:
    sys.path.append(root_path)
from search_module.Searcher import ArticleSearcher
from util.common import permit_read_status, \
    search_accounts_number, search_essays_number

kr_searcher = ArticleSearcher('../data/36kr/index_all')
stof_searcher = ArticleSearcher('../data/stackoverflow/index_all')


class SearchLucHandler(BaseHandler):
    def get(self):
        template_values = {}
        query = self.get_argument('query', None)
        field = self.get_argument('field', 'token_title')
        domain = self.get_argument('domain', '36kr')
        if query is None or query == '':
            template_values['articles'] = []
            template_values['total'] = 0
            self.redirect('/')
        else:
            start = datetime.now()
            if domain == '36kr':
                articles = kr_searcher.search_by(
                    field=field,
                    command=query,
                    num=1000,
                    query_type='chi',
                    attrs=['url', 'title', 'tag_list', 'author', 'author_url', 'category', 'cat_url'])
            elif domain == 'stof':
                articles = stof_searcher.search_by(
                    field=field,
                    command=query,
                    num=1000,
                    query_type='eng',
                    attrs=['url', 'title', 'author', 'author_url'])
            end = datetime.now()
            template_values['cost_time'] = (end-start).total_seconds()
            total_count = len(articles)
            template_values['hasnext'] = 1 if total_count > search_accounts_number else 0
            template_values['lastindex'] = search_accounts_number
            template_values['addfactor'] = search_accounts_number
            template_values['total'] = total_count
            template_values['articles'] = articles  # [:search_accounts_number]
            template_values['query'] = query
            template_values['field'] = field
            template_values['domain'] = domain
            self.render('search_luc.html', template_values=template_values)
