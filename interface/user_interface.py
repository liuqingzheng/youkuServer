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


def buy_member(user_dic):
    user = models.User.select_one(id=user_dic['user_id'])
    user.is_vip = 1
    user.update()
    back_dic = {'flag': True, 'msg': 'buy success'}
    return back_dic


def get_movie_list(user_dic):
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
            return {'flag': True, 'movie_list': back_movie_list}
        else:
            return {'flag': False, 'msg': '暂无可查看影片'}
    else:
        return {'flag': False, 'msg': '暂无影片'}


def download_movie(user_dic):
    movie = models.Movie.select_one(id=user_dic['movie_id'])
    if not movie:  # 电影不存在，返回false
        back_dic = {'flag': False, 'msg': '该电影不存在'}
        return back_dic
    user = models.User.select_one(id=user_dic['user_id'])
    send_back_dic = {'flag': True}
    if user_dic['movie_type'] == 'free':  # 下载免费电影，非会员需要等待；下载收费电影，不需要等待了直接下
        if user.is_vip:
            send_back_dic['wait_time'] = 0
        else:
            send_back_dic['wait_time'] = 30

    send_back_dic['filename'] = movie.name
    send_back_dic['filesize'] = os.path.getsize(movie.path)
    send_back_dic['path'] = movie.path
    # 把下载记录保存到记录表中
    down_record = models.DownloadRecord(user_id=user_dic['user_id'], movie_id=movie.id)
    down_record.save()
    return send_back_dic


def check_notice(user_dic):
    # 直接调用通过条数查询的接口，传入None表示全查
    return check_notice_by_count(count=None)


def check_notice_by_count(count=None):
    # count 为None，查全部，为1 查一条
    notice_list = models.Notice.select_all()
    back_notice_list = []
    if notice_list:  # 不为空，继续查询，为空直接返回false
        if not count:
            for notice in notice_list:
                back_notice_list.append({notice.name: notice.content})
        else:  # 查一条
            back_notice_list.append({notice_list[0].name: notice_list[0].content})
        return {'flag': True, 'notice_list': back_notice_list}
    else:
        return {'flag': False, 'msg': '暂无公告'}


def check_download_record(user_dic):
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
        return back_dic
    else:
        download_list = []
        for record in download_record:
            movie = models.Movie.select_one(id=record.movie_id)
            download_list.append(movie.name)
        back_dic = {'flag': True, 'msg': 'buy success', 'download_list': download_list}
        return back_dic
