import re
import os
# from Termwords import *
import shutil
from collections import defaultdict


class TaggedEntity:
    # 实体类
    entity_total_num = 0  # 实体数计数 

    def __init__(self, entity_type, start_pos, end_pos, entity_name):
        # 实体类，实体类型，开始位置，结束位置，实体名
        self.entity_type = entity_type
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.entity_name = entity_name

        # 构造实体序号
        TaggedEntity.entity_total_num += 1  # 总计数+1
        self.entity_id = 'T' + str(TaggedEntity.entity_total_num)


class Line:
    # 句子类
    total_len = 0  # 类全局变量，该文本中字符总长度
    partten_tag = re.compile(r'<.*?>')
    # 0428 统计一下术语词停用词情况
    termword_dic = defaultdict(int)  # 初始化词典

    def __init__(self, tagged_line):
        # 有标签的句子
        self.tagged_line = tagged_line

        # '引文作者', '引文时间', '术语', '引文的结果', '研究结果', '研究方法', '图', '表', '时间',
        #                  '数据源', '具体模型', '软件工具', '研究问题', '引文的研究问题', '引文的方法', '研究展望', '标准数据集',
        #                  '包含引用句', '自建数据集', '数学公式', '预标注术语'
        self.tag_dic = {
            'ywzz': '引文作者',
            'ywsj': '引文时间',
            'sy': '术语',
            'ywdjg': '引文的结果',
            'yjjg': '研究结果',
            'yjff': '研究方法',
            't': '图',
            'b': '表',
            'sj': '时间',
            'sjy': '数据源',
            'jtmx': '具体模型',
            'rjgj': '软件工具',
            'yjwt': '研究问题',
            'ywdyjwt': '引文的研究问题',
            'ywdff': '引文的方法',
            'yjzw': '研究展望',
            'bzsjj': '标准数据集',
            'bhyyj': '包含引用句',
            'zjsjj': '自建数据集',
            'sxgs': '数学公式',
            'ybzsy': '预标注术语',
        }

        # 实体标签 列表
        self.entity_list = []

        # 1）统计句子中出现的所有实体名，2）获得无标签的句子
        self.check_entities()

        # print("删除前"+self.ori_line)
        self.ori_line = self.kill_erro_tag(self.ori_line)  # 删除多余的错误标签
        # 最后 修改全局长度，加入无标签的句子长度
        # print("删除后" + self.ori_line)
        Line.total_len += len(self.ori_line) + 1

    def check_entities(self):
        '检查句子中是否有<标签>，如果有则加入统计，注意此处的难点是如何保证标签在无标签句子中的正确获取'
        if '<' in self.tagged_line:
            partten_name = re.compile(r'(?<=[zjygftbwsx]>)(.*?)(?=</)')  # 获得实体名称， 防止大于号的干扰
            partten_type_end = re.compile(r'</(.*?)>')  # 结束标签，如</model>
            partten_type_start = re.compile(r'<[^/]*?>')  # 开始标签，如<model>

            # print(partten_name)
            s = self.tagged_line  # 获取有标记的句子

            # 先获得结束类别标签的位置
            res_type_end = re.search(partten_type_end, s)

            while res_type_end:

                end_tag_end_pos = res_type_end.span()[1]  # 结束标签的结束位置
                s_buf = s[:end_tag_end_pos]  # 分割出一部分 
                entity_type = res_type_end.group(1)  # 获得实体类别
                # print(entity_type)
                res_name = re.search(partten_name, s_buf)  # 匹配实体名称
                # print(res_name)
                if res_name:
                    entity_name = res_name.group()  # 获得实体名称
                else:
                    s = self.tagged_line  # 本句有标签错误的情况，直接输出句子 20200417
                    break  # 结束while循环
                # print("测试：" + entity_name)
                res_type_start = re.search(partten_type_start, s_buf)  # 开始标签位置
                if res_type_start:
                    start_tag_start_pos = res_type_start.span()[0]  # 开始标签的开始位置
                else:
                    start_tag_start_pos = end_tag_end_pos - 1  # 确实标签，这里记录为-1  20200417
                entity_start_pos = start_tag_start_pos  # 实体开始位置更新、
                # entity_name = self.kill_erro_tag(entity_name)  # 删除多余的错误标签
                entity_end_pos = len(s[:start_tag_start_pos] + entity_name)  # 实体结束位置更新

                s = s[:start_tag_start_pos] + entity_name + s[end_tag_end_pos:]  # 拼接一个新的字符串 

                # print(entity_type, entity_start_pos, entity_end_pos, entity_name)  # 实体类别，开始，结束，实体名称
                # print(s)  # 修改后的句子

                # 导入到我们的实体列表中
                if entity_type in self.tag_dic:
                    self.entity_list.append(TaggedEntity(self.tag_dic[entity_type], Line.total_len + entity_start_pos,
                                                         Line.total_len + entity_end_pos, entity_name))

                res_type_end = re.search(partten_type_end, s)

            self.ori_line = s  # 去除标签后是无标签的的ori_line 
        else:
            self.ori_line = self.tagged_line  # 没有标签，直接原样输出即可

    def kill_erro_tag(self, s):
        '删除多余标签'
        return re.sub(Line.partten_tag, '', s)


