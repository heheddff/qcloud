#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

class Logs(object):
    def __init__(self, log_path):
        self.log_path = log_path

    def create_log_name(self, log_name):
        return os.path.join(self.log_path, log_name)

    def write_img(self, lists):
        new_lists = []

        f = open(self.write_img_log, 'a+')
        for path in lists:
            filename = os.path.basename(path)
            print(self.hot_lists)
            if filename in self.hot_lists:
                # print(filename)
                self.cp_img(path)
                continue

            if filename not in self.checked_lists:
                self.checked_lists.append(filename)
                new_lists.append(path)
                f.write(filename + '\n')
        f.close()
        return new_lists

    def write_img_hot(self, path):
        f = open(self.write_img_hot_log, 'a+')
        filename = os.path.basename(path)
        if filename not in self.hot_lists:
            self.hot_lists.append(filename)
            f.write(filename + '\n')
            f.close()

    def read_img_hot(self):
        if os.path.isfile(self.write_img_hot_log):
            with open(self.write_img_hot_log) as f:
                return f.read().split('\n')
        else:
            return []

    def read_img(self):
        if os.path.isfile(self.write_img_log):
            with open(self.write_img_log) as f:
                # print(set(f.read().split('\n')))
                return f.read().split('\n')
        else:
            # print(self.write_img_log)
            return []

    # 记录检测结果
    def write_res(self, res):
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            f = open(self.log_name, "a+")
            for line in res:
                if line['code'] != 0:
                    continue
                if line['data']['result'] == 0:
                    mes = "{0} {1} {2}\r\n".format(t, '否', line)
                else:
                    self.cp_img(line['filename'])
                    self.cp_img(line['filename'].replace('/v/', '/'))
                    self.weixin.send(line['filename'] + "\r\n")
                    mes = "{0} {1} {2}\r\n".format(t, '是', line)
                    self.write_img_hot(line['filename'])
                f.write(mes)
            f.close()
        except Exception as e:
            print('write', e)

    @staticmethod
    def read_log(log_name):
        with open(log_name) as f:
            # print(set(f.read().split('\n')))
            return f.read().split('\n')

    @staticmethod
    def write_log(log_name, message, t=None):
        with open(log_name, 'a+') as f:
            f.write(message + '\n')


