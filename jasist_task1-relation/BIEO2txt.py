#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
"""
@Time:2021-04-12 19:27
@Author:Veigar
@File: BIEO2txt.py
@Github:https://github.com/veigaran
"""
import codecs
from itertools import groupby

"""
1、完成BIEO格式的txt转为正常带标签句子的txt
2、因原始文件为总文件，需进行切分，其中#开头表示一个txt
3、对每一个txt，若句子行数大于130，则再次进行切分
"""


# 词转为句子
def word2sentence(word_list):
    word_list = list((s.split('\t') for s in word_list))
    line = ''
    for item in word_list:
        index = word_list.index(item)
        if item[0] == "#" and item[2][0] == "B":
            item[2] = "O"
            line += item[0] + " "
            word_list[index + 1][2] = "B" + word_list[index + 1][2][1:]  # 若出现标签首行为#则强制转为下一个单词为起始位置
        else:
            if item[2] == "O":
                line += item[0] + " "
            elif item[2][0] == "B":  # 若下一个单词错误标记为O、B、S，则更改为S类型
                if word_list[index + 1][2] == ("O" or "S" or "B"):
                    line += "<" + item[2][2:] + ">" + item[0] + "</" + item[2][2:] + ">" + " "
                else:  #
                    line += "<" + item[2][2:] + ">" + item[0] + " "
            elif item[2][0] == "I":  # 若上一个或下一个单词错误标记为O、S，则更改为S类型
                if word_list[index + 1][2] == ("O" or "S") or word_list[index - 1][2] == ("O" or "S" or "E"):
                    line += "<" + item[2][2:] + ">" + item[0] + "</" + item[2][2:] + ">" + " "
                else:
                    line += item[0] + " "
            elif item[2][0] == "E":  # 若上一个单词错误标记为O、E、S，则更改为S类型
                if word_list[index - 1][2] == ("O" or "S" or "E"):
                    line += "<" + item[2][2:] + ">" + item[0] + "</" + item[2][2:] + ">" + " "
                else:
                    line += item[0] + "</" + item[2][2:] + ">" + " "
            elif item[2][0] == "S":
                line += "<" + item[2][2:] + ">" + item[0] + "</" + item[2][2:] + ">" + " "
    return line


# 列表按数量n等分
def clip_list(a, c):  # a为原列表，c为等分长度
    clip_back = []
    if len(a) > c:
        for i in range(int(len(a) / c)):
            # print(i)
            clip_a = a[c * i:c * (i + 1)]
            clip_back.append(clip_a)
            # print(clip_a)
        # last 剩下的单独为一组
        last = a[int(len(a) / c) * c:]
        if last:
            clip_back.append(last)
    else:  # 如果切分长度不小于原列表长度，那么直接返回原列表
        clip_back = a

    return clip_back


# 写入数据到txt
def write_txt(out_path, sentences):
    # 输出模式是“a”即在原始文本上继续追加文本
    with codecs.open(out_path, "a", "utf") as f:
        for sentence in sentences:
            f.write(sentence + '\n')


def main():
    path = r'F:\PostGraduated\0.数据校对\2-数据转换\data\4.模型预测结果\bert-base\labed_output.txt'
    output = r'F:\PostGraduated\0.数据校对\2-数据转换\data\output'
    result = []
    # 读取原始BIEOS标记的txt文件，读取后格式为：['the\tO\tO','','',.....'','','']
    with open(path, 'r', encoding='utf') as f:
        for line in f:
            result.append(line.strip('\n'))
    # print(result)

    line_list = []
    txt_list = []
    # 不同的句子之间中间有‘’分割，经处理后，得到一个[[句子1],[句子2],[].....]，其中[句子1]格式为['the\tO\tO','','',.....'','','']
    res1 = [list(g) for k, g in groupby(result, lambda x: x == '') if
            not k]
    # print(res1)
    # 遍历总列表，将每个子列表去除标签，转为正常的含<>的句子，得到的结果为['句子1','句子2',''......]
    for item in res1:
        line_list.append(word2sentence(item))
    # print(line_list)
    # 将上方列表转为字符串形式
    total_line = "\n".join(line_list)
    # print(total_line)
    # 上述处理后仍然为一个总文件，因此根据'\n#'切分为不同的部分，也即不同的txt文件，此时txt_string格式为['txt1','txt2','',......]
    txt_string = total_line.split('\n#')
    # print("------")
    # print(txt_string)
    # 因需对大于130的txt划分，为了方便统计长度，对于列表内的每个txt再次转为列表，保存到txt_list中，格式为：[[txt1],[txt2],[],.....]
    # 每个txt的格式为：['句子1','句子2','',......]
    for txt in txt_string:
        txt_list.append(txt.split('\n'))
    # print(txt_list)

    # 遍历总列表
    for index in range(len(txt_list)):
        print(index)
        outPath = output + '\\' + str(index) + '.txt'
        write_txt(outPath, txt_list[index])
        # if len(txt_list[index]) > 130:  #对长度大于130的进行切分
        #     temp = clip_list(txt_list[index], 130)
        #     for i in range(len(temp)):
        #         outPath = output + '\\' + str(index+21186) + "_" + str(i) + '.txt'
        #         write_txt(outPath, temp[i])
        # else:
        #     outPath = output + '\\' + str(index+21186) + '.txt'
        #     write_txt(outPath, txt_list[index])


if __name__ == '__main__':
    main()
