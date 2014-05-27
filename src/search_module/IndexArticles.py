#!/usr/bin/env python
import sys
import os
import lucene
from java.io import File
from org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.document import Document, Field, NumericDocValuesField
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.util import Version

import threading
import time
from datetime import datetime
root_path = os.path.abspath('..')
sys.path.append(root_path)
from crawler.util.ItemUtils import ItemUtils
from crawler.items import Article, Question


class Ticker(object):
    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)


class IndexFiles(object):
    """Usage: python Indexitemdocs <XMLPath> <IndexPath>"""

    def __init__(self, **kwargs):
        xmlpath = kwargs.get('xmlpath')
        storeDir = kwargs.get('storeDir')
        analyzer = kwargs.get('analyzer')
        ItemClass = kwargs.get('ItemClass')
        if not os.path.exists(storeDir):
            os.mkdir(storeDir)
        store = SimpleFSDirectory(File(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)
        # self.indexDocs(xmlpath, writer)
        self.indexXML(xmlpath, writer, ItemClass)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexXML(self, xmlpath, writer, ItemClass):
        count = 0
        for itemdoc in ItemUtils(ItemClass=ItemClass)._parse_items(xmlpath):
            doc = Document()
            for key in itemdoc:
                try:
                    if key in ['token_taglist', 'token_content', 'token_title', 'token_author', 'author']:
                        doc.add(Field(key, itemdoc[key],
                                Field.Store.YES, Field.Index.ANALYZED,
                                Field.TermVector.WITH_POSITIONS_OFFSETS))
                    elif key.endswith('url') or key in ['category', 'path', 'title', 'tag_list', 'content']:
                        doc.add(Field(key, itemdoc[key],
                                Field.Store.YES, Field.Index.NO))
                    elif key == 'id':
                        doc.add(NumericDocValuesField('id', long(itemdoc[key])))
                except Exception, e:
                    print e, key, itemdoc['title']
            writer.addDocument(doc)
            count += 1
            print '\radding doc %s:\t%s...' % (count, itemdoc['title'][:5]),


class IndexApp(object):
    def __init__(self, xmlpath, indexpath, ItemClass):
        self.jccenv = lucene.initVM()
        self.xmlpath = xmlpath
        self.indexpath = indexpath
        self.ItemClass = ItemClass

    def run(self):
        print 'lucene', lucene.VERSION
        start = datetime.now()
        try:
            IndexFiles(
                xmlpath=self.xmlpath,
                storeDir=self.indexpath,
                analyzer=SimpleAnalyzer(Version.LUCENE_CURRENT),
                ItemClass=self.ItemClass)
            end = datetime.now()
            print end - start
        except Exception, e:
            print "Failed: ", e


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print IndexFiles.__doc__
        sys.exit(1)
    IndexApp(sys.argv[1], sys.argv[2], Article).run()
