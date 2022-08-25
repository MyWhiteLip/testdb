
import string
import re
from searchmanage_Wiki.tools import Tools
from searchmanage_Wiki import DbpediaLookUp




def isAllPunctuation(word):
    punc = string.punctuation
    if word and not all(every in punc for every in word):
        return True
    return False

# 用于过滤DBpedia查询的属性和属性值
# 参数p：属性列表
# 参数v：属性值列表
# mysql查询参数
# sparql =
# """
#    SELECT*
#    WHERE{
#        < %s > ?p ?v
#        FILTER regex(?p, "^http://dbpedia.org/ontology/").}
# """
# 返回值value：过滤后的属性值字符串类型
# 返回值URL：过滤后的属性值URL类型（即前缀为http://dbpedia.org/resource/），如果本身为字符串类型，则不变
# 返回值isURL: 判断过滤后的属性值是否为URL类型（即前缀为http://dbpedia.org/resource/），1为真，0为假


def Dbpedia_Format(p, v):
    pattern2 = "http://dbpedia.org/ontology/abstract"
    pattern3 = "http://dbpedia.org/resource/Category:"
    pattern4 = "http://dbpedia.org/resource/File:"
    pattern5 = re.compile(r'^(?:http|ftp)s?://')
    value = []
    URL = []
    isURL = []
    for i in range(len(p)):
        if pattern2 != p[i] and pattern3 not in v[i] and pattern4 not in v[i]:
            if "http://dbpedia.org/resource/" in v[i]:
                value.append(v[i][28:len(v[i])].replace("_", " "))
                URL.append(v[i])
                isURL.append(1)
            elif not pattern5.match(v[i]):
                value.append(v[i])
                URL.append(v[i])
                isURL.append(0)
    return value, URL, isURL
