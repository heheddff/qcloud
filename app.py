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
import os
import time
import sys
from config import config
from qcloud_image import Client, CIFiles
import re
'''
# 这里支持传入多个需要鉴别的本地图片地址
res = client.porn_detect(CIFiles(['./img/11.jpg',]))['result_list'][0]['data']

'''


class Dirs(object):
	log_name = 'temp.log'  # 临时日志

	def __init__(self, path=None):
		self.path = path if path else config['path']
		self.baks = config['bak']
		self.logs = config['log']
		self.appid = config['appid']
		self.start = self.match_date(config['start'])
		self.end = self.match_date(config['end'])
		self.current_month = config['current_month']
		self.count = config['count']
		self.write_img_log = os.path.join(self.logs,time.strftime("%Y%m", time.localtime())+'_checked.log')
		self.checked_lists = self.read_img()
		self.secret_id = config['secret_id']
		self.secret_key = config['secret_key']
		self.bucket = ''
		self.create_dirs(self.baks)
		self.create_dirs(self.logs)
		self.client = self.core()
		# print(config)
		# print(self.path)
		# print(self.baks)
		# print(self.logs)

	# 创建sdk
	def core(self):
		try:
			client = Client(self.appid, self.secret_id, self.secret_key, self.bucket)
			client.use_http()
			client.set_timeout(30)
		except Exception as e:
			print(e)
			return False
		else:
			return client

	# 目录检测
	@staticmethod
	def check_dir(path):
		return os.path.isdir(path)

	# 获取图片所在路径
	def get_dirname(self, path):
		dir_abs = os.path.dirname(path)
		dir_abs2 = os.path.join(self.baks.rstrip('/'), dir_abs.lstrip('/'))
		return dir_abs2

	# 依据可疑图片创建对应路径
	def create_dirs(self, path):
		try:
			if self.check_dir(path) is False:
				os.makedirs(path)
				print(path, 'is create')
			else:
				print(path, 'is exists')
		except Exception as e:
			print(e)
			return False
		else:
			return path

	# 获取待检测图片
	@staticmethod
	def walk_dir(dir_path):
		lists = []
		print("开始对以下目录进行检测:", dir_path)

		if os.path.isdir(dir_path):
			for root, dirs, files in os.walk(dir_path, topdown=False):
				for name in files:
					filename = os.path.join(root, name)
					lists.append(filename)
			return lists

	# 开始图片鉴别
	def check_img(self, lists=None):
		if self.client is False:
			return

		if lists:
			length = len(lists)
			print(length)

			num = length // self.count + 2  # 保证所有图片都能被检测
			for j in range(1, num):
				start = (j - 1) * self.count
				end = j * self.count
				wait_lists = self.write_img(lists[start:end])

				if len(wait_lists) == 0:
					continue

				try:
					res = self.client.porn_detect(CIFiles(wait_lists))

					if 'httpcode' in res and res['httpcode'] == 200:  # 'httpcode': 200 为成功
						self.write_res(res['result_list'])
				except Exception as e:
					print('error', e)
					continue
				# time.sleep(0.3)

	def write_img(self, lists):
		new_lists = []

		f = open(self.write_img_log, 'a+')
		for path in lists:
			filename = os.path.basename(path)
			if filename not in self.checked_lists:
				self.checked_lists.append(filename)
				new_lists.append(path)
				f.write(filename+'\n')
		f.close()
		return new_lists

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
					mes = "{0} {1} {2}\r\n".format(t, '是', line)

				f.write(mes)
			f.close()
		except Exception as e:
			print('write', e)

	# 移动可疑图片
	def cp_img(self, filename):
		try:
			if os.path.isfile(filename) is False:
				return False

			file_dir = self.get_dirname(filename)
			des_dir = self.create_dirs(file_dir)
			file = os.path.basename(filename)
			des_file = os.path.join(des_dir, file)

			if os.path.exists(des_file) is False:
				os.rename(filename, des_file)
		except Exception as e:
			print('cp_img error,', e, filename)
			return False
		else:
			return True

	# 生成指定日期目录，已废弃
	@staticmethod
	def create_date(year=None, month=None):
		if year is None:
			year = time.strftime("%Y", time.localtime())
		if month is None:
			month = time.strftime("%m", time.localtime())

		year_month = year + month
		return year_month

	# 检测输入日期是否正常,已废弃
	@staticmethod
	def check_inputs(inputs):

		print("你输入的日期是：", " ".join(inputs))
		year = None
		month = None

		if len(inputs) == 1 and len(inputs[0]) == 4:
			year = inputs[0]
		elif len(inputs) == 2 and len(inputs[0]) == 4 and len(inputs[1]) == 2:
			year = inputs[0]
			month = inputs[1]
		elif len(inputs) == 2 and len(inputs[0]) == 2 and len(inputs[1]) == 4:
			year = inputs[1]
			month = inputs[0]
		return year, month

	#  匹配给定的日期格式
	@staticmethod
	def match_date(date=None):
		pattern = r'\d{2,4},\d{1,2}'
		pattern1 = r'\.'
		res = re.match(pattern, re.sub(pattern1, ',', date))
		if res:
			return res.group(0)
		else:
			return res

	# 参数式获取
	def sys_year_month(self):
		try:
			inputs = sys.argv[1:]
			if len(inputs) == 2:
				start = self.match_date(inputs[0])
				end = self.match_date(inputs[1])
				return self.check_start_end(start, end)
			else:
				return False
		except Exception as e:
			print('sys param error', e)
			return False

	# 获取开始日期，结束日期,优先级:配置文件<参数式<交互式
	def get_start_end(self):
		sys_year_month = self.sys_year_month()
		if sys_year_month:
			self.start, self.end = sys_year_month
		'''
		input_year_month = self.input_year_month()
		if input_year_month:
			self.start, self.end = input_year_month
		'''
		return self.create_date_by_start_end(self.start, self.end)

	@staticmethod
	def create_date_by_start_end(start_date, end_date):
		year_month = []
		try:
			start_year, start_month = eval(start_date)
			end_year, end_month = eval(end_date)
		except Exception as e:
			print(e)
			return False
		else:
			if start_year <= end_year:
				years = end_year - start_year
				months = years * 12 + (end_month - start_month)
				for i in range(months + 1):
					if start_month < 10:
						year_month.append((str(start_year), '0' + str(start_month)))
					else:
						year_month.append((str(start_year), str(start_month)))

					start_month += 1

					if start_month == 13:
						start_year += 1
						start_month = 1
				return year_month
			else:
				print("起始日期不能大于结束日期")
				return False

	# 检测是否同时输入开始日期和结束日期
	@staticmethod
	def check_start_end(start=None, end=None):
		if start and end:
			return start, end
		else:
			return False

	# 交互式输入
	def input_year_month(self):
		try:
			start = input("请输入起始年月,如 2019，05:")
			end = input("请输入起始年月,如 2019，05:")

			start = self.match_date(start)
			end = self.match_date(end)

			return self.check_start_end(start, end)
		except Exception as e:
			print('参数输入有误，请按给定格式重新输入', e)
			return False

	# 主程序
	def main(self):
		if self.current_month == 1:
			year_months = [time.strftime("%Y%m", time.localtime())]
		else:
			year_months = self.get_start_end()
			print(year_months)

		if year_months is False or len(year_months) == 0:
			return

		for path in self.path:
			for year_month in year_months:
				self.log_name = os.path.join(self.logs, ''.join(year_month) + '.log')
				if os.path.isdir(os.path.join(path,''.join(year_month))):
					check_path = os.path.join(path, ''.join(year_month))
				else:
					check_path = os.path.join(path, '/'.join(year_month))
				# print(check_path)

				lists = self.walk_dir(check_path)
				self.check_img(lists)


dirs = Dirs()
dirs.main()

