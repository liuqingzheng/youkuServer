import hashlib
import os
import time
import json
import struct

def login_auth(func):
    def wrapper(*args, **kwargs):
        from server import use_data as mu
        for value in mu.alive_user.values():
            if value[0] == args[0]['session']:
                args[0]['user_id'] = value[1]
                break
        if not args[0].get('user_id', None):
            send_back({'flag': False, 'msg': '您没有登录'}, args[1])
        else:
            return func(*args, **kwargs)

    return wrapper


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


def send_back(back_dic, conn):

    head_json_bytes = json.dumps(back_dic).encode('utf-8')
    conn.send(struct.pack('i', len(head_json_bytes)))  # 先发报头的长度
    conn.send(head_json_bytes)
