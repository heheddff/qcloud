#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qcloud_image import Client, CIFiles


class SDK(object):
    def __init__(self,appid, secret_id, secret_key, bucket=''):
        try:
            self.client = Client(appid, secret_id, secret_key, bucket)
            self.client.use_http()
            self.client.set_timeout(30)
        except Exception as e:
            print(e)

    def send(self, lists):
        try:
            res = self.client.porn_detect(CIFiles(lists))
            if 'httpcode' in res and res['httpcode'] == 200:  # 'httpcode': 200 为成功
                return res['result_list']
            else:
                return False
        except Exception as e:
            print(e)
            return False

