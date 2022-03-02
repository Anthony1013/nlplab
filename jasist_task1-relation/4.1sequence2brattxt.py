'''
Author: your name
Date: 2021-01-30 21:39:33
LastEditTime: 2021-01-31 17:40:34
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /bert_ner-master/sequence2brattxt.py
'''
# -*- coding: utf-8 -*-
# @Time    : 2021-01
# @Author  : Jeffrey·Lau
# 将模型训练结果序列格式转换为带标签的txt格式
import os
import pandas as pd
from tqdm import tqdm
from pypinyin import lazy_pinyin, Style


def tag():
    tag_list = open('conf/tag.txt', 'rt', encoding='utf-8').readlines()
    tag_dic = {}
    for tag in tag_list:
        tag_eng = ''.join(lazy_pinyin(tag, style=Style.FIRST_LETTER)).strip('\n')  # 返回 汉字的首字母组成的列表，eg: 中国 -> ['z', 'g']
        tag_dic[tag_eng] = tag.strip('\n')
    return tag_dic


def read_txt_length(file):
    df = pd.read_excel(file, header=0, index_col=0)
    return df


def trans_sequence(labed_txt, txt_length_df, result_folder):
    if not os.path.exists(result_folder):
        os.mkdir(result_folder)
    elif os.listdir(result_folder):
        print('文件夹内已有内容！')
        return  # 已有文件夹

    tag_dic = tag()

    with open(labed_txt, 'rt', encoding='utf-8')as labelf:
        line_result = ''  # 转换成带标签txt后每行的内容string
        line_result_length = 0  # 转换成带标签的txt后每行的内容string
        has_sep = 0
        for index, row in tqdm(txt_length_df.iterrows()):
            txt_filename = row[0]
            txt_length = row[1]
            '''此处手动设置第一次出现[SEP]标签所在的文献x，其行的数目的变动.
            （由于改行词数超过510导致换行，以及后续空行与SEP CLS的混乱)'''
            if txt_filename == '10.1002#asi.22811.txt':
                txt_length -= 3  # 第一次先跑一遍代码，观察该文件多了几行。
            count_extra_line = 0  # 记录 文献x多出的行数目
            ''''''

            writen_txt_length = 0
            while writen_txt_length < txt_length:
                with open('{}/{}'.format(result_folder, txt_filename), 'a+', encoding='utf-8')as rf:
                    line = labelf.readline()

                    if len(line.split('\t')) == 3 and line.split('\t')[0] != '':
                        content = line.split('\t')[0]  # 每行标签的单词
                        label = line.split('\t')[2].strip('\n')  # 标签
                        if content == '[SEP]':
                            writen_txt_length += 1
                            line_result = line_result.strip(' ') + '\n'
                            rf.write(line_result)
                            line_result = ''
                            line_result_length = 0
                            # if count_extra_line!=0:
                            #     txt_length+=count_extra_line
                            #     count_extra_line=0
                            has_sep = 1
                        elif content == '[CLS]':
                            continue
                        elif label == 'O':
                            # rf.write(content+' ')
                            line_result += content + ' '
                            line_result_length += 1
                        else:
                            if len(label.split('-')) == 2:
                                label_c = label.split('-')[0]  # 标签类型
                                lable_l = label.split('-')[1]  # 标签位置类型 BIMS
                            ## 标签若为[SEP]则维持上一轮的标签
                            chn_label = tag_dic[label_c]
                            if lable_l == 'S':
                                line_result += '<{0}> {1} </{0}> '.format(chn_label, content)
                                line_result_length += 1
                            elif lable_l == 'B':
                                line_result += '<{0}> {1} '.format(chn_label, content)
                                line_result_length += 1
                            elif lable_l == 'I':
                                line_result_length += 1
                                line_result += content + ' '
                            elif lable_l == 'E':
                                line_result += '{1} </{0}> '.format(chn_label, content)
                                line_result_length += 1

                        '''
                            len(line.split('\t'))!=3 and line.split('\t')[0]=''
                            '\tO\tO\n'       （空值\tO\tO)
                        '''
                    elif len(line.split('\t')) != 3 and line.split('\t')[0] == '':
                        continue
                        '''
                            len(line.split('\t'))!=3
                            ''              （空行）
                        '''
                    elif len(line.split('\t')) != 3:
                        if has_sep == 0:  # 在出现[SEP]前，将label.txt中的空行认定为txt中的换行
                            writen_txt_length += 1
                            # rf.write('\n')
                            line_result = line_result.strip(' ') + '\n'
                            rf.write(line_result)
                            line_result = ''

                            if line_result_length >= 510:  # 若某行有510个词，加上[SEP]、[CLS],共512个词。则后续开始标记乱行。
                                print('{}\t{}\t'.format(txt_filename, txt_length))
                                count_extra_line += 1
                            elif count_extra_line - 1 != 0:  # 记录从出现超出512开始到出现[SEP]之前，文献x多出的行数
                                count_extra_line += 1
                            line_result_length = 0

                        else:  # 某行出现[SEP]后，之后label.txt中的空行不再认为是txt中的换行。
                            continue
            # print('{}/{}写入完成！'.format(result_folder,txt_filename))


def main():
    df = read_txt_length(file='doi_length.xlsx')
    trans_sequence(labed_txt='label_predictsh_20210130.txt', txt_length_df=df, result_folder='marked_txt_20210131')


if __name__ == "__main__":
    main()

# 22811.txt中开始出现问题分句。前面的所有txt无问题，后面的所有txt全部有断句问题。
# 22811.txt中第115行过长，训练预测结果中自动换行，以至于按照空行匹配后line115变为line115-130行。
# 从此之后的空行换行均错乱。需要参照[SEP]  [CLS]换行。
