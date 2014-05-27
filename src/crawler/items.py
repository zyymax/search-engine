#-*-coding:utf-8
'''
@author zyy_max
@date   2013-05-05
@brief  Define Item that need to be crawled
'''
from util.item import Item, Field

class BaseItem(Item):
    #original fields
    id = Field()
    title = Field()
    url = Field()
    author = Field()
    author_url = Field()
    content = Field()
    path = Field()
    #tokenized fields
    token_title = Field()
    token_content = Field()
    token_author = Field()
    vector = Field()
    knn_list = Field()


# items for stackoverflow
class Tag(Item):
    name = Field()
    url = Field()
    count = Field()
    
class Question(BaseItem):
    pass

# items for 36kr
class Topic(Item):
    name = Field()
    url = Field()

class Article(BaseItem):
    #original fields
    category = Field()
    cat_url = Field()
    tag_list = Field()
    #tokenized fields
    token_taglist = Field()
