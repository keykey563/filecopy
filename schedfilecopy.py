# coding:utf-8

import os
import shutil
import time
import sched
import logging
import logging.handlers
import configparser


class FileCopy:
    def __init__(self):
        # 备份原地址
        self.src_file_path = ''
        # 备份目标地址
        self.dst_file_path = ''
        # 备份文件总数量
        self.total_num = 0
        # 备份成功文件数量
        self.copy_num = 0
        # 备份失败文件数量
        self.fail_num = 0
        # 备份失败路径
        self.fail_files = []
        self.init_logger()
        self.schedule = sched.scheduler(time.time, time.sleep)

    def init_config(self):
        """
            初始化配置参数
        :return:
        """
        conf = configparser.ConfigParser()
        conf.read("config.properties", encoding='utf-8')
        try:
            self.src_file_path = conf.get('file_path', 'src_path')
            self.dst_file_path = conf.get('file_path', 'dest_path')
            self.log_info("读取到备份路径：{}".format(self.src_file_path))
            self.log_info("读取到备份目标路径：{}".format(self.dst_file_path))
        except Exception as er:
            self.log_error("未读取到配置文件或配置参数，请检查配置！！！", er)
            raise Exception()

    def init_logger(self):
        """
            初始化打印日志对象
        :return:
        """
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        LOG_FILE_MAX_SIZE = 1 * 1024 * 1024
        fh = logging.handlers.RotatingFileHandler("info.log", maxBytes=LOG_FILE_MAX_SIZE, backupCount=2,
                                                  encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s %(process)-6d %(levelname)-8s %(message)s')
        fh.setFormatter(formatter)
        # add the handlers to logger
        logger.addHandler(fh)

    def run_method(self):
        """
            执行备份
        :return:
        """
        self.log_info("备份操作 ------------- Start ------------------")
        start = time.time()
        try:
            self.copy_opt(self.src_file_path, os.path.basename(self.src_file_path))
        except Exception as e:
            test.log_error("运行异常", e)
        end = time.time()
        self.log_info("---------------------------------")
        self.log_info("\t运行时间:{}s".format("{:.2f}".format((end - start))))
        self.log_info("\t扫描文件数量:{}".format(self.total_num))
        self.log_info("\t增量备份文件数量:{}".format(self.copy_num))
        if self.fail_num > 0:
            self.log_info("\t备份失败文件数量:{}".format(self.fail_num))
            self.log_info("\t备份失败文件列表:{}".format(self.fail_files))
        self.log_info("---------------------------------")
        self.log_info("备份操作 ------------- End --------------------")

    def copy_opt(self, file_path, cur_file_name):
        """
            备份操作主函数，递归调用
        :param file_path:       文件路径
        :param cur_file_name:   当前文件名称
        :return:
        """
        self.log_info("------------------------------------")
        self.log_info("遍历目录下的文件，当前文件路径:{}".format(file_path))
        file_list = os.listdir(file_path)
        for file_name in file_list:
            if os.path.isdir(file_path + "/" + file_name):
                # 如果当前路径为目录，则需要递归遍历该目录下的文件
                self.copy_opt(file_path + "/" + file_name, cur_file_name + "/" + file_name)
            else:
                # 当前路径为文件，则执行复制操作
                self.total_num += 1
                self.copy_file(file_path, cur_file_name, file_name)

    def copy_file(self, file_path, dir_path, file_name):
        """
            复制文件主函数
        :param file_path:   文件路径
        :param dir_path:    目录路径
        :param file_name:   文件名称
        :return:
        """
        self.log_info("执行文件复制操作，文件路径:{}，目录名称:{}，文件名称:{}".format(file_path, dir_path, file_name))
        dst_path = self.dst_file_path + "/" + dir_path
        cur_file_path = dst_path + "/" + file_name
        flag = True

        try:
            if os.path.lexists(dst_path) is False:
                # 路径不存在，级联创建目录
                self.mkdir(dst_path)

            # 判断当前文件是否存在
            if os.path.exists(cur_file_path):
                # 获取该文件的最后修改日期，来判断是否复制该文件
                dst_file_last_edit_times = os.path.getmtime(cur_file_path)
                src_file_last_edit_times = os.path.getmtime(file_path + "/" + file_name)
                self.log_info("已存在文件--{}".format(file_name))
                if src_file_last_edit_times <= dst_file_last_edit_times:
                    flag = False
            if flag is True:
                shutil.copyfile(file_path + "/" + file_name, cur_file_path)
                # 复制文件状态信息，包括文件权限位、最后访问时间、最后修改时间等
                shutil.copystat(file_path + "/" + file_name, cur_file_path)
                self.copy_num += 1
        except IOError as e:
            self.log_info("----文件复制过程异常，文件名为:{}".format(cur_file_path))
            self.log_info(e)
            # 将该文件记录到异常中
            self.fail_num += 1
            self.fail_files.append(cur_file_path)

    def mkdir(self, file_path):
        """
            递归创建多级目录
        :param file_path:
        :return:
        """
        self.log_info("创建目录：{}".format(file_path))
        if not os.path.isdir(file_path):
            self.mkdir(os.path.split(file_path)[0])
        else:
            return
        os.mkdir(file_path)

    def log_info(self, msg):
        """
            打印INFO级别日志
        :param msg: 提示信息
        :return:
        """
        print(msg)
        logging.info(msg)

    def log_error(self, msg, error):
        """
            打印ERROR级别日志
        :param msg:     提示信息
        :param error:   错误信息
        :return:
        """
        print(msg)
        logging.error(msg)
        logging.error(error)

    def execute_cmd(self, cmd, inc):
        """
            触发执行主函数
        :return:
        """
        os.system(cmd)
        self.schedule.enter(inc, 0, self.execute_cmd, (cmd, inc))

    def sched_execute(self, cmd, inc=60):
        """
            周期性任务调度
        :param cmd: 执行名称
        :param inc: 间隔时间，默认1分钟
        :return:
        """
        # enter四个参数分别为：间隔时间、优先级（当同时间到达的两个事件同时执行时定序）、被调用触发的函数、给该触发函数的参数（tuple形式）
        self.schedule.enter(0, 0, self.execute_cmd, (cmd, inc))
        self.schedule.run()


if __name__ == "__main__":
    test = FileCopy()
    try:
        test.init_config()
        test.run_method()
    except Exception as error:
        test.log_error("运行异常", error)
    # test.sched_execute("netstat -ano | findstr 3306", 5)
