# -*- coding: utf-8 -*-
# @Time    : 2021-04-10
# @Author  : Jeffrey·Lau
# @FileName: 3.1_notag2sequence_format.py
# @Function: 将未标注的文件转换为序列格式

import os
from os import listdir
from os.path import join
import codecs
import re
import pandas as pd

import threading
import time
from Logger import Logger
log=Logger(filename='log.txt',level='info').logger
# from pypinyin import lazy_pinyin, Style
from tqdm import tqdm


def get_txt_path(folder):
    return [join(folder,f) for f in listdir(folder)]


def txt2seq(file, dst_folder, lineword_folder):
    line_word=[] # 记录文章每行的次数
    with codecs.open(file,'r',encoding='utf8')as f:
        with codecs.open(join(dst_folder,os.path.split(file)[-1]),'w',encoding='utf8')as r:
            doi_identity=re.search('\d{5}',os.path.split(file)[-1]).group(0)
            r.write('###'+doi_identity+'DOI\tO\n') # 增加文章识别号在每个文章序列开头
            for line in tqdm(f.readlines()):
                words = line.strip('\n').strip('\r').split(' ')
                r.writelines(['{}\tO\n'.format(word) for word in words])
                r.write('\n')
                line_word.append(len(words))
    pd.Series(data=line_word,index=None,name=doi_identity).to_csv('{}/{}_lineword.csv'.format(lineword_folder, doi_identity))


class Txt2seq_Thread(threading.Thread):
    def __init__(self, file, dst_folder, lineword_folder):
        threading.Thread.__init__(self)
        self.file=file
        self.dst_folder=dst_folder
        self.lineword_folder=lineword_folder
          
    def run(self):
        txt2seq(self.file, self.dst_folder,self.lineword_folder)


def main(n_thread=10): #默认开启30线程
    dst_folder='3.1jasist_notag_seq'
    lineword_folder='3.1jasist_notag_lineword'
    for f in [dst_folder,lineword_folder]:
        if not os.path.exists(f):
            os.makedirs(f)
    txt_path=get_txt_path(folder='3.0jasist_notag_baseon_task1#2#2016')

    start_time=time.time()
    T=[]
    for i, path in enumerate(txt_path):
        # 30个线程一组，结束后进入下一组进程
        if i%n_thread==0 and i!=0:
            for t in T:
                t.join() # 等待t进程结束
            T=[]
        
        t=Txt2seq_Thread(path,dst_folder,lineword_folder)
        t.start()
        T.append(t)

    end_time = time.time()
    use_time=end_time-start_time
    log.info(str(n_thread)+'\t'+str(use_time))


if __name__=='__main__':
    # from random import randint
    # for n in range(11,16):
    #     main(n)
    #     time.sleep(randint(1,5))
    
    main(10)

