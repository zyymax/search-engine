search-engine
=============
TODO
----
1.Crawler + Preprocess + Index + KNN + KMeans:

    >>> cd src
    >>> mkdir ../data
    >>> ./main.py

2.Web Search:

    >>> cd src
    >>> python web/web.py
    
Modules
------
### 1.Crawler

crawl docs from 36kr.com and questions from stackoverflow.com

### 2.Preprocess

filter illegal characters;

tokenization: jieba for chinese, porter stemming for english

### 3.Index

build index by pylucene

### 4.Search

search on index by pylucene

### 5.Web

light-weight web server by Tornado


Dependence
----------
Crawler:  BeautifulSoup, lxml, scrapy, stemming

Indexer:  PyLucene

Web Server:  Tornado

