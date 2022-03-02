# coding=utf-8
# author: dl.zihezhu@gmail.com
# datetime:2020/7/4 19:36

"""
程序说明：
   Logger类
    实现记录异常的堆栈信息，以及输出信息
"""
import logging
from logging import handlers


class Logger:
    # 参考代码来源：https://www.cnblogs.com/nancyzhu/p/8551506.html
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, filename='log.txt', level='info', when='W0', back_count=10,
                 fmt='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别

        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        self.logger.addHandler(sh)  # 把对象加到logger里

        # 往文件里写入 #指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=back_count,
                                               encoding='utf-8')
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(th)


if __name__ == '__main__':
    log = Logger('log.log', level='info').logger  # 使用方法，首先，实现一个log类
    log.debug('debug')
    log.info('info')
    log.warning('警告')
    log.error('报错')
    log.critical('严重')
    Logger('error.log', level='error').logger.error('error')
