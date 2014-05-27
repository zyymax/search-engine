from BeautifulSoup import BeautifulSoup
from xml.dom import minidom
from urllib2 import urlopen
import urlparse
import os
import sys
import time
import re
from collections import deque
import Queue
from Queue import Empty
import threading


class deStack(deque):

    """
    deque-based Stack
    """

    def popone(self):
        return self.pop()


class deQueue(deque):

    """
    deque-based Queue
    """

    def popone(self):
        return self.popleft()


class BaseSpiderV2(object):

    """
            @author:	zyy_max
            @date:		2013-05-06
            @brief:		basic spider v2 with general purpose of BFS and DFS searching
                                    combined BFS and DFS with deque-based deStack and deQueue
                                    combine dowork and get_nexturl_list
    """

    def __init__(self, **kwargs):
        start_urls = kwargs.get('start_urls', [])
        self.start_urls = list(set(start_urls))
        self.allowed_domains = kwargs.get('allowed_domains', [])
        self._maxdept = kwargs.get('maxdept', 9)
        self._maxnum = kwargs.get('maxnum', 20000)
        self._maxkeptnum = kwargs.get('maxkeptnum', 1000)
        self.delay = kwargs.get('delay', 0.5)
        self.output_file = kwargs.get('output_file', None)
        self.input_file = kwargs.get('input_file', None)
        self.pre_dir = kwargs.get('pre_dir', '')
        self._url_dict = {}
        self._crawled_dict = {}
        self._item_list = []
        self._kept_list = []
        self._subgottastop = False
        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        # extra initilization for subclasses
        pass

    def gottastop(self):
        return len(
            self._crawled_dict) > self._maxnum or len(
            self._kept_list) >= self._maxkeptnum or self._subgottastop

    def bad_domain(self, next_url):
        host = urlparse.urlparse(next_url).netloc
        return not any(host.endswith(domain)
                       for domain in self.allowed_domains)

    def start(self, isBFS=True):
        if isBFS:
            url_que = deQueue((url, 0) for url in self.start_urls)
        else:
            url_que = deStack((url, 0) for url in self.start_urls)
        self.traverse(url_que)
        self.on_close()

    def traverse(self, url_que):
        """
                general BFS/DFS traverse process for basespider
                url_que: deQueue==>BFS, deStack==>DFS
        """
        while not self.gottastop() and len(url_que) != 0:
            cur_url, cur_dept = url_que.popone()
            try:
                response = urlopen(cur_url, None, 5)
                data = response.read()
                real_url = response.geturl()
            except Exception as e:
                print 'open url "%s" error:' % cur_url, e
                continue
            # check real_url
            if self.bad_domain(real_url) or real_url in self._crawled_dict:
                continue
            self._crawled_dict[real_url] = 1
            self._url_dict.pop(real_url, None)
            print 'No.%s,Dep.%s:\tcrawling "%s"' % (len(self._crawled_dict), cur_dept, real_url)
            got_dict = self.parse_nexturl_list(real_url, data)
            self._url_dict.update(got_dict)
            if cur_dept < self._maxdept-1 and len(got_dict) != 0:
                url_que.extend([(next_url, cur_dept+1)
                                for next_url in got_dict.keys()])

    def parse_nexturl_list(self, cur_url, data):
        """
                parse next url_list
                implemented by subclass
        """
        raise NotImplementedError

    def _saveweb(self, url, data, path_name=None):
        # save html
        if path_name is None:
            path_name = os.path.join(
                self.pre_dir,
                url.replace(
                    'http://',
                    '').split('?')[0])
        if os.path.exists(path_name):
            print 'path:%s already exists' % path_name
            return None
        dir_list = path_name.split('/')
        path_list = dir_list[:-1]
        html_name = dir_list[-1]
        dir = ''
        for sub_dir in path_list:
            dir += sub_dir
            if not os.path.exists(dir):
                os.mkdir(dir)
            dir += os.sep
        open(path_name, 'wb').write(data)
        return path_name

    def on_create(self):
        """
                test def
        """
        if self.input_file is None:
            return
        with open(self.input_file, 'r') as ins:
            format = self.input_file[self.input_file.rindex('.')+1:].upper()
            in_str = ins.read()
            if format == 'TXT':
                pass
                # item = Item()  # which Item is used???

    def on_close(self):
        if self.output_file is None:
            return
        with open(self.output_file, 'w') as out:
            format = self.output_file[self.output_file.rindex('.')+1:].upper()
            out_str = None
            lines = []
            for item in self._item_list:
                data = item.tostring(format=format)
                lines.append(data)
            if format == 'TXT':
                out_str = os.linesep.join(lines)
            elif format == 'XML':
                out_str = '<?xml version="1.0" encoding="utf-8"?>\n<items>' + \
                    ''.join(lines)+'</items>'
            if out_str is not None:
                out.write(out_str)


