#-*- coding: utf-8 -*-
'''
Created on 20130422

@author:    zyy_max
@desc:  get tokens from web content

Modified on 20130516
@brief: 1. make classes: WhitspaceTokenizer for simple token; JiebaXXXTokenizer for several types of jieba token
        2. all tokenizer classes are based on BaseTokenizer
'''
import jieba
import os, sys, re
from stemming.porter2 import stem

class BaseTokenizer(object):
    def __init__(self, data=None):
        self.tokens = []
        self.data = data
        
    def filter(self):
        if self.data is not None:
            self.data = ''.join(map(self._filterchar, self.data))
            self.tokens = self.data.split()
            self.data = ' '.join(self.tokens)
        
    def _filterchar(self, c):
        if not re.compile(u'[\w\u4e00-\u9fa5]').match(c):
            #if __debug__:
            #   print c
            return ' '
        return c.lower()
        
    def token(self, data=None):
        if data is not None:
            self.data = data 
        if self.data is not None:
            self.filter()
            self.tokens = self._tokenproc()
        return self
        #print '.'.join(self.tokens)
    
    def _tokenproc(self):
        raise NotImplementedError
        
    def tostring(self):
        return '/'.join(self.tokens)

class WhitespaceTokenizer(BaseTokenizer):
    def _tokenproc(self):
        return self.data.split()

class PorterStemmerTokenizer(BaseTokenizer):
    def _tokenproc(self):
        return map(stem, self.data.split())     

class JiebaSearchTokenizer(BaseTokenizer):
    def _tokenproc(self):
        return list(jieba.cut_for_search(self.data))
        
class JiebaCutTokenizer(BaseTokenizer):
    def _tokenproc(self):
        return list(jieba.cut(self.data))   

            
    
    
    
    
    