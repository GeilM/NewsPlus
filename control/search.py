import jieba
import os
import time
import scipy.sparse
import pymysql.cursors
import pymysql.connections
import sys
import re
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer,CountVectorizer
from gensim.models import word2vec
import copy



stopwords = []
index = {}
titles = {}
categories = {}



def fuzzyfinder(user_input):
#    print(titles)
    suggestions =[]
    pattern = '.*?'.join(user_input)
    regex = re.compile(pattern)
    for item in titles.values():
#        print(item)
        match = regex.search(item)
        if match:
            suggestions.append((len(match.group()),match.start(),item))
    return [x for _,_, x in sorted(suggestions)]
    
    

# 计算索引事对相近词的大小？读取数据库，这里可以有变化  我爱北京天安门
def calc_words(seg_list):
    print('---------------------------------------------------------------')

    # seg_list = segs.split(' ')

    print('seglist')
    print(seg_list)
    
    # 计算了TF-IDF的值
    scores = {}
    for seg in seg_list:
        if seg in index.keys():
            pair_dic = index[seg]
            for k,v in pair_dic.items():
                if k not in scores.keys():
                    scores[k] = 0
                scores[k] += v
                  
                  
#    计算标题的作用
    for k,v in titles.items():
        for seg in seg_list:
            if re.search(seg,v):
                if k not in scores.keys():
                    scores[k] = 0
                obj = re.findall(seg,v)
                scores[k]+=(0.2*len(obj))
        
#   计算category的作用
    for k in categories.keys():
        for seg in seg_list:
            if seg in categories[k]:
                if k in scores.keys():
                    scores[k] += 0.1    
            
    return scores



# 第一个存的原输入，匹配标题
def remove_blank(seg_list,words):
    search_list = []
    search_list.append(words)
    mark = ['', '\n', "\n\n", '%', ',', '。', '/', '-', '.', '、', '“', '，', '”', '【', '】', '{', '}', '[', ']', '?', '？',
            '!', '！', '》', '《', '<', '>', '↓', ':', '：', '\\']

    for seg in seg_list:
        seg = str(seg).replace(':', '').replace('(', '').replace(')', '')

        seg = ''.join(seg.split())
        if seg not in mark and seg not in stopwords:
            search_list.append(seg)
    return search_list



# 获取用户输入的搜索词，对数据库进行搜索,返回一个排序列表（按照计算所得值排序）
def search(words):
    # print(words)
    seg_list = jieba.lcut_for_search(words)
    # 去除列表中的空白
    search_list = remove_blank(seg_list,words)

    # 搜索近义词
    # 先直接用TF-IDF算权重
    scores = calc_words(search_list)

    #对score排序,从大到小排序
    results = sorted(scores.items(),key= lambda x:x[1],reverse=True)
    
    paths = []
    for each in results:
#        print(each[0]+'\t'+str(each[1]))
        if each[1] > 0.2:
            paths.append(each[0])
    return paths

#def search

def load_stopwords():
    f = open("stopwords.txt",encoding='utf-8')
    for line in f:
        word = line.strip()
        stopwords.append(word)
        
    return stopwords

def load_sql():
    f = open('load_sql.txt','r',encoding='utf-8')
    for line in f.readlines():
            line = line.strip()
            row = line.split('\t')
            pairs = row[1].split(';')
            dic = {}
            for each in pairs: 
                pair = each.strip('(').strip(')')
                tmp = pair.split(',')
                dic[tmp[0].strip()] = float(tmp[1].strip())
#                id_w.append(dic)
            index[row[0].strip()] = dic
    f.close()
    return index

def load_category():
    f = open('cate.txt','r',encoding='utf-8')
    for line in f.readlines():
        line = line.strip()
        row = line.split('\t')
        names = row[1].split(';')
        categories[row[0]] = names
    f.close()    
    return categories



def get_all_titles():
    f = open('titles.txt','r',encoding='utf-8')
    for line in f.readlines():
        line = line.strip()
        row = line.split('\t')
        titles[row[0]] = row[1]
    f.close()
    return titles



# if __name__=='__main__':
#     jieba.load_userdict('dict.txt')
#     load_stopwords()
#     load_sql()
#     get_all_titles()
#     load_category()
#     words = input("请输入想要搜索的内容：")
#     print(fuzzyfinder(words,titles))
#     # print(relavent)



