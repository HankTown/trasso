# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 10:41:19 2019

@author: HankTown
"""

#此方法将txt文件转化为二维列表，子列表代表句子，子列表的元素是单词，得到的结果用作get_t_trans_asso_words()的参数
def txtToWords(txt,stopwords=None):
    """将txt文本分词后转化为二维数组words
    Keyword arguments:
    txt             --  txt文本的文件地址
    stopwords       --  停用词表的文件地址
    """
    #读入文本
    fname=txt
    f=open(fname,'r',encoding= 'utf-8')
    text=f.read()
    text=text.split('\n')
    stopword = [line.strip() for line in open(stopwords,encoding= 'utf-8').readlines()]
    #以下对文本分句，delimeters是句子分隔符
    seprators='?!;？！。；…'
    for sep in seprators:
        res=[]
        for sentence in text:
            res+=(sentence.split(sep))
        text=res
    
    #以下对分句后的text进行jieba分词
    res=[]
    
    import jieba.posseg as pseg
    
    for sentence in text:
        #分词
        sentence=pseg.cut(sentence)
        sentence=    [w for w in sentence]
        #去除前后空格和非语素字
        sentence=[w.word.strip() for w in sentence if w.flag != 'x']
        #去除空字符
        sentence=[word for word in sentence if len(word) > 0]
        #去除停用词
        if stopwords!=None:
            sentence=[w for w in sentence if w not in stopword]
        res.append(sentence)
    return res

def combine(word_list, window=2):
    """构造在window下的单词组合，用来构造单词之间的边。
    Keyword arguments:
    word_list  --  list of str, 由单词组成的列表。
    windows    --  int, 窗口大小。
    """
    if window < 2: window = 2
    for x in range(1, window):
        if x >= len(word_list):
            break
        word_list2 = word_list[x:]
        #利用zip方法，yield生成一对词构成的边
        res = zip(word_list, word_list2)
        for r in res:
            yield r


import numpy as np
def get_asso_words(txt,stopwords, w , window=2, t=2 , s=0.5 , m=10):
    """获取关键词的主方法
    Keyword arguments:
    txt             --  txt文本的文件地址
    stopwords       --  停用词表的文件地址
    word            --  需要查询的关键词
    window          --  一个句子中相邻的window个单词，两两之间认为有边
    t               --  设置的转移步数
    s               --  设置的自转换概率
    m               --  想要获取的关联词个数
    
    """
    words=txtToWords(txt,stopwords)
    t_trans_mat = []
    result_words=[]
    #从词查下标的字典
    word_index = {}
    #从下标查词的字典
    index_word = {}
    words_number = 0
    
    #以下将把words列表中所有词统计到VSM（向量空间模型）中，并提供词到下标，下标到词两个字典方便后续查找。
    for word_list in words:
        for word in word_list:
            if not word in word_index:
                word_index[word] = words_number
                index_word[words_number] = word
                words_number += 1

    #以下根据每个词出现的位置信息建立无向权重图
    graph = np.zeros((words_number, words_number))
    w_index=word_index.get(w)
    #如果两个词出现在同一个句子中，符合窗口大小关系，则在它们之间建立一条边，并存入图中。
    for word_list in words:
        for w1, w2 in combine(word_list, window):
            if w1 in word_index and w2 in word_index:
                index1 = word_index[w1]
                index2 = word_index[w2]
                graph[index1][index2] += 1.0
                graph[index2][index1] += 1.0
                
    #下面根据前面得到的graph建立节点间的1步转换概率矩阵。
    trans_g=np.zeros((words_number, words_number))
    for i in range(words_number):
        sum_i=np.sum(graph[i])
        if(sum_i==0):
            sum_i=1
        trans_g[i][i]=s
        for j in range(words_number):
            if j!=i:
                trans_g[i][j]=(1-s)*(graph[i][j]/float(sum_i))
    trans_mat=np.mat(trans_g)
    #从1步转移概率矩阵邱t步转移概率矩阵
    t_trans_mat=trans_mat**t
    
    #在t步转移概率矩阵中获取前m个相关词的下标，然后在index_word字典中查到词，存入result_words中返回
    w_prob=np.array(t_trans_mat[w_index])
    w_prob_rank=np.argsort(-w_prob)
    import logging
    for i in range(m):
        try:
            result_words.append(index_word[w_prob_rank[0][i+1]])
        except Exception as e:
            print('文本中没有词语：'+w)
            logging.log(1,'文本中没有词语：'+w,e)
    return result_words


asso_result=get_asso_words('rdbg2019.txt','stopwords.txt','习近平',m=30)
for w in asso_result:
    print(w)



# Insert your code here. 
