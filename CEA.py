import threading
import numpy as np
import csv
import pandas as pd
from spellchecker import SpellChecker
import gl
import similarity.simi
from useful import Dbpedia_Format
spell = SpellChecker()

from searchmanage_Wiki import SearchManage, Wikipedia, SparqlQuery, BingQuery, SpellCheck, DbpediaLookUp


def correct(word):
    index = word.rfind("/")
    word = word[index + 1:]
    word = word.replace("_", " ")
    return word


def is_number(s):
    try:

        float(s)

        return True

    except ValueError:

        pass

    try:

        import unicodedata

        unicodedata.numeric(s)

        return True

    except (TypeError, ValueError):

        pass

    return False


def writetocsv(result):
    # python2可以用file替代open
    with open("test/test.csv", "a", newline="",encoding= u'utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # 先写入columns_name
        # 写入多行用writerows
        writer.writerow(result)
def judge_pure_english(keyword):

    return all(ord(c) < 128 for c in keyword)

def writetocsv_other(result):
    with open("test/test_other.csv", "a", newline="",encoding= u'utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # 先写入columns_name
        # 写入多行用writerows
        writer.writerow(result)


def check(item):
    if item[0] == "Q" and item[1:len(item)].isdigit():
        return True
    else:
        return False


def getmark(A, B):
    if is_number(A) and is_number(B):
        if float(B) != 0:
            return 1 - abs((float(A) - float(B)) / float(B))
    else:
        return similarity.simi.ratio_similarity(A, B)


db = DbpediaLookUp(m_num=1000)
end_point = "https://dbpedia.org/sparql"
sparql_ = """
  SELECT?a?b
  WHERE {<%s> ?a ?b
  FILTER regex(?a, "^http://dbpedia.org/ontology/").
  FILTER(str(?a)!="http://dbpedia.org/ontology/wikiPageWikiLink").
  FILTER(str(?a)!="http://dbpedia.org/ontology/abstract")
 } LIMIT 100
  """
sql2 = SparqlQuery(m_num=20000, format_='json', url_=end_point, sparql_=sparql_)


def start_search(points1):
    r7 = db.search_run(points1, patten='search', is_all=False, maxResults=10,timeout=5)["resource"]

    resu=sql2.search_run(r7, timeout=10000)

    r8 = resu["b"]
    r9 = resu["a"]
    value=[]
    url=[]
    isurl=[]
    for i in range(len(r8)):
        templist1=[]
        templist2=[]
        for j in range(len(r8[i])):
            tempvalue,tempurl,tempisurl=Dbpedia_Format(r9[i][j],r8[i][j])
            templist1.append(tempvalue)
            templist2.append(tempurl)
        value.append(templist1)
        url.append(templist2)
    return r7, value,url


def start_write(thisword, re1, text_col, result, col, claim0,url):
    result_1 = result
    tempmark = 0
    ans = ""
    resuid=0
    word=""
    for item in text_col:
        word+=item

    if str(col) != "0":
        key = str(result_1[0]) + " " + str(result_1[1])
        if key in gl.result:
            dbkey = gl.result[key]
            if ans in gl.idmap:
                for i in range(len(re1)):
                    if re1[i] in gl.idmap[dbkey]:
                        ans = re1[i]
                        resuid=i
                        break
    if str(col) != "0" and ans == "":
        key = str(result_1[0]) + " " + str(result_1[1])
        if key in gl.result:
            dbkey = gl.result[key]
            if dbkey in gl.valuemap:
                claim_list = gl.valuemap[dbkey]
                label_score = 0
                for i in range(len(re1)):
                    if judge_pure_english(re1[i]):
                        label_mark = 0
                        for claim in claim_list:
                            if judge_pure_english(claim):
                                label_mark = max(label_mark, getmark(correct(re1[i]), claim))
                            else:
                                continue
                        if label_mark > label_score:
                            label_score = label_mark
                            ans = re1[i]
                            resuid=i
                if label_score < 0.7:
                    ans = ""
                    resuid=0
    if str(col) != "0" and ans == "":
        item_mark = 0
        for i in range(len(re1)):
            tempscore = similarity.simi.ratio_similarity(thisword, correct(re1[i]))
            if tempscore > item_mark:
                ans = re1[i]
                resuid=i
                item_mark = tempscore
        if item_mark < 0.7:
            ans = ""
            resuid=0
    if ans == "":
        if len(re1) == 1:
            ans = re1[0]
            resuid=0
        else:
            for i in range(len(re1)):
                if judge_pure_english(re1[i]):
                    claim_mark = similarity.simi.ratio_similarity(correct(re1[i]),thisword+" "+word)
                    for item in text_col:
                        mark_item = 0
                        for claim in claim0[i]:
                            if judge_pure_english(claim) :
                                tempmark_item = getmark(item, correct(claim))
                                if tempmark_item > mark_item:
                                    mark_item = tempmark_item
                        claim_mark += mark_item
                    if claim_mark > tempmark:
                        ans = re1[i]
                        resuid=i
                        tempmark = claim_mark
    if ans == "" and len(re1) != 0:
        ans = re1[0]
        resuid=0
    if ans != "":
        result_1.append(ans)
        writetocsv(result_1)
        if str(col) == "0":
            gl.result[str(result_1[0]) + " " + str(result_1[1])] = result_1[3]
            gl.idmap[ans]=url[resuid]
            gl.valuemap[ans] = claim0[resuid]
    else:
        writetocsv_other(result)


valid_path = "DataSets/ToughTablesR2-DBP/Valid/gt/cea_gt.csv"
test_path = "DataSets/ToughTablesR2-DBP/Test/target/cea_target.csv"
points = []
text = []
file_temp = {}


def startserach(start, end, freq, path=""):
    global points, text
    filelist = np.array(
        pd.read_csv(path + valid_path, usecols=[0], header=None).iloc[start:end]).tolist()
    rowlist_1 = np.array(
        pd.read_csv(path + valid_path, usecols=[1], header=None).iloc[start:end]).tolist()
    collist_1 = np.array(
        pd.read_csv(path + valid_path, usecols=[2], header=None).iloc[start:end]).tolist()
    for m in range(len(filelist)):
        df = None
        if filelist[m][0] not in file_temp:
            file = path + "DataSets/ToughTablesR2-DBP/Valid/tables/" + filelist[m][0] + ".csv"
            df = pd.read_csv(file, header=None)
            file_temp[filelist[m][0]] = df
        else:
            df = file_temp.get(filelist[m][0])
        length = df.shape[1]
        col_text = []
        for i in range(length):
            if not pd.isna(df.iloc[rowlist_1[m][0], i]) and i != collist_1[m][0]:
                col_text.append(df.iloc[rowlist_1[m][0], i])
        keyword = df.iloc[rowlist_1[m][0], collist_1[m][0]]
        points.append(keyword)
        text.append(col_text)
        if (m + 1) % freq == 0:
            re1, re2,url = start_search(points)
            for i in range(len(re1)):
                index = m - freq + i + 1
                result = []
                result.append(filelist[index][0])
                result.append(rowlist_1[index][0])
                result.append(collist_1[index][0])
                if len(re1[i]) != 0:
                    start_write(points[i], re1[i], text[i], result, collist_1[index][0], re2[i],url[i])
            points = []
            text = []


startserach(0, 100,100)
