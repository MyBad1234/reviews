import os
import json
import pathlib
import platform
import datetime

def errorLog(text):
    file = open(file="errors.log", mode="a+", encoding="utf-8")
    file.write(str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))+": "+text+"\n")
    file.close()

def parseLog(text):
    file = open(file="parse.log", mode="a+", encoding="utf-8")
    file.write(str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))+": "+text+"\n")
    file.close()


class FileUtils:
    """some functions for work with files"""

    def check_path(self):
        """control files_info in file system"""

        path = str(pathlib.Path(__file__).parent.parent)

        # control path by platform
        if platform.system() == 'Windows':
            path += '\\files_info\\'
        else:
            path += '/files_info/'

        # create temp
        if os.path.exists(path):
            os.mkdir(path)

    def make_path(self, file_name):
        """make path with filename"""

        path = str(pathlib.Path(__file__).parent.parent)

        # control path by platform
        if platform.system() == 'Windows':
            path += '\\files_info\\'
        else:
            path += '/files_info/'

        return path + file_name


class ErrorClass(FileUtils):
    """work with errors"""

    def __init__(self):
        super().check_path()

    def write_error(self, file_name, text):
        """write traceback to file"""

        path = super().make_path(file_name + '.txt')

        # write log with error
        with open(path, 'w') as file:
            file.write(text)


class LastWork(FileUtils):
    """class for checking last work of reviews"""

    def __init__(self):
        self.dt = datetime.datetime.now()
        super().check_path()

    def write_statistic(self):
        """write last update"""

        path = super().make_path('STATISTIC_REVIEWS.json')

        with open(path, 'w') as file:
            file.write(json.dumps({
                'use': False,
                'last_update': datetime.datetime.now().strftime('%d.%m.%y %H:%M')
            }, indent=4))
