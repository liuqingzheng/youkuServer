import hashlib
import time
import os


def get_uuid(name):
    md = hashlib.md5()
    md.update(name.encode('utf-8'))
    md.update(str(time.clock()).encode('utf-8'))
    return md.hexdigest()


def get_time():
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return now_time


def get_colck_time():
    return str(time.clock())


def get_bigfile_md5(file_path):
    if os.path.exists(file_path):
        md = hashlib.md5()
        filesize = os.path.getsize(file_path)
        file_list = [0, filesize // 3, (filesize // 3) * 2, filesize - 10]
        with open(file_path, 'rb') as f:
            for line in file_list:
                f.seek(line)
                md.update(f.read(10))
        return md.hexdigest()
