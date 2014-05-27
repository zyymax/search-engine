#-*-coding : utf-8 -*-
"""
Created at 2013-05-27

author: zyy_max
desc:   used to find K-nearest neighbours of each document
"""
from collections import defaultdict
from pprint import pprint
import os, sys, math
root_path = os.path.abspath('..')
if not root_path in sys.path:
    sys.path.append(root_path)
from crawler.util.ItemUtils import ItemUtils
from crawler.items import Article, Question, BaseItem

class KNNBuilder(object):
    def __init__(self, **kwargs):
        self.ItemClass = kwargs.get('ItemClass', BaseItem)
        xmlpath = kwargs.get('xmlpath', None)
        if xmlpath is not None:
            self.articles = list(self.parse_items(xmlpath, self.ItemClass))
        self.field = kwargs.get('field', 'token_content')
        self.vector_path = kwargs.get('vector_path', None)
        self.knn_path = kwargs.get('knn_path', None)
        self.naive_matrix = kwargs.get('naive_matrix', None)
        self.knn_show = kwargs.get('knn_show', None)
        self.df_path = kwargs.get('df_path', None)
        if self.knn_show is not None:
            self.k = kwargs.get('k', 3)
    
    def prepare(self):
        print 'preparing idf_list & vec_per_doc...'
        self.df_dict = self.build_df_dict(self.field)
        df_sum = sum(self.df_dict.values())
        self.df_list = self.sort_dict_into_list(self.df_dict, reverse=False)
        self.idf_list = [(math.log10(df_sum/count), word) for count, word in self.df_list]
        print 'totally',len(self.df_dict),'words found'
        # pprint(self.idf_list[:10])
        vec_list = []
        id_count = 0
        docid_id_dict = {}
        id_docid_list = []
        for article in self.articles:
            docid_id_dict[article['id']] = id_count
            id_docid_list.append(article['id'])
            id_count += 1
            vector = list(self.build_tfdf_vector(article[self.field]))
            # print article['id'], len(filter(lambda x : x > 0, vector)), max(vector)
            pos_vec = {}
            total = math.sqrt(sum([x*x for x in vector]))
            for idx in xrange(len(vector)):
                if vector[idx] != 0:
                    vector[idx] = vector[idx] / total
                    pos_vec[idx] = vector[idx]
            vec_list.append(pos_vec)
            article['vector'] = ','.join(map(lambda x: '%.3f' % x if x!=0 else '0', vector))
        self.docid_id_dict = docid_id_dict
        self.id_docid_list = id_docid_list
        self.vec_list = vec_list
        
    def buildKNN(self):
        print 'building knn...'
        size = len(self.vec_list)
        knn_dict = {}
        for id1 in xrange(size):
            knn_dict[id1] = {}
            for id2 in xrange(size):
                if id1 == id2:
                    continue
                if id2 in knn_dict and id1 in knn_dict[id2]:
                    knn_dict[id1][id2] = knn_dict[id2][id1]
                else:
                    knn_dict[id1][id2] = self.cos_dist(self.vec_list[id1], self.vec_list[id2])
        knn_list = []
        for idx in xrange(size):
            knn_list.append(list(self.sort_dict_into_list(knn_dict[idx], reverse=True)))
        self.knn_list = knn_list

    def saveKNN(self, ItemClass):
        print 'saving necessary data...'
        if self.vector_path is not None:
            # saving vector_path
            ItemUtils(ItemClass=ItemClass)._save(self.articles, self.vector_path, field = ['id', 'vector'])
        if self.knn_path is not None:
            # saving knn_path
            for article in self.articles:
                docid = article['id']
                article['knn_list'] = ','.join(['%.5f/%s' % (score, self.id_docid_list[idx]) for score, idx in self.knn_list[self.docid_id_dict[docid]]])
            ItemUtils(ItemClass=ItemClass)._save(self.articles, self.knn_path, field = ['id', 'knn_list'])
        if self.naive_matrix is not None:
            # saving naive_matrix
            naive_knn_dict = []
            size = len(self.knn_list)
            for id1 in xrange(size):
                naive_knn_dict.append({})
                for score, id2 in self.knn_list[id1]:
                    naive_knn_dict[id1][id2] = score
            line_list = []
            for i in xrange(size):
                line = ''
                for j in xrange(size):
                    line += '[%s][%s]:' % (i, j)
                    if i == j:
                        line += '1 '
                    else:
                        line += '%.5f ' % naive_knn_dict[i][j]
                line_list.append(line[:-1]+'\n')            
            open(self.naive_matrix, 'w').writelines(line_list)
        if self.knn_show is not None:
            # saving knn_show
            id_title_dict = {}
            for article in self.articles:
                id_title_dict[article['id']] = article['title']
            line_list = []
            for idx1 in xrange(len(self.knn_list)):
                line = id_title_dict[self.id_docid_list[idx1]]+':'
                for i in xrange(self.k):
                    score, idx2 = self.knn_list[idx1][i]
                    line += '(%s, %.5f, %s),' % (i+1, score, id_title_dict[self.id_docid_list[idx2]])
                # print type(line), line.encode('utf-8')
                line_list.append(line.encode('utf-8')[:-1]+'\n')
            # print type(line_list), line_list[0]
            open(self.knn_show, 'w').writelines(line_list)
        if self.df_path is not None:
            #saving df path
            line_list = []
            for i in xrange(len(self.df_list)):
                line_list.append('%s\t%s\t%.2f\n' % (self.df_list[i][1].encode('utf-8'), self.df_list[i][0], self.idf_list[i][0]))
            open(self.df_path, 'w').writelines(line_list)

    def run(self):
        print 'read to build KNN'
        self.prepare()
        self.buildKNN()
        self.saveKNN(self.ItemClass)



    def cos_dist(self, pos_vec_1, pos_vec_2):
        score = 0
        for pos in pos_vec_1.keys():
            if pos in pos_vec_2:
                score = score + pos_vec_1[pos] * pos_vec_2[pos]
        return score

    def parse_items(self, xmlpath, ItemClass):
        return ItemUtils(ItemClass=ItemClass)._parse_items(xmlpath)

    def build_tfdf_vector(self, content):
        tf_dict = self.build_wordcount_dict(content)
        vector = []
        for idf, word in self.idf_list:
            tf = tf_dict[word]
            yield idf*math.log10(tf+1) if tf != 0 and idf != 0 else 0

    def build_df_dict(self, field):
        df_dict = defaultdict(int)
        for item in self.articles:
            wc_dict = self.build_wordcount_dict(item[field])
            for word in wc_dict.keys():
                df_dict[word] += wc_dict[word]
        return df_dict

    def build_wordcount_dict(self, content):
        """
            build word count dictionary for single content
        """
        wc_dict = defaultdict(int)
        for word in content.split('/'):
            wc_dict[word] += 1
        return wc_dict

    def sort_dict_into_list(self, wc_dict, reverse=True):
        wc_list = [(count, word) for word, count in wc_dict.items()]
        return sorted(wc_list, cmp=lambda x,y: cmp(x[0], y[0]), reverse=reverse)

if __name__=="__main__":
    kb = KNNBuilder(
            ItemClass=Article,
            xmlpath='../36kr/stop_articles.xml',
            field='token_content',
            vector_path='../36kr/vectors.txt',
            knn_path='../36kr/knn_lists.txt',
            naive_matrix='../36kr/naive_matrix.txt',
            knn_show='../36kr/knn_show.txt',
            df_path='../36kr/df_show.txt',
            k=3,
        )
    kb.run()
    st_kb = KNNBuilder(
            ItemClass=Question,
            xmlpath='../stackoverflow/stop_questions.xml',
            field='token_content',
            vector_path='../stackoverflow/vectors.txt',
            knn_path='../stackoverflow/knn_lists.txt',
            naive_matrix='../stackoverflow/naive_matrix.txt',
            knn_show='../stackoverflow/knn_show.txt',
            df_path='../stackoverflow/df_show.txt',
            k=3,
        )
    st_kb.run()
