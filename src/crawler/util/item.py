"""
Scrapy Item

See documentation in docs/topics/item.rst
@midified:    zyy_max
"""

from pprint import pformat
from UserDict import DictMixin
from lxml import etree

from scrapy.utils.trackref import object_ref


class BaseItem(object_ref):
    """Base class for all scraped items."""
    pass


class Field(dict):
    """Container of field metadata"""


class ItemMeta(type):

    def __new__(mcs, class_name, bases, attrs):
        fields = {}
        new_attrs = {}
        for n, v in attrs.iteritems():
            if isinstance(v, Field):
                fields[n] = v
            else:
                new_attrs[n] = v

        cls = type.__new__(mcs, class_name, bases, new_attrs)
        cls.fields = cls.fields.copy()
        cls.fields.update(fields)
        return cls


class DictItem(DictMixin, BaseItem):

    fields = {}

    def __init__(self, *args, **kwargs):
        self._values = {}
        if args or kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).iteritems():
                self[k] = v

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        if key in self.fields:
            self._values[key] = value
        else:
            raise KeyError("%s does not support field: %s" % \
                (self.__class__.__name__, key))

    def __delitem__(self, key):
        del self._values[key]

    def __getattr__(self, name):
        if name in self.fields:
            raise AttributeError("Use item[%r] to get field value" % name)
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            raise AttributeError("Use item[%r] = %r to set field value" % \
                (name, value))
        super(DictItem, self).__setattr__(name, value)

    def keys(self):
        return self._values.keys()

    def __repr__(self):
        return pformat(dict(self))


class Item(DictItem):

    __metaclass__ = ItemMeta

    def fromstring(self, data, format='TXT'):
        if format == 'TXT':
            for item in data.split('||||'):
                try:
                    idx = item.index(':')
                    self[item[:idx]] = item[idx+1:].decode('utf-8')
                except Exception,e:
                    print 'no ":" found',item.decode('utf-8')
                    return False
        elif format == 'XML':
            parser = etree.XMLParser(recover=True, encoding='utf-8')
            try:
                tree = etree.fromstring(data, parser)
                for child in tree.xpath('//item')[0].iterchildren():
                    if child.text is not None:
                        self[child.tag] = child.text.replace('&lt;', '<').replace('&gt;', '>')
                    else:
                        self[child.tag] = ''
            except Exception,e:
                print 'error parsing %s:' % data,e
                return False
        return True

    def tostring(self, format='TXT', field=None):
        result = ''
        if format == 'TXT':
            for key in self.keys():
                if field is not None and not key in field:
                    continue
                result += '%s:%s||||' % (key, self[key].encode('utf-8'))
            result = result[:-4]
        elif format == 'XML':
            for key in self.keys():
                if field is not None and key not in field:
                    continue
                result += '<%s>%s</%s>' % (key, self[key].encode('utf-8').replace('<', '&lt;').replace('>', '&gt;'), key)
            result = '<item>%s</item>' % result
        return result

