#-*-coding:utf-8
'''
@author zyy_max
@date   2013-05-27
@brief  item utils -- load, save
'''
from lxml import etree
from item import Item as BaseItem
import os

class ItemUtils(object):
    """
        parser and save instance of ItemClass
    """
    def __init__(self, ItemClass=BaseItem):
        self.ItemClass = ItemClass

    def _parse_items(self, src_fname):
        """
            parse instances of self.ItemClass from src_fname
        """
        format = src_fname[src_fname.rindex('.')+1:].upper()
        if format == 'XML':
            parser = etree.XMLParser(recover=True, encoding='utf-8')
            tree = etree.parse(src_fname, parser)
            for tag in tree.xpath('//item'):
                item = self.ItemClass()
                try:
                    item.fromstring(etree.tostring(tag), format=format)
                    yield item
                except Exception,e:
                    print e
        elif format == 'TXT':
            with open(src_fname, 'r') as ins:
                for line in ins.readlines():
                    item = self.ItemClass()
                    try:
                        item.fromstring(line.rstrip(), format=format)
                        yield item
                    except Exception,e:
                        print e

    def _save(self, item_list, dst_fname, field=None):
        """
            save item_list to dst_fname, keep all field by default or only field in field_list is kept
        """
        with open(dst_fname, 'w') as out:
            format = dst_fname[dst_fname.rindex('.')+1:].upper()
            out_str = None
            lines = []
            for item in item_list:
                data = item.tostring(format=format, field=field)
                lines.append(data)
            if format == 'TXT':
                out_str = os.linesep.join(lines)
            elif format == 'XML':
                out_str = '<?xml version="1.0" encoding="utf-8"?>\n<items>'+'\n'.join(lines)+'</items>'
            if out_str is not None:
                out.write(out_str)
