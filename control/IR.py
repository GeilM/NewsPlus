import jieba
import os
import time
import pymysql.cursors
import pymysql.connections
import sys
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer,CountVectorizer
from gensim.models import word2vec



def get_id(title):
    id = ''
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='asdfgH11', db='newsIR', charset='utf8')
        cur = conn.cursor()
        sql = "select * from newsInfo where title='{0}'"
        print('title\t'+title)
        title.strip('\n')
        cur.execute(sql.format(title))
        id = cur.fetchone()[1]
        print("查询mapping 成功")


    except Exception as e:
        print("查询mapping失败", e)


    finally:
        conn.commit()
        cur.close()
        conn.close()

    return id


# 得到文章标题和id的对应关系，更新weights数据库
def get_mapping():
    mapping = {}
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='asdfgH11', db='newsIR', charset='utf8')
        cur = conn.cursor()
        sql = "select * from newsInfo"
        results = cur.execute(sql)
        for each in results.fetchall():
            mapping[each['title']] = each['article_id']
            # print(each['title']+'\t'+each['article_id'])

        print("查询mapping 成功")


    except Exception as e:
        print("查询mapping失败", e)


    finally:
        cur.close()
        conn.close()

    return mapping


# 训练word2vec的单词向量，输入的是分词语料库？
# 输入为二维列表，分好词的列表
def train_words(texts):
    pass


# 将传入的文段进行分词，传回分词结果，注意对文段中的特殊字符的处理,返回列表
def split_words(filename):
    # 还是存下文件以便比对
    print("-------------------------------------------------------------------------------------")
    curDir = os.getcwd()    # 获取当前目录
    sFilePath = 'segfile'
    path = os.path.join(curDir,sFilePath)
    if not os.path.exists(path):
        os.mkdir(path)
    f = open(filename, 'r', encoding='utf-8')
    title = f.readline()
    title = title.strip()
    id = get_id(title)

    print('title\t'+str(id))
    # time.sleep(1)
    context = f.read()
    f.close()
    mark = ['','\n',"\n\n",'%',',','。','/','-','.','、','“','，','”','【','】','{','}','[',']','?','？','!','！','》','《','<','>','↓',':','：','\\']
    seg_list = jieba.cut(context,cut_all=True)

    result = []
    for seg in seg_list:
        seg = str(seg).replace(':', '').replace('(', '').replace(')', '')

        seg = ''.join(seg.split())
        if seg not in mark:
            # print(seg)
            # time.sleep(1)?
            result.append(seg)

    # 将分词后的结果存到本地
    f = open(path + "/" + str(id) + "-seg.txt", 'w', encoding='utf-8')
    f.write(' '.join(result))
    f.close()
    print('保存成功')
    print("-----------------------------------------------------------------------------------")
    return title,result    # 分词列表


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
    weight = tfidf.toarray()  # 对应的tf-idf矩阵

    curDir = os.getcwd()  # 获取当前目录
    sFilePath = 'tfidfFile'
    path = os.path.join(curDir, sFilePath)
    if not os.path.exists(path):
        os.mkdir(path)

    # 将每份文档的TF-IDF写入tfidfFile文件夹中保存,i代表文档，j代表文档中的词
    for i in range(len(weight)):
        # print(filelist[i])
        filelist[i] = filelist[i].strip()   # 去除字符串两边的空白符和引号
        # time.sleep(1)
        id = get_id(filelist[i])
        # print('id\t'+str(id))
        print('--------------------------writing all the tf-idf in the file -------------------')
        f = open(path + '\\' + str(id) +'-weights.txt', 'w', encoding='utf-8')
        for j in range(len(word)):
            # print(str(word[j]) + '\t' + str(weight[i][j]))
            f.write(str(word[j]) + '\t' + str(weight[i][j]) + "\n")
        f.close()
    # 是不是要用到稀疏矩阵来存啊欸
    return word, weight


# 将得到的newsinfo的信息保存到数据库，info为数据库元组
def save_db(*info):
    keywords = ','.join(info[1])
    # 忘记要存path了。。哦可以直接获取路径来判断category

    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='asdfgH11', db='newsIR', charset='utf8')
        cur = conn.cursor()
        sql = "update newsInfo set keywords='{0}' where article_id='{1}' "
        cur.execute(sql.format(keywords,info[0]))
        print("update news info 成功")

        sql = "insert into weights(article_id,keyword,weight) values('{0}','{1}','{2}')"
        for i in range(len(info[2])):
            # print(info[0]+','+info[1][i]+','+str(info[2][i]))
            cur.execute(sql.format(info[0],info[1][i],str(info[2][i])))

            print("插入 weights 成功，第 {:d} 条".format(i))

        print('save_db:完全更新了数据库')
    except Exception as e:
        print("save_db:插入失败",e)


    finally:
        conn.commit()
        cur.close()
        conn.close()

    return


