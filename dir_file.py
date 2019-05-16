import os


class DirFiles(object):

    def __init__(self, bak_path):
        self.bak = bak_path
        self.create_dirs(self.bak)

    # 目录检测
    @staticmethod
    def check_dir(path):
        return os.path.isdir(path)

    # 检测文件
    @staticmethod
    def check_file(path):
        return os.path.isfile(path)

    # 获取图片所在路径
    def get_dirname(self, path):
        dir_abs = os.path.dirname(path)
        dir_abs2 = os.path.join(self.bak.rstrip('/'), dir_abs.lstrip('/'))
        return dir_abs2

    @staticmethod
    def get_basename(path):
        return os.path.basename(path)

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

    @staticmethod
    def get_check_path(path, year_month):
        return os.path.join(path, year_month)

    def cp_img(self, filename, t):
        try:
            if self.check_file(filename) is False:
                return False

            file_dir = self.get_dirname(filename)
            des_dir = self.create_dirs(file_dir)
            file = self.get_basename(filename)
            des_file = os.path.join(des_dir, file)

            if os.path.exists(des_file) is True:
                des_file = os.path.join(des_dir, t + '_' + file)
            os.rename(filename, des_file)
        except Exception as e:
            print('cp_img error,', e, filename)
            return False
        else:
            return True

