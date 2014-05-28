search-engine
=============
TODO
----
1.Crawler + Preprocess + Index + KNN + KMeans:

    >>> cd src
    >>> mkdir ../data
    >>> python main.py

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

Setup Dep
---------
1.BeautifulSoup

    >>> sudo pip install BeautifulSoup

2.stemming

    >>> sudo pip install stemming

3.PyLucene
Download PyLucene

    >>> wget http://mirror.bit.edu.cn/apache/lucene/pylucene/pylucene-4.8.0-1-src.tar.gz
    >>> tar zxvf pylucene-4.8.0-1-src.tar.gz
    >>> cd pylucene-4.8.0-1/jcc

Modify JDK_PATH

    >>> sed -i "s#/usr/lib/jvm/java-7-openjdk-amd64#$JAVA_HOME#g" setup.py

[Warning] before you install JCC

$JAVA_HOME/bin need to be in $PATH of root OR you need to add these two lines:

    >>> sed -i "s#'javac'#'$JAVA_HOME/bin/javac'#g" setup.py
    >>> sed -i "s#\['javadoc'\]#\['$JAVA_HOME/bin/javadoc'\]#g" setup.py

Install JCC

    >>> sudo python setup.py install

Install Ant

    >>> sudo apt-get install ant
    
To install PyLucene, you need to modify Path2Python, Path2Java and Path2Ant in "Makefile"

After that:

    >>> cd pylucene-4.8.0-1
    >>> make
    >>> sudo make install







