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
        if not os.path.exists(path):
            os.mkdir(path)

        return path

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
        self.dt = datetime.datetime.now()
        super().check_path()

        # delete old files
        self.delete_old_files()

    def delete_old_files(self):
        """delete files with date > timedelta(days=4)"""

        for i in os.listdir(super().check_path()):
            try:
                if i.split('.')[-1] == 'txt':
                    count = datetime.datetime.now() \
                        - datetime.datetime.strptime(i.split('.')[0], '%d-%m-%y')

                    if count > datetime.timedelta(days=4):
                        os.remove(super().make_path(i))

            except (IndexError, ValueError):
                pass

    def write_error(self, head, text):
        """write traceback to file"""

        # make name
        file_name = self.dt.strftime('%d-%m-%y') + '.txt'

        path = super().make_path(file_name)

        # write log with error
        with open(path, 'a') as file:
            file.write('\n\n\n\n\n' + str(head) + '\n' + str(text))


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
