# -*- coding: utf-8 -*-
# @Time    : 2020-10-14
# @Author  : Jeffrey·Lau
# @FileName: brattxt2sequence_format.py
# @Software: PyCharm
# @Function: 将brat平台导出的txt（带标签）数据清洗转换至两列格式，可供模型训练
# @brat数据已经提前将ann标签加入txt

# <version> revised v2.0 修正了 tag格式 为类似 B-model

import os
import re
from pypinyin import lazy_pinyin, Style
from tqdm import tqdm


class Line:
    def __init__(self, line):
        self.line = line

    def get_tag(self, line=None):  # 给句子中单词打上标签
        # line = re.sub('')
        if line is None:
            line = self.line
        words = line.strip('\n').strip(' ').split(' ')
        words_tp = []
        tag_c = 0  # 当前word类型
        tag_m = 'O'  # 当前word隶属标签
        tag_me = ''  # 当前word标签前缀(BIES)等

        # 给word打上对应的标签mark以及标签后缀BIES
        for i in range(len(words)):
            word = words[i]
            mark_l = re.findall('^<[\u4E00-\u9FA5]+>', word.strip('\n')) #|a-z|A-Z
            mark_r = re.findall('^</[\u4E00-\u9FA5]+>', word.strip('\n')) #|a-z|A-Z
            # mark_l = re.findall('^<model>', word.strip('\n'))  # 只找出model标签 #####################################
            # mark_r = re.findall('^</model>', word.strip('\n')) # 只找出model标签 #####################################
            if mark_l:
                tag_m = mark_l[0][1:-1]
                tag_c = 1
                tag_me = ''
            elif mark_r:
                tag_m = 'O'
                tag_c = -1
                tag_me = ''
                if i != 0:
                    if words_tp[i - 1][1][0] == 'I':  # 本word为终止标签，前word标签前缀为I，说明为非一个word的内容，#则把前一个word的'I'改成'E'
                        words_tp[i - 1][1] = 'E' + words_tp[i - 1][1][1:]
                    else:  # 本word为终止标签，前word标签后缀为B，#则把前一个word的'B'改成'S'
                        words_tp[i - 1][1] = 'S' + words_tp[i - 1][1][1:]
            else:
                tag_c = 0
                if i != 0:
                    if words_tp[i - 1][1] != 'O':  # 判断为 <标签>内内容
                        # 判断为 <标签>内内容第一个word
                        if words_tp[i - 1][2] == 1:  # 前一个word的类型为1：起始标签，则该word为B
                            tag_me = 'B-'
                        else:
                            tag_me = 'I-'  # 前一个word的类型非1：起始标签，则该word为I
                    else:
                        tag_me = ''  # 标签外内容，标签后缀为空

            # 将中文标签转换为英文首字母 #####################################################################################################################
            tag_m_eng = ''.join(lazy_pinyin(tag_m, style=Style.FIRST_LETTER))  # 返回 汉字的首字母组成的列表，eg: 中国 -> ['z', 'g']
            words_tp.append([word, tag_me + tag_m_eng, tag_c])
            # words_tp.append([word, tag_me + tag_m, tag_c])

        line_marked = ['{}\t{}'.format(item[0], item[1]) 
                        for item in words_tp if item[2] == 0]  ###########去除句子中 <标签> </标签>
        return line_marked

    def clean_emmbed_tag(self):  # 清洗多重嵌入式标签中的内层标签
        words = self.line.strip('\n').strip(' ').split(' ')
        words_tp = []
        tag_c = 0  # index判别当前word类型（0普通1左标签-1右标签）
        tag_a = 0  # 累加前向tag_p值（辅助判断当前word位置：内容/嵌入式外围标签/嵌入式内层标签？）

        for word in words:
            if re.findall('^<[\u4E00-\u9FA5]+>', word.strip('\n')): #|a-z|A-Z
                tag_c = 1
            elif re.findall('^</[\u4E00-\u9FA5]+>', word.strip('\n')): #|a-z|A-Z
                tag_c = -1
            else:
                tag_c = 0
            tag_a += tag_c
            words_tp.append((word, tag_c, tag_a))
        line_cleaned_innermark = [item[0] for item in words_tp if
                                  not ((item[1] == 1 and item[2] > 1) or (item[1] == -1 and item[2] > 0))]  # 去除内部嵌套标签
        line = ' '.join(line_cleaned_innermark)
        return line

    def clean_get_tag(self):  # 执行 1先清洗get_tag();2后打标签clean_emmbed_tag() 操作
        line = self.clean_emmbed_tag()
        line_marked = self.get_tag(line)
        return line_marked


def trans_format(file,resultfile=None):
    if resultfile is None:
        resultfile = re.sub(r'\.[^\.]+$', '', file) + '_pro.txt'

    with open(file, 'rt', encoding='utf-8')as f:
        with open(resultfile, 'w', encoding='utf-8')as r:
            for line in tqdm(f.readlines()):
                if line.strip('\n')=='': #若为空行'B-ywzz','I-ywzz','E-ywzz','S-ywzz'，跳过
                    continue
                line = re.sub('\s*<',' <',line) # 将<标签左侧的多个空格或无空格变为1个
                line = re.sub('>\s*','> ',line) # 将>标签右侧的多个空格或无空格变为1个

                lineclass = Line(line)
                line_marked = lineclass.clean_get_tag() # 清洗嵌套标签
                r.writelines([word + '\n' for word in line_marked])
                r.write(' \n')


def KFold_txtmark(folder='data_merged', result_folder='data_reviesed'):
    from os.path import join
    
    for i in range(0,10):
        if not os.path.exists(join(result_folder,str(i))):
            os.makedirs(join(result_folder,str(i)))

        for file in os.listdir(join(folder,'data_'+str(i))):
            trans_format(join(folder,'data_'+str(i),file),join(result_folder,str(i),file))
            print(join(folder+os.sep+'data_'+str(i),file)+'转换完成~')


if __name__ == "__main__":
    # demo
    # trans_format(file='23985.txt')

    # 不十折交叉
    # trans_format(file='test_data.txt')
    # trans_format(file='train_data.txt')

    # 十折交叉
    # KFold_txtmark(folder='data_reviesed_merged')

    trans_format(file='jasist_merged_task1_2_2016.txt',resultfile='jasist_data_merged_BIES.txt')
