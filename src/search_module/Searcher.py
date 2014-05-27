#!/usr/bin/env python
from lucene import \
	QueryParser, IndexSearcher, StandardAnalyzer, SimpleAnalyzer, ChineseAnalyzer,\
	SimpleFSDirectory, File, VERSION, initVM, Version, Highlighter, SimpleFragmenter,\
	QueryScorer, SimpleHTMLFormatter, StringReader
import sys, jieba
from stemming.porter2 import stem

class ArticleSearcher(object):
	def __init__(self, store_dir):
		initVM()
		directory = SimpleFSDirectory(File(store_dir))
		self.searcher = IndexSearcher(directory, True)
		print 'loaded index: %s' %store_dir
		self.analyzer = {}
		self.analyzer['StandardAnalyzer'] = StandardAnalyzer(Version.LUCENE_CURRENT)
		self.analyzer['SimpleAnalyzer'] = SimpleAnalyzer(Version.LUCENE_CURRENT)
		self.analyzer['ChineseAnalyzer'] = ChineseAnalyzer(Version.LUCENE_CURRENT)

	def _set_store_dir(self, store_dir):
		self.searcher.close()
		directory = SimpleFSDirectory(File(store_dir))
		self.searcher = IndexSearcher(directory, True)
		print 'loaded index: %s' %store_dir
	def close(self):
		self.searcher.close()

	def search_by(self, **kwargs):
		command = kwargs.get('command', '')
		if command == '':
			return None
		field = kwargs.get('field')
		query_type = kwargs.get('query_type', 'chi')
		if query_type == 'chi':
			if field in ['token_taglist', 'token_content', 'token_title', 'token_author']:
				command = ' '.join(jieba.cut_for_search(command))
			hlt_analyzer = self.analyzer['ChineseAnalyzer']
		else:
			if field in ['token_content', 'token_title']:
				command = ' '.join(map(stem, command.split()))
			hlt_analyzer = self.analyzer['StandardAnalyzer']
		analyzer = self.analyzer['SimpleAnalyzer']
		num = kwargs.get('num', 50)
		attrs = kwargs.get('attrs', ['url', 'title'])
		print "[%s]\tSearching for '%s' in field '%s'" %(query_type, command, field)
		query = QueryParser(Version.LUCENE_CURRENT, field, analyzer).parse(command)
		if field in ['token_content', 'token_title']:
			getAbs = True
			query_for_highlight = QueryParser(Version.LUCENE_CURRENT, 'content', hlt_analyzer).parse(command)
			scorer = QueryScorer(query_for_highlight)
			formatter = SimpleHTMLFormatter("<strong>", "</strong>")
			#formatter = SimpleHTMLFormatter("<span class=\"highlight\">", "</span>")
			highlighter = Highlighter(formatter, scorer)
			fragmenter = SimpleFragmenter(20)
			highlighter.setTextFragmenter(fragmenter)
		else:
			getAbs = False
		scoreDocs = self.searcher.search(query, num).scoreDocs
		print "%s total matching documents." % len(scoreDocs)
		articles = []
		for scoreDoc in scoreDocs:
			doc = self.searcher.doc(scoreDoc.doc)
			article = {}
			for attr in attrs:
				article[attr] = doc.get(attr)
			if getAbs == True:
				content = doc.get('content')
				tokenStream = hlt_analyzer.tokenStream("content", StringReader(content))
				article['abstract'] = highlighter.getBestFragments(tokenStream, content, 3, "...")
			articles.append(article)
		return articles

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "Usage: SearchFiles <IndexPath>"
		sys.exit(-1)
	print 'lucene', VERSION
	searcher = ArticleSearcher(sys.argv[1])
	while True:
		command = raw_input("Query:")
		if command == '':
			break
		for article in searcher.search_by(field = 'token_title', command=command.decode('gbk').encode('utf-8'), query_type='chi', num=100):
			print 'title: %s' %article['abstract']