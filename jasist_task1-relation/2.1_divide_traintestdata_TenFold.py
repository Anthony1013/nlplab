# <author> Jeffrey·Lau 20200728
# <version> 3.0 -20210203
# <version> 4.0 -20210406

import os
from os.path import join
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split


def data_merge(folder, merged_txt='data_merged.txt'):
    ''' 将多个txt的数据合并 '''
    if type(folder)==list: # 若folder为list，则汇总合并多个文件夹内所有文件的path
        paths = []
        [paths.extend(join(folder_i,f) for f in os.listdir(folder_i)) for folder_i in folder]    
    else:
        paths = [join(folder,f) for f in os.listdir(folder)]

    with open(merged_txt,'w+',encoding='utf-8')as dmf:
        for p in tqdm(paths):
            with open(p,'rt',encoding='utf-8')as pf:
                dmf.writelines(pf.readlines())


def load_data(filepaths=None, datafile=None):
    ''' 加载文件夹内所有数据 '''
    if filepaths is None:
        filepaths = [datafile]
    data = []
    [data.extend(open(path, 'rt', encoding='utf-8').readlines()) for path in filepaths]
    # random.shuffle(data)
    return data


def train_test_divide(data):
    ''' 读取数据文件并划分为训练集、测试集 '''
    # random.shuffle(data)
    train_data, test_data = train_test_split(data, test_size=0.1)

    with open('train_data.txt', 'w+', encoding='utf-8')as tr:
        tr.write('\n'.join(train_data))
    with open('test_data.txt', 'w+', encoding='utf-8')as te:
        te.write('\n'.join(test_data))
    return train_data, test_data


def kfold(data, outputfolder='data'):
    ''' 十折交叉验证划分数据训练集、测试集 '''
    [os.makedirs(outputfolder+os.sep+'data_{}'.format(i)) for i in range(10) if not os.path.exists(outputfolder + os.sep + 'data_{}'.format(i))]

    kf = KFold(n_splits=10, shuffle=False) # shuffle 是否打乱数据
    k = 0
    for train_index, test_index in kf.split(data): # kf.split()的结果是索引
        train_list = [data[tr].strip('\r\n') for tr in train_index]
        test_list = [data[te].strip('\r\n') for te in test_index]
        with open(outputfolder + os.sep + 'data_' + str(k) + os.sep + 'train.tsv', 'w+', encoding='utf-8')as tr:
            tr.write('\n'.join(train_list))
        with open(outputfolder + os.sep+ 'data_' + str(k) + os.sep + 'test.tsv', 'w+', encoding='utf-8')as te:
            te.write('\n'.join(test_list))
        # pd.DataFrame(train_list).to_csv(outputfolder + os.sep + 'data_' + str(k) + os.sep + 'train.tsv', index=False,
        #                                  header=False, sep='\t')
        # pd.DataFrame(test_list).to_csv(outputfolder + os.sep+ 'data_' + str(k) + os.sep + 'test.tsv', index=False, 
        #                                  header=False, sep='\t')
        k += 1
        print('第{}折完成！'.format(k))


if __name__ == '__main__':
    task_folder = ['jasist_task1-relation-20210531']
    tagged_folders = [join('tagged_files',task) for task in task_folder]
    data_merge(tagged_folders, merged_txt='jasist_merged_task1_2_2016.txt')
