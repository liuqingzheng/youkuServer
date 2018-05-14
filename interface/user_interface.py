# 注册（用手机号注册，密码用md5加密）
# 登录（登录后显示最新一条公告）
# 冲会员
# 查看视频（即将所有视频循环打印出来）
# 下载普通视频（非会员下载视频需要等30s广告，会员下载无需等待）
# 下载收费视频（非会员下载需要10元，会员下载需要5元）
# 查看观影记录（就是查看自己下载过的视频）
# 查看公告（包括历史公告）
from db import models
import os
from lib import common


@common.login_auth
def buy_member(user_dic, conn):
    '''
    购买会员功能，直接将is_vip字段设为1
    :param user_dic:
    :param conn:
    :return:
    '''
    user = models.User.select_one(id=user_dic['user_id'])
    user.is_vip = 1
    user.update()
    back_dic = {'flag': True, 'msg': 'buy success'}
    common.send_back(back_dic, conn)


@common.login_auth
def get_movie_list(user_dic, conn):
    '''
    获取视频列表：取出全部视频，过滤掉删除的视频，根据前台传来的查询条件，把电影放到列表里
    :param user_dic:
    :param conn:
    :return:
    '''
    back_dic = {}
    movie_list = models.Movie.select_all()
    back_movie_list = []
    if movie_list:  # 不为空，继续查询，为空直接返回false
        for movie in movie_list:
            if not movie.is_delete:
                # 拼成一个列表['电影名字','收费/免费'，'电影id']
                if user_dic['movie_type'] == 'all':
                    # 全部
                    back_movie_list.append([movie.name, '免费' if movie.is_free else '收费', movie.id])
                elif user_dic['movie_type'] == 'free':
                    # 免费电影
                    if movie.is_free:  # 免费的才往列表里放
                        back_movie_list.append([movie.name, '免费', movie.id])
                else:
                    # 收费电影
                    if not movie.is_free:  # 收费的才往列表里放
                        back_movie_list.append([movie.name, '收费', movie.id])

        if back_movie_list:
            back_dic = {'flag': True, 'movie_list': back_movie_list}
        else:
            back_dic = {'flag': False, 'msg': '暂无可查看影片'}
    else:
        back_dic = {'flag': False, 'msg': '暂无影片'}
    common.send_back(back_dic, conn)


@common.login_auth
def download_movie(user_dic, conn):
    movie = models.Movie.select_one(id=user_dic['movie_id'])
    if not movie:  # 电影不存在，返回false
        back_dic = {'flag': False, 'msg': '该电影不存在'}
        common.send_back(back_dic, conn)
        return
    user = models.User.select_one(id=user_dic['user_id'])
    send_back_dic = {'flag': True}
    if user_dic['movie_type'] == 'free':  # 下载免费电影，非会员需要等待；下载收费电影，不需要等待了直接下
        if user.is_vip:
            send_back_dic['wait_time'] = 0
        else:
            send_back_dic['wait_time'] = 30

    send_back_dic['filename'] = movie.name
    send_back_dic['filesize'] = os.path.getsize(movie.path)
    # 把下载记录保存到记录表中
    down_record = models.DownloadRecord(user_id=user_dic['user_id'], movie_id=movie.id)
    down_record.save()
    common.send_back(send_back_dic, conn)
    with open(movie.path, 'rb')as f:
        for line in f:
            conn.send(line)


@common.login_auth
def check_notice(user_dic, conn):
    '''
    查看公告功能
    :param user_dic:
    :param conn:
    :return:
    '''
    # 直接调用通过条数查询的接口，传入None表示全查
    notice_list = check_notice_by_count(count=None)
    if notice_list:
        back_dic={'flag': True, 'notice_list': notice_list}
    else:
        back_dic={'flag': False, 'msg': '暂无公告'}

    common.send_back(back_dic, conn)


def check_notice_by_count(count=None):
    '''
    查看功能的方法，供内部调用
    count 为None，查全部，为1 查一条
    :param count:
    :return:
    '''
    notice_list = models.Notice.select_all()
    back_notice_list = []
    if notice_list:  # 不为空，继续查询，为空直接返回false
        if not count:
            for notice in notice_list:
                back_notice_list.append({notice.name: notice.content})
        else:  # 查一条
            last_row=len(notice_list)-1
            back_notice_list.append({notice_list[last_row].name: notice_list[last_row].content})
        return back_notice_list
    else:
        return False


@common.login_auth
def check_download_record(user_dic, conn):
    '''
    查看下载记录：
    先通过user_id到DownloadRecord表中查到下载的每一条记录，
    通过每一条记录中的电影id再去电影表查询电影，取出名字，返回
    :param user_dic:
    :return:
    '''
    download_record = models.DownloadRecord.select_all(user_id=user_dic['user_id'])
    if not download_record:
        back_dic = {'flag': False, 'msg': '暂无观影记录'}
        common.send_back(back_dic, conn)
    else:
        download_list = []
        for record in download_record:
            movie = models.Movie.select_one(id=record.movie_id)
            download_list.append(movie.name)
        back_dic = {'flag': True, 'msg': 'buy success', 'download_list': download_list}
        common.send_back(back_dic, conn)
