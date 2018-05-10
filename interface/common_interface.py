from db import models
from interface import login_user_data
from lib import common


def login(user_dic, mutex):
    user = models.User.select_one(name=user_dic['name'])
    if user:  # 用户存在
        if user.user_type == user_dic['user_type']:
            if user.password == user_dic['password']:
                session = common.get_uuid(user_dic['name'])
                mutex.acquire()
                if user_dic['addr'] in login_user_data.alive_user:
                    #如果当前的客户端已经登录，再次登录的时候，把原来的用户踢出，再重新加入进去
                    login_user_data.alive_user.pop(user_dic['addr'])
                login_user_data.alive_user[user_dic['addr']] = [session, user.id]
                mutex.release()

                # print(login_user_data.alive_user)
                # print(len(login_user_data.alive_user))
                back_dic = {'flag': True, 'session': session,'is_vip':user.is_vip, 'msg': 'login success'}
            else:
                back_dic = {'flag': False, 'msg': 'password error'}
        else:
            back_dic = {'flag': False, 'msg': '登录类型不匹配'}
    else:
        back_dic = {'flag': False, 'msg': 'user do not exisit'}
    return back_dic


def register(user_dic):
    user = models.User.select_one(name=user_dic['name'])
    if user:  # 用户存在
        back_dic = {'flag': False, 'msg': 'user is exisit'}
    else:
        user = models.User(name=user_dic['name'], password=user_dic['password'], user_type=user_dic['user_type'])
        user.save()
        back_dic = {'flag': True, 'msg': 'register success'}

    return back_dic
