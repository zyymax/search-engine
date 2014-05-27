"""
Created at 2013-05-30

author: zyy_max
desc:   used to cluster with KMeansClustering Algorithm
"""
import random, time, math, os
from collections import defaultdict
from pprint import pprint
from datetime import datetime
from copy import deepcopy
class KMeansClustering(object):
    """
        input: dictionary of vectors:{docid:{index:float}},...}
    """
    def __init__(self, vectors=None):
        print 'checking types of input vectors...'
        if not isinstance(vectors, dict):
            print self.__doc__
            raise TypeError
        for docid in vectors.keys():
            if not isinstance(vectors, dict):
                print self.__doc__
                raise TypeError
            for idx in vectors[docid].keys():
                value = vectors[docid][idx]
                if not isinstance(idx, int) or not isinstance(value, float):
                    print self.__doc__
                    raise TypeError
        vector_list = []
        id_count = 0
        id_docid_list = []
        docid_id_dict = {}
        for docid in vectors:
            id_docid_list.append(docid)
            docid_id_dict[docid] = id_count
            vector_list.append(vectors[docid])
            id_count += 1
        self.vector_list = vector_list
        self.id_docid_list = id_docid_list
        self.docid_id_dict = docid_id_dict

    def getcluster(self, count):
        kernal_dict = self.init_clusters(count)
        self.iter_getcluster(kernal_dict)

    def save(self, path):
        kernal_file = os.path.join(path, 'kernals.txt')
        codebook_file = os.path.join(path, 'codebook.txt')
        with open(kernal_file, 'w') as out:
            for kid in self.kernal_dict.keys():
                out.write('Kernal no.%s:' % kid)
                for pos, value in self.kernal_dict[kid].items():
                    out.write('(%d, %.3f),' % (pos, value))
                out.write('\n')
        with open(codebook_file, 'w') as out:
            for kid in self.kernal_dict.keys():
                for idx, vid in enumerate(self.code_book[kid]):
                    out.write('KernalID:%s\t%d/%d\t' % (kid, idx+1,len(self.code_book[kid])))
                    docid = self.id_docid_list[vid]
                    score = self.cos_dist(self.kernal_dict[kid], self.vector_list[vid])
                    out.write('DocID:%s\tDist:%.3f' % (docid, score))
                    out.write('\n')

    def iter_getcluster(self, kernal_dict):
        round_no = 0
        while True:
            if round_no == 10:
                break
            round_no += 1
            start = datetime.now()
            code_book = self.get_codebook(kernal_dict)
            pre_kernal_dict = deepcopy(kernal_dict)
            kernal_dict = self.get_kernaldict(code_book)
            print 'round no.%s\tcost:%ss' % (round_no, (datetime.now()-start).total_seconds()),[(kid, len(vids)) for kid, vids in code_book.items()]
            if self.gottastop(kernal_dict, pre_kernal_dict):
                break
        self.kernal_dict = kernal_dict
        self.code_book = code_book

    def get_kernaldict(self, code_book):
        kernal_dict = {}
        for kid in code_book:
            kernal = {}
            for vid in code_book[kid]:
                kernal.update(self.vector_list[vid])
            for pos in kernal.keys():
                count = 0
                v_sum = 0
                for vid in code_book[kid]:
                    if pos in self.vector_list[vid]:
                        count += 1
                        v_sum += self.vector_list[vid][pos]
                kernal[pos] = v_sum / count
            v_total = math.sqrt(sum(map(lambda x: x*x, kernal.values())))
            for pos in kernal.keys():
                kernal[pos] = kernal[pos]/v_total
            kernal_dict[kid] = kernal
        return kernal_dict

    def get_codebook(self, kernal_dict):
        code_book = defaultdict(list)
        for idx in xrange(len(self.vector_list)):
            max_dist = 0
            max_kid = 0
            for kid in kernal_dict.keys():
                kernal = kernal_dict[kid]
                dist = self.cos_dist(kernal, self.vector_list[idx])
                if dist > max_dist:
                    max_dist = dist
                    max_kid = kid
            code_book[max_kid].append(idx)
        return code_book

    def init_clusters(self, count):
        print 'generating initial seeds...'
        random.seed(time.time())
        size = len(self.vector_list)
        template = range(size)
        for i in xrange(count):
            idx = random.randint(i, size-1)
            template[i], template[idx] = template[idx], template[i]
        print 'random seed:',template[:count]
        kernal_dict = {}
        for idx, vid in enumerate(template[:count]):
            kernal_dict[idx] = self.vector_list[vid]
        return kernal_dict

    def gottastop(self, kernal_dict_1, kernal_dict_2):
        diff_sum = 0
        for kid in kernal_dict_1.keys():
            diff = self.cos_dist(kernal_dict_1[kid], kernal_dict_2[kid])-1
            diff_sum += diff
        #     print kid,diff,
        # print ''
        return True if abs(diff_sum) < 1e-6 else False

    def cos_dist(self, pos_vec_1, pos_vec_2):
        score = 0
        for pos in pos_vec_1.keys():
            if pos in pos_vec_2:
                score = score + pos_vec_1[pos] * pos_vec_2[pos]
        return score

class CluserApp(object):
    def __init__(self, vector_path, cluster_root):
        self.vector_path = vector_path
        self.cluster_root = cluster_root
        if not os.path.exists(cluster_root):
            os.mkdir(cluster_root)

    def run(self):
        print 'ready to cluster with vectors in file:', self.vector_path
        vectors = {}
        with open(self.vector_path) as ins:
            for line in ins.readlines():
                parts = line.split('||||')
                for part in parts:
                    if part.startswith('id'):
                        docid = part.split(':')[-1].rstrip()
                    elif part.startswith('vector'):
                        vector = map(lambda x: float(x), part.split(':')[-1].split(','))
                        pos_vec = {}
                        for idx in xrange(len(vector)):
                            value = vector[idx]
                            if value == 0:
                                continue
                            pos_vec[idx] = value
                vectors[docid] = pos_vec
        kmc = KMeansClustering(vectors)
        kmc.getcluster(10)
        kmc.save(self.cluster_root)

if __name__=="__main__":
    ca = CluserApp('../stackoverflow/vectors.txt', '../stackoverflow/cluster')
    ca.run()