# 计算索引事对相近词的大小？读取数据库，这里可以有变化  我爱北京天安门
def calc(seg_list):
    print('---------------------------------------------------------------')

    # seg_list = segs.split(' ')

    print('seglist')
    print(seg_list)
    ids = []
    # 存储每篇文章的得分
    scores = {}
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='asdfgH11', db='newsIR', charset='utf8')
        cur = conn.cursor()
        sql = "select * from newsInfo"
        news = cur.execute(sql)

        # 获得文章的id
        for each in cur.fetchall():
            ids.append(each[1])
            # print(each[1])

        sql = "select * from weights where article_id='{0}' and keyword='{1}' "

        # 开始搜索,对每篇文章进行评分统计
        for id in ids:
            score = 0
            for seg in seg_list:
                rows = cur.execute(sql.format(id,seg))
                if rows != 0:
                    score += float(cur.fetchone()[2])
                    # print(float(cur.fetchone()[2]))
            # 完全无关的不添加到字典中去

            if score != 0:
                scores[id] = score

    except Exception as e:
        print("calc:连接数据库失败",e)

    finally:
        conn.commit()
        cur.close()
        conn.close()

    return scores


# 获取文章的路径，便于读取整篇文章
def get_news_path(ids):
    paths = []
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='asdfgH11', db='newsIR', charset='utf8')
        cur = conn.cursor()
        sql = "select * from newsInfo where article_id='{0}'"

        for id in ids:
            cur.execute(sql.format(id))
            info = cur.fetchone()
            paths.append(info[1])
    except Exception as e:
        print("get_news_path：连接数据库失败",e)
    finally:
        conn.commit()
        cur.close()
        conn.close()


    return paths

# 建立数据库
def building():
    targetDir = os.path.join(os.getcwd(),'files')
    # targetDir = 'G:/PycharmProject/IR/files'
    k = 10      # 指定keywords的数量
    corpus = []     # 存放分词结果
    filelist = []

    # 是否应该分板块进行计算？等后面确定了再说吧
    folders = os.listdir(targetDir)
    for folder in folders:
        folder = os.path.join(targetDir,folder)
        files = os.listdir(folder)
        # filelist.extend(files)  # 存的是文件名的二维列表，好像是靠这个来判断怎么存的
        for file in files:
            file = os.path.join(folder,file)
            title,re = split_words(file)

            filelist.append(title)
            doc = ' '.join(re)
            corpus.append(doc) # 二维数组，i为文档，j为分词

    # 将得到的分词结果统计，使用TF-IDF算法,应该会返回两个参数
    word,weight = tf_idf(corpus,filelist)

    for i in range(len(filelist)):
        # 为何mapping会出现nonetype？。。。。。解析有问题？？？吧- -
        id = get_id(filelist[i])
        # print('id\t'+id)
        # time.sleep(5)
        # 取出文档中重重要的词，写入数据库,返回topK个关键词，按大小顺序排列？要存weight的
        topK_words,topK_values = extract_words(word,weight,i,k)
        # 构造info, 写入数据库
        # keywords = ';'.join(topK_words)
        # keyvalues = ';'.join(topK_values)
        save_db(id,topK_words,topK_values)

    return


# 获取用户输入的搜索词，对数据库进行搜索,返回一个排序列表（按照计算所得值排序）
def search(words):

    # print(words)
    seg_list = jieba.lcut_for_search(words)
    # print(' '.join(seg_list))
    # 搜索近义词
    # 先直接用TF-IDF算权重
    scores = calc(seg_list)

    #对score排序,从大到小排序
    results = sorted(scores.items(),key= lambda x:x[1],reverse=True)
    #再次查询db,参数变了
    paths = []
    for each in results:
        paths.append(each[0])
    return paths


# if __name__=='__main__':
#     # building()
#
#     words = input("请输入想要搜索的内容：")
#     relavent = search(words)
#     print('-------')
#     print(relavent)



