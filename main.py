from urllib.parse import quote
import urllib
import json
from urllib.request import urlopen

import numpy as np

# 输入实体名，返回实体全部的三元组知识
# 格式：http://shuyantech.com/api/cndbpedia/value?q=**&attr=**    # 前**是查询的实体名；后**是查询的属性名


def judge_pure_english(keyword):

    return all(ord(c) < 128 for c in keyword)
print(judge_pure_english("8MDD4V30,8,0,http://dbpedia.org/resource/Albacete_Balompié"))