import time
import sys
import re


class YearMonth(object):
    # 生成指定日期目录，已废弃
    def __init__(self, start, end):
        self.start = self.match_date(start)
        self.end = self.match_date(end)

    # 获取当前年月
    @staticmethod
    def create_date(year=None, month=None, status=None):
        if year is None:
            year = time.strftime("%Y", time.localtime())
        if month is None:
            month = time.strftime("%m", time.localtime())

        if status:
            year_month = year + month
            return year_month

        return year, month

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

    @staticmethod
    def get_current_time():
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

