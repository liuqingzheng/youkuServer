import socket
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from threading import current_thread, Thread
from conf import setting
import struct
import json
from interface import common_interface, admin_interface, user_interface, login_user_data
import time

server_pool = ThreadPoolExecutor(2)
mutex = Lock()
dispatch_dic = {
    'login': common_interface.login,
    'register': common_interface.register,
    'upload': admin_interface.upload_movie,
    'delete_movie': admin_interface.delete_movie,
    'release_notice': admin_interface.release_notice,
    'buy_member': user_interface.buy_member,
    'get_movie_list': user_interface.get_movie_list,
    'check_notice': user_interface.check_notice,
    'check_download_record': user_interface.check_download_record,
    'check_movie':admin_interface.check_movie
}


def working(conn, addr):
    print(current_thread().getName())
    while True:
        try:
            head_struct = conn.recv(4)
            if not head_struct: break
            head_len = struct.unpack('i', head_struct)[0]
            head_json = conn.recv(head_len).decode('utf-8')
            head_dic = json.loads(head_json)
            # 分发之前，先判断是不是伪造
            head_dic['addr'] = addr[1]
            if head_dic['type'] == 'register' or head_dic['type'] == 'login':
                dispatch(head_dic, conn)
            else:
                for value in login_user_data.alive_user.values():
                    value[0] == head_dic['session']
                    head_dic['user_id'] = value[1]
                    break
                if head_dic.get('user_id', None):
                    dispatch(head_dic, conn)
                else:
                    back_dic = {'flag': False, 'msg': '您没有登录'}
                    send_back(back_dic,conn)
        except Exception as e:
            print(e)
            conn.close()
            # 把服务器保存的用户信息清掉
            mutex.acquire()
            if addr[1] in login_user_data.alive_user:
                login_user_data.alive_user.pop(addr[1])
            # print('***********end*************%s'%len(login_user_data.alive_user))
            mutex.release()

            print('客户端：%s :断开链接' % str(addr))
            break


def dispatch(head_dic, conn):
    if head_dic['type'] == 'login':  # 登录
        back_dic = common_interface.login(head_dic, mutex)
        send_back(back_dic, conn)
    elif head_dic['type'] == 'download_movie':  # 下载
        back_dic = user_interface.download_movie(head_dic)
        send_back(back_dic, conn)
        with open(back_dic['path'], 'rb')as f:
            for line in f:
                conn.send(line)

    elif head_dic['type'] == 'upload':  # 上传
        back_dic = admin_interface.upload_movie(head_dic, conn)
        send_back(back_dic, conn)
    else:
        if head_dic['type'] not in dispatch_dic:
            back_dic = {'flag': False, 'msg': '请求不存在'}
            send_back(back_dic, conn)
        else:
            back_dic = dispatch_dic[head_dic['type']](head_dic)
            send_back(back_dic, conn)


def send_back(back_dic, conn):
    head_json_bytes = json.dumps(back_dic).encode('utf-8')
    conn.send(struct.pack('i', len(head_json_bytes)))  # 先发报头的长度
    conn.send(head_json_bytes)


def server_run():
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.bind(setting.server_address)
    socket_server.listen(5)

    while True:
        conn, addr = socket_server.accept()
        print('客户端:%s 链接成功' % str(addr))
        server_pool.submit(working, conn, addr)

    socket_server.close()
