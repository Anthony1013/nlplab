# coding=utf-8
# zihe.zhu@qq.com
# step1
# 根据非空ann文件生成标注文件
"""
    1. 从后往前标注的策略
    2. 合并同一篇章的文献，因为之前按照130行同一篇章进行了切割。
    3. 合并好的txt文件，放在同一个文件夹中，**以doi号命名文件** 
    4. 这个程序使用了多线程，跑之前需要注释掉第51 59 137 138行，再运行第二遍，取消这些注释。
"""
import os
from collections import defaultdict
from Logger import *
import threading
import time
import shutil


# 首先设置mod
mod = 'jasist_task2'

# 文件夹删除更新
save_path = f'./tagged_files/{mod}/'  # 存储文件夹名称
if os.path.exists(save_path):
    shutil.rmtree(save_path)
os.makedirs(save_path)

if os.path.exists(f'./tagged_files/{mod}标注统计结果.txt'):
    os.remove(f'./tagged_files/{mod}标注统计结果.txt')
log = Logger(f'./tagged_files/{mod}标注统计结果.txt', level='info').logger
threadLock = threading.Lock()


class AnnTermTagger(threading.Thread):
    """
        根据ann文件构建标注器
    """
    tag_dic = defaultdict(int)
    tagger_logger_tagged = defaultdict(int)
    tagger_logger_total = defaultdict(int)

    def __init__(self, ann_file, f, d, mod):
        super(AnnTermTagger, self).__init__()
        self.f = f
        self.tagger_name = d  # 标注人
        # self.sleep_time = int(f[-7])                 #原为self.sleep_time = int(f[-5])
        self.ann_file = ann_file
        self.txt_file = ann_file[:-3]+'txt'  
        self.doi = self.get_doi()
        self.ann_tags = self.load_tags()  

    def run(self):
        # time.sleep(self.sleep_time*3)
        threadLock.acquire()  # 上锁
        AnnTermTagger.tagger_logger_total[self.tagger_name] += 1
        if self.ann_tags:
            self.tag_file()
            log.info(f"{self.ann_file}\t实体数：{len(self.ann_tags)}")
            AnnTermTagger.tagger_logger_tagged[self.tagger_name] += 1
        else:
            log.info(f"{self.ann_file}\t暂未标注")
        threadLock.release()
    
    def get_doi(self):
        # 获取doi
        if '10.1002' in self.f:
            return self.f[12:17]
        else:
            return self.f[:-4]                               #原为return self.f[:5]
    
    def load_tags(self):
        # 因为存在嵌套标注的情况，所以此处我们对标注内容进行去重，排序处理，长的排在前面。
        def get_details(t):
            # 以空格切分“研究问题 709 854”
            blocks = t.split()
            try:
                entity_name,s_p,e_p=blocks[0],int(blocks[1]),int(blocks[-1])
                return {"entity_name":entity_name, "s_p":s_p,"e_p": e_p }
            except:
                return None
            # return {"entity_name":blocks[0], "s_p":int(blocks[1]),"e_p": int(blocks[-1]) }

        with open(self.ann_file, 'r', encoding='utf-8') as fr:
            lines = fr.readlines()
            if lines:
                terms = [[get_details(line.split('\t')[1]), line.split('\t')[2].strip()] for line in lines if len(line.split('\t'))==3 and get_details(line.split('\t')[1])]
                return list(sorted(terms, key=lambda x: x[0]["s_p"], reverse=True))  # tricks：从后往前标，不用计算每次插入的长度就能保证准确
            else:
                return None
    
    def tag_file(self):
        # 根据标签开始标注txt
        def super_replace(content, tag):
            # 根据tag进行标注，采取局部替换的策略
            entity_tag = tag[0]["entity_name"]
            AnnTermTagger.tag_dic[tag[0]["entity_name"]] += 1  # 顺便，记录标签数
            s_p = int(tag[0]["s_p"])
            e_p = int(tag[0]["e_p"])
            buf_con = f"<{entity_tag}> {tag[1]} </{entity_tag}>"
            return content[:s_p] + content[s_p:e_p+1].replace(tag[1],buf_con) + content[e_p+1:]

        fr = open(self.txt_file, 'r', encoding='utf-8')
        content = fr.read().replace('\n', '\n\r')
        for tag in self.ann_tags:
            content = super_replace(content, tag)
        # 标注完毕，写入吧。
        #  判断文件夹是否存在，存在先删除，然后新建。
        
        with open(f'{save_path}{self.doi}.txt','a+',encoding='utf-8') as fa:
            fa.write(content.replace('\n\r', '\n'))  # 替换回去

    @staticmethod
    def cal_total_tags():
        # 输出各个标注者完成情况， 输出标签规律
        ft1 = "{0}\t{1}"
        log.info(ft1.format('标注者', '标注进度'))
        for name in AnnTermTagger.tagger_logger_tagged:
            progress_bar = str(AnnTermTagger.tagger_logger_tagged[name])+'/'+str(AnnTermTagger.tagger_logger_total[name])
            log.info(ft1.format(name, progress_bar))
        log.info('*'*20)

        log.info(ft1.format('标签类别', '总个数'))
        res = sorted(AnnTermTagger.tag_dic.items(), key=lambda x:x[1], reverse=True) 
        for t in res:
            log.info(ft1.format(t[0], t[1]))


if __name__ == "__main__":
    # root_path = f'./tagdata/{mod}/'  # brat标注好的语料
    root_path = f'{mod}/'
    dirs = os.listdir(root_path)
    if '.stats_cache' in dirs:
        dirs.remove('.stats_cache')
    for d in dirs:
        buf_path = root_path+d
        # buf_path = root_path
        
        [AnnTermTagger(buf_path + '/' + f, f, d, mod).start() for f in os.listdir(buf_path) if f.endswith(('.ann'))]
    
    # 统计标签情况：
    #   先把下面的注释，跑完一遍再跑
    # time.sleep(10)  # 手动等待多线程结束
    # AnnTermTagger.cal_total_tags()  # 输出标签分布规律
