# -*- coding:utf-8 -*-
# @author  : Shuxin_Wang
# @email   : 213202122@seu.edu.cn
# @time    : 2022/8/13 
# @function: the script is used to do something.
# @version : V1.0 
#
import re
from searchmanage_Wiki import DbpediaLookUp, Tools

URL_DBPEDIA_SEARCH = "https://lookup.dbpedia.org/api/search"


def resource_to_type(resources: list, db: DbpediaLookUp) -> list:
    REG_ = re.compile("^http://dbpedia.org/resource/")
    data_1d, index_ = Tools.list_level(resources)
    res = []
    res2 = []
    for r in data_1d:
        s = REG_.sub("", r)
        res.append(s)
        res2.append(s.replace("_", " "))
    dpr = db.search_run(res2, timeout=10000, patten='search', is_all=False, maxResults=50)

    ind = []
    for i in range(len(res)):
        ind.append(0)
        for j in range(len(dpr['resource'][i])):
            if re.findall(res[i], dpr['resource'][i][j]):
                ind[i] = j
                break

    type_ = []
    for i in range(len(ind)):
        type_.append(dpr['type'][i][ind[i]])
    return Tools.list_back(type_, index_)


if __name__ == "__main__":
    # DbpediaLookUp->"resource"
    db = DbpediaLookUp(m_num=10)
    r7 = db.search_run(['Tupelo'], patten='search', is_all=False, maxResults=20)
    a = r7['type'][0]
    print(a)
    print(len(a))
    # print(r7['resource'][0])
    b = resource_to_type(r7['resource'][0], db)
    print(b)
    print(len(b))
