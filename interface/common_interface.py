from db import models
from lib import common
from interface import user_interface
from server import use_data as da


def login(user_dic, conn):
    '''
    登录功能，登录成功，将用户信息以｛"addr":[session,user_id]｝的形式，放到内存中，
    多线程操作，必须加锁，锁需要在主线程中生成
    :param user_dic:
    :param conn:
    :return:
    '''
    user = models.User.select_one(name=user_dic['name'])
    if user:  # 用户存在
        if user.user_type == user_dic['user_type']:
            if user.password == user_dic['password']:
                session = common.get_uuid(user_dic['name'])
                da.mutex.acquire()
                if user_dic['addr'] in da.alive_user:
                    # 如果当前的客户端已经登录，再次登录的时候，把原来的用户踢出，再重新加入进去
                    da.alive_user.pop(user_dic['addr'])
                da.alive_user[user_dic['addr']] = [session, user.id]
                da.mutex.release()
                back_dic = {'flag': True, 'session': session, 'is_vip': user.is_vip, 'msg': 'login success'}
                if user_dic['user_type'] == 'user':
                    last_notice = user_interface.check_notice_by_count(1)
                    back_dic['last_notice'] = last_notice
            else:
                back_dic = {'flag': False, 'msg': 'password error'}
        else:
            back_dic = {'flag': False, 'msg': '登录类型不匹配'}
    else:
        back_dic = {'flag': False, 'msg': 'user do not exisit'}
    common.send_back(back_dic, conn)


def register(user_dic, conn):
    '''
    注册功能
    :param user_dic:
    :param conn:
    :return:
    '''
    user = models.User.select_one(name=user_dic['name'])
    if user:  # 用户存在
        back_dic = {'flag': False, 'msg': 'user is exisit'}
    else:
        user = models.User(name=user_dic['name'], password=user_dic['password'], user_type=user_dic['user_type'])
        user.save()
        back_dic = {'flag': True, 'msg': 'register success'}

    common.send_back(back_dic, conn)
