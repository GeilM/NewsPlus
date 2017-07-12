import jieba
import os
from gensim.models import word2vec
import logging

stopwords = []

def is_contain_chinese(s):
    ss = ''
   
    for ch in s:
        
        if u'\u4e00' <= ch <= u'\u9fff' or 'a'<=ch<= 'z' or 'A' <= ch <= 'Z':
            ss += ch
        else:
            ss += ch

    return ss


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
#    title = f.readline()
#    title = title.strip()
    # id = get_id(title)

    # print('title\t'+str(id))
    # time.sleep(1)
    context = f.read()
    context = str(context).replace('\n',' ')
    f.close()
    mark = ['','\n',"\n\n",'%',',','。','/','-','.','、','“','，','”','【','】','{','}','[',']','?','？','!','！','》','《','<','>','↓',':','：','\\']
    seg_list = jieba.cut(context,cut_all=False)

    result = []
    for seg in seg_list:
        seg = str(seg).replace(':', '').replace('（', '').replace('）', '').replace("“",'').replace("”",'').replace('"','').replace('|','')

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
    

    
def get_corpus():
    cwd = os.getcwd()
    corpus = []
    file = 'news-text'
    save_corpus = 'corpus.txt'
    f = open(os.path.join(os.getcwd(),save_corpus),'w',encoding='utf-8')
    
    root_dir = os.path.join(cwd,file)
    for file in os.listdir(root_dir):
        filename = os.path.join(root_dir,file)
        seg_list = split_words(filename)
        corpus.append(seg_list)
        txt = ' '.join(seg_list)
        segs = is_contain_chinese(txt)
        f.write(segs+'\n')
            
    f.close()
    
 


def train_words():
    file = 'corpus.txt'
    inp = os.path.join(os.getcwd(),file)
    out1 = 'news.model'
 
    logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.INFO)  
    sentences =word2vec.Text8Corpus(inp)  # 加载语料  
    model =word2vec.Word2Vec(sentences, size=200)  #训练skip-gram模型，默认window=5  
    model.save(out1)
    
    print(model)
    
def load_model():
    model = word2vec.Word2Vec.load(os.path.join(os.getcwd(),'news.model'))
#    汽车的向量
    print(model[u'汽车'])
#    找到最相似的词语
    result = model.most_similar('足球')
    for each in result:
        print(each[0] +'\t'+ str(each[1]))
#    计算相似性
    sim1 = model.similarity(u'勇敢', u'战斗')
    sim2 = model.similarity(u'勇敢', u'胆小')
    sim3 = model.similarity(u'高兴', u'开心')
    sim4 = model.similarity(u'伤心', u'开心')
    
    print(sim1)
    print(sim2)
    print(sim3)
    print(sim4) 
    
#    model.most_similar(positive=['woman', 'king'], negative=['man'])
#    计算两个词集合之间的余弦相似度,当某个词语不再这个训练集合中的时候会报错
    list1 = [u'今天', u'我', u'很', u'开心']
    list2 = [u'空气',u'清新', u'善良', u'开心']
    list3 = [u'国家电网', u'再次', u'宣告', u'破产', u'重新']
    list_sim1 =  model.n_similarity(list1, list2)
    print(list_sim1)
    list_sim2 = model.n_similarity(list1, list3)
    print(list_sim2)
    
    
    
    

if __name__=='__main__':
    jieba.load_userdict('dict.txt')
#    get_corpus()
#    train_words()
    load_model()
    
   
