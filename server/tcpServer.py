import json
import socket
import struct
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from threading import current_thread

from conf import setting
from interface import common_interface, admin_interface, user_interface
from server import use_data

server_pool = ThreadPoolExecutor(10)
mutex = Lock()
use_data.mutex = mutex
dispatch_dic = {
    'login': common_interface.login,
    'register': common_interface.register,
    'upload': admin_interface.upload_movie,
    'delete_movie': admin_interface.delete_movie,
    'download_movie': user_interface.download_movie,
    'upload': admin_interface.upload_movie,
    'release_notice': admin_interface.release_notice,
    'buy_member': user_interface.buy_member,
    'get_movie_list': user_interface.get_movie_list,
    'check_notice': user_interface.check_notice,
    'check_download_record': user_interface.check_download_record,
    'check_movie': admin_interface.check_movie
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
            head_dic['addr'] = str(addr)

            dispatch(head_dic, conn)

        except Exception as e:
            print('错误信息：', e)
            conn.close()
            # 把服务器保存的用户信息清掉
            mutex.acquire()
            if str(addr) in use_data.alive_user:
                use_data.alive_user.pop(str(addr))
            # print('***********end*************%s'%len(login_user_data.alive_user))
            mutex.release()

            print('客户端：%s :断开链接' % str(addr))
            break


def dispatch(head_dic, conn):
    if head_dic['type'] not in dispatch_dic:
        back_dic = {'flag': False, 'msg': '请求不存在'}
        send_back(back_dic, conn)
    else:
        dispatch_dic[head_dic['type']](head_dic, conn)


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
