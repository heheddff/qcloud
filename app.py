#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
鉴黄图片
其中返回字段数据代表的意义如下:
result: 供参考的识别结果，0正常，1黄图，2疑似图片
confidence: 识别为黄图的置信度，范围0-100；是normal_score, hot_score, porn_score的综合评分
normal_score: 图片为正常图片的评分
hot_score: 图片为性感图片的评分
porn_score: 图片为色情图片的评分
forbid_status: 封禁状态，0表示正常，1表示图片已被封禁（只有存储在万象优图的图片才会被封禁）
"""

from config import config
from weixin import WeiXin

from date import YearMonth
from dir_file import DirFiles
from logs import Logs
from sdk import SDK
import os
import time
'''
# 这里支持传入多个需要鉴别的本地图片地址
res = client.porn_detect(CIFiles(['./img/11.jpg',]))['result_list'][0]['data']

'''


class Dirs(object):
	log_name = 'temp.log'  # 临时日志

	def __init__(self, path=None):
		self.path = path if path else config['path']
		self.bak_path = config['bak']
		self.log_path = config['log']
		self.dir_files = DirFiles(self.bak_path)
		self.logs = Logs(self.log_path)
		self.dir_files.create_dirs(self.log_path)

		self.year_month = YearMonth(config['start'], config['end'])
		self.current_month = config['current_month']

		self.count = config['count']
		self.disable_date = config['disable_date']
		# log
		self.write_img_log = self.dir_files.get_check_path(self.logs.log_path, self.year_month.create_date(status=1)+'_checked.log')
		self.write_img_hot_log = self.dir_files.get_check_path(self.logs.log_path, 'hot.log')

		self.checked_lists = self.logs.read_log(self.write_img_log) if self.dir_files.check_file(self.write_img_log) else []
		self.hot_lists = self.logs.read_log(self.write_img_hot_log) if self.dir_files.check_file(self.write_img_hot_log) else []

		# 鉴黄sdk
		self.appid = config['appid']
		self.secret_id = config['secret_id']
		self.secret_key = config['secret_key']
		self.sdk = SDK(self.appid, self.secret_id, self.secret_key)

		# 企业微信
		self.weixin = WeiXin(
			corpid=config['weixin']['corpid'],
			secrect=config['weixin']['secrect'],
			agentid=config['weixin']['agentid'],
			touser=config['weixin']['touser'],
			product=config['product']
		)

	def filter_wait_check_img(self, path):
		filename = self.dir_files.get_basename(path)
		t = self.year_month.get_current_time()
		if filename in self.hot_lists:
			self.dir_files.cp_img(path,t)
			return False

		if filename not in self.checked_lists:
			self.checked_lists.append(filename)
			self.logs.write_log(self.write_img_log, filename)
			return True

	# 开始图片鉴别
	def check_img(self, lists=None):

		length = len(lists) if lists else 0
		if length == 0:
			return

		print(length)
		num = length // self.count + 2  # 保证所有图片都能被检测
		for j in range(1, num):
			start = (j - 1) * self.count
			end = j * self.count
			wait_lists = list(filter(self.filter_wait_check_img, lists[start:end]))
			print(wait_lists)
			if len(wait_lists) == 0:
				continue

			res = self.sdk.send(wait_lists)
			if res is False:
				continue
			self.process_http_result(res)

	# 分析处理检测结果
	def process_http_result(self, res):
		try:
			for line in res:
				if line['code'] != 0:
					continue
				t = self.year_month.get_current_time()
				if line['data']['result'] == 0:
					mes = "{0} {1} {2}".format(t, '否', line)
				else:
					mes = "{0} {1} {2}".format(t, '是', line)
					self.dir_files.cp_img(line['filename'], t)
					self.dir_files.cp_img(line['filename'].replace('/v/', '/'), t)

					self.weixin.send(line['filename'] + "\r\n")
					# 鉴别为黄图单独写入文件
					self.logs.write_log(self.write_img_hot_log, self.dir_files.get_basename(line['filename']))

				self.logs.write_log(self.log_name, mes)
		except Exception as e:
			print('error', e)

	# 主程序
	def main(self):

		if self.disable_date == 1:
			current_year_month = self.year_month.create_date(status=1)
			self.log_name = self.logs.create_log_name(current_year_month + '.log')
			print(self.log_name)

			for path in self.path:
				lists = self.dir_files.walk_dir(path)
				self.check_img(lists)
		else:

			if self.current_month == 1:
				year_months = [self.year_month.create_date()]
			else:
				year_months = self.year_month.get_start_end()
				print(year_months)

			if year_months is False or len(year_months) == 0:
				return

			for path in self.path:
				for year_month in year_months:
					self.log_name = self.logs.create_log_name(''.join(year_month) + '.log')
					check_path = self.dir_files.get_check_path(path,''.join(year_month))

					if self.dir_files.check_dir(check_path) is False:
						check_path = self.dir_files.get_check_path(path, '/'.join(year_month))

					lists = self.dir_files.walk_dir(check_path)
					#print(lists)
					self.check_img(lists)


dirs = Dirs()
dirs.main()

