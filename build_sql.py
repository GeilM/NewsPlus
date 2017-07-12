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




stopwords = []
def load_stopwords():
    f = open("stopwords.txt",encoding='utf-8')
    for line in f:
        word = line.strip()
        stopwords.append(word)
        
    return stopwords



# 将传入的文段进行分词，传回分词结果，注意对文段中的特殊字符的处理,返回列表
def split_words(filename):
    # 还是存下文件以便比对
#    print("-------------------------------------------------------------------------------------")
    curDir = os.getcwd()    # 获取当前目录
    sFilePath = 'segfile'
    path = os.path.join(curDir,sFilePath)
    if not os.path.exists(path):
        os.mkdir(path)
    f = open(filename, 'r', encoding='utf-8')
    title = f.readline()
    title = title.strip()
    # id = get_id(title)

    # print('title\t'+str(id))
    # time.sleep(1)
    context = f.read()
    f.close()
    mark = ['','\n',"\n\n",'%',',','。','/','-','.','、','“','，','”','【','】','{','}','[',']','?','？','!','！','》','《','<','>','↓',':','：','\\']
    seg_list = jieba.cut(context,cut_all=False)

    result = []
    for seg in seg_list:
        seg = str(seg).replace(':', '').replace('(', '').replace(')', '')

        seg = ''.join(seg.split())
        if seg not in mark and seg not in stopwords:
#            print(seg)
            # time.sleep(1)?
            result.append(seg)

    # 将分词后的结果存到本地
    # f = open(path + "/" + str(id) + "-seg.txt", 'w', encoding='utf-8')
    # f.write(' '.join(result))
    # f.close()
    # print('保存成功')
    # print("-----------------------------------------------------------------------------------")
    return result    # 分词列表


# 并取出有权重的词作为keywords
def extract_words(word,weight,i,k):

    word_weight = {}
    for j in range(len(word)):
        # print(str(word[j])+'\t'+str(weight[i][j]))
        word_weight[word[j]] = weight[i][j]


    word_weight = sorted(word_weight.items(),key=lambda x:x[1],reverse=True)

    topK_words = []
    topK_values = []
    for i in range(k):
        if word_weight[i][1] > 0:
            topK_words.append(word_weight[i][0])
            topK_values.append(word_weight[i][1])
    # result = ','.join(topK)

    return topK_words,topK_values


# 计算在文档集中tf-idf的权重值
def tf_idf(datasets,filelist):

    vectorizer = CountVectorizer()  # 用于统计词频矩阵
    transformer = TfidfTransformer()    # 统计TF-IDF的值
    tfidf = transformer.fit_transform(vectorizer.fit_transform(datasets))


    word = vectorizer.get_feature_names()  # 所有文本的关键字
    weight = tfidf.toarray().tocsr()  # 对应的tf-idf矩阵

    curDir = os.getcwd()  # 获取当前目录
    sFilePath = 'tfidfFile'
    path = os.path.join(curDir, sFilePath)
    if not os.path.exists(path):
        os.mkdir(path)

    # 将每份文档的TF-IDF写入tfidfFile文件夹中保存,i代表文档，j代表文档中的词
    # for i in range(len(weight)):
    #     # print(filelist[i])
    #     filelist[i] = filelist[i].strip()   # 去除字符串两边的空白符和引号
    #     # time.sleep(1)
    #     # id = get_id(filelist[i])
    #     # print('id\t'+str(id))
    #     # print('--------------------------writing all the tf-idf in the file -------------------')
    #     f = open(path + '\\' + filelist[i]+'-weights.txt', 'w', encoding='utf-8')
    #     for j in range(len(word)):
    #         # print(str(word[j]) + '\t' + str(weight[i][j]))
    #         f.write(str(word[j]) + '\t' + str(weight[i][j]) + "\n")
    #     f.close()
    # 是不是要用到稀疏矩阵来存啊欸
    return word, weight


# 将得到的newsinfo的信息保存到数据库，info为数据库元组
def save_db(*info):

    if len(info[1]) == 0:
        keywords = ''
    else:
        keywords = ','.join(info[1])


    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='123456', db='newsIR', charset='utf8')
        cur = conn.cursor()
        sql = "update newsInfo set keywords='{0}' where article_id='{1}' "
        cur.execute(sql.format(keywords,info[0]))
        # print("update news info 成功")

        sql = "insert into weights(article_id,keyword,weight) values('{}','{}','{}')"
        check = "select * from weights where article_id='{0}' and keyword='{1}'"
        #  考虑了提取的关键字列表为空的情况
        for i in range(len(info[1])):
            # print(info[0]+','+info[1][i]+','+str(info[2][i]))
            row = cur.execute(check.format(info[0],info[1][i]))
            if not row:
                cur.execute(sql.format(info[0],info[1][i],str(info[2][i])))

            # print("插入 weights 成功，第 {:d} 条".format(i))

        print('save_db:完全更新了数据库')
    except Exception as e:
        print("save_db:插入失败",e)
        print(keywords)


    finally:
        conn.commit()
        cur.close()
        conn.close()

    return

def get_all_titles():
    titles = []
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='123456', db='newsIR', charset='utf8')
        cur = conn.cursor()
        sql = "select * from newsInfo"
        news = cur.execute(sql)

        # 获得文章的title,标题权重较大
        for each in cur.fetchall():
            titles.append(each[0])
            
    except Exception as e:
        print('e\t'+e)
    finally:
        conn.commit()
        cur.close()
        conn.close()
        
    return titles



# 建立数据库
def building():
    load_stopwords()
    targetDir = os.path.join(os.getcwd(),'news-text')
    # targetDir = 'G:/PycharmProject/IR/files'
    k = 15      # 指定keywords的数量
    corpus = []     # 存放分词结果
    filelist = []
    
    

    files = os.listdir(targetDir)
    for file in files:

        file_dir = os.path.join(targetDir,file)
        re = split_words(file_dir)
        # print(file+'\t'+title)
        id = file.split('.')[0]
        filelist.append(id)
        doc = ' '.join(re)
#        print(doc)
        corpus.append(doc)  # 二维数组，i为文档，j为分词

    # 将得到的分词结果统计，使用TF-IDF算法,应该会返回两个参数
    word,weight = tf_idf(corpus,filelist)

    for i in range(len(filelist)):
     
        # 取出文档中重要的词，写入数据库,返回topK个关键词，按大小顺序排列
        topK_words,topK_values = extract_words(word,weight,i,k)
        # 构造info, 写入数据库（
        # keywords = ';'.join(topK_words)
        # keyvalues = ';'.join(topK_values)
#        print("save\t"+filelist[i])
        save_db(filelist[i],topK_words,topK_values)

    return
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





if __name__=='__main__':
    
    jieba.load_userdict('G:/PycharmProject/test/dict.txt')
    building()