def read_in(path):
    with open(path, 'r', encoding='utf-8') as fr:
        lines = fr.readlines()
    step = 100  # 每100个句子分一个段落
    lines_split_130 = [lines[i:i + step] for i in range(0, len(lines), step)]
    return lines_split_130


def write_termwords_frq(path):
    # 20200428 写入统计结果
    with open(path, 'w', encoding='utf-8') as fw:
        results = sorted(Line.termword_dic.items(), key=lambda x: x[1], reverse=True)
        for res in results:
            fw.write('{0}\t{1}\n'.format(res[0], res[1]))


def run(user, dp, paths, root_path):
    for path in paths:
        # 1 读入文件
        lines_split = read_in(dp + path)
        # root_path = './jasist_demo_20200428/'
        # print(lines_split)

        # 2 处理文件
        fw_path = root_path + '{0}/{1}_'.format(user, path)
        # print(fw_path)
        if not os.path.exists(root_path + '{0}/'.format(user)):
            os.makedirs(root_path + '{0}/'.format(user))
            # shutil.copytree('./conf/', root_path + '{0}/'.format(user))
        count_lines_split = 1
        for lines in lines_split:
            # 取块
            for line in lines:
                # print(Line.total_len)
                line_checked = Line(line)  # 获得句子类，完成句子的清洗
                # 存入ann
                with open(fw_path + str(count_lines_split) + '.ann', 'a', encoding='utf-8') as fw:
                    for te in line_checked.entity_list:
                        fw.write(
                            '{0}\t{1} {2} {3}\t{4}\n'.format(te.entity_id, te.entity_type, te.start_pos, te.end_pos,
                                                             te.entity_name))
                        # 坑，注意这个输出格式 有\t 还有空格

                # 存入txt
                with open(fw_path + str(count_lines_split) + '.txt', 'a', encoding='utf-8') as fw:
                    fw.write(line_checked.ori_line)

            count_lines_split += 1  # 块+1
            Line.total_len = 0  # 全局变量归零

        #  结束
        print(user, '构建完成')


def main():
    # 用户集，可以直接用你配置中的用户名密码词典
    # 结果生成以用户名命名的文件夹
    USER_PASSWORD = {
        'test': 'test',
        '1': '1',
        '2': '2',
        '3': '3',
    }
    users = USER_PASSWORD.keys()

    # 文档集
    root_path = './output/'  # 输出的结果文件位置
    if os.path.exists(root_path):
        shutil.rmtree(root_path)
    os.mkdir(root_path)  # 自动清空数据集，并新建

    # print(root_path)
    dataset_path =r'C:\Users\13284\Desktop\jasist_task1-relation\jasist_task1-relation-20210531\sqj2\\'  # 需要分割的文档集
    files = os.listdir(dataset_path)
    print(files)
    n = 0
    step = 1000
    m = n + step

    # 为每个用户分配文档
    for user in users:
        paths = files[n:m]
        run(user, dataset_path, paths, root_path)
        # 下一集合
        n += step
        m += step


def demo_main():
    # 一个简单样例
    run('', './data/', ['test.txt'], root_path=r'C:\Users\13284\Desktop\jasist_task1-relation\jasist_task1-relation-20210531\fyt')


if __name__ == "__main__":
    main()
    #demo_main()