class BaseSpiderV3(BaseSpiderV2):

    """
            @author:	zyy_max
            @date:		2013-05-08
            @brief:		basic spider v3 with multi-thread urlopen
                                    implemented with Queue and threading
    """

    def __init__(self, **kwargs):
        start_urls = kwargs.get('start_urls', [])
        self.start_urls = list(set(start_urls))
        self.allowed_domains = kwargs.get('allowed_domains', [])
        self._maxdept = kwargs.get('maxdept', 9)
        self._maxnum = kwargs.get('maxnum', 20000)
        self._maxkeptnum = kwargs.get('maxkeptnum', 1000)
        self.delay = kwargs.get('delay', 0.5)
        self.output_file = kwargs.get('output_file', None)
        self.input_file = kwargs.get('input_file', None)
        self.pre_dir = kwargs.get('pre_dir', '')
        if self.pre_dir != '':
            if not os.path.exists(self.pre_dir):
                raise IOError('%s not exists' % self.pre_dir)
        # to keep in-queue and not-crawled urls
        self._url_dict = {}
        # to keep out-queue and crawled urls
        self._crawled_dict = {}
        # to keep crawled items
        self._item_list = []
        # to keep necessary urls
        self._kept_list = []
        # to keep threading pool
        self._thread_pool = []
        self._subgottastop = False
        self.initialize(**kwargs)

    def start(self, isBFS=True, maxQueSize=10000, threadNum=5):
        self.data_que = Queue.Queue(maxQueSize)
        if isBFS:
            self.url_que = Queue.Queue(maxQueSize)
        else:
            self.url_que = Queue.LifoQueue(maxQueSize)
        for start_url in self.start_urls:
            self.url_que.put((start_url, 0))
        self.make_start_thread_pool()
        self.stop_free_thread_pool()
        self.on_close()

    def make_start_thread_pool(self, threadNum=5, daemons=True):
        for i in xrange(threadNum-1):
            new_thread = threading.Thread(target=self.openurl_work)
            new_thread.setDaemon(daemons)
            self._thread_pool.append(new_thread)
            new_thread.start()
        new_trav_thread = threading.Thread(target=self.traverse)
        new_trav_thread.setDaemon(daemons)
        self._thread_pool.append(new_trav_thread)
        new_trav_thread.start()

    def stop_free_thread_pool(self):
        for existing_thread in self._thread_pool:
            existing_thread.join()
        del self._thread_pool[:]

    def openurl_work(self):
        while not self.gottastop():
            try:
                cur_url, cur_dept = self.url_que.get(timeout=3)
            except Empty, e:
                print 'Exiting:\tno available url in queue...'
                break
            try:
                response = urlopen(cur_url, None, 10)
                data = response.read()
                real_url = response.geturl()
                if self.bad_domain(real_url) or real_url in self._crawled_dict:
                    continue
                self.data_que.put((real_url, cur_dept, data))
                self._crawled_dict[real_url] = 1
                self._url_dict.pop(real_url, None)
                lock = threading.RLock()
                lock.acquire()
                print '[HTML]\tNo.%s,Dep.%s:\tcrawling "%s"' % (len(self._crawled_dict), cur_dept, real_url)
                lock.release()
                time.sleep(self.delay)
            except Exception as e:
                print 'open url "%s" error:' % cur_url, e

    def traverse(self):
        """
                general BFS/DFS traverse process for basespider
                url_que: deQueue==>BFS, deStack==>DFS
        """
        while True:
            try:
                real_url, cur_dept, data = self.data_que.get(timeout=3)
                got_dict = self.parse_nexturl_list(real_url, data)
                if self.gottastop():
                    break
                self._url_dict.update(got_dict)
                if cur_dept < self._maxdept-1:
                    for next_url in got_dict.keys():
                        self.url_que.put((next_url, cur_dept+1))
            except Empty, e:
                print 'Exiting:\tno available data in queue...'
                break
