from conf import setting
import os
from lib import common
from db import models


def upload_movie(user_dic, conn):
    recv_size = 0
    print('----->', user_dic['file_name'])
    file_name = common.get_time() + user_dic['file_name']
    path = os.path.join(setting.BASE_MOVIE_LIST, file_name)
    with open(path, 'wb') as f:
        while recv_size < user_dic['file_size']:
            recv_data = conn.recv(1024)
            f.write(recv_data)
            recv_size += len(recv_data)
            # print('recvsize:%s filesize:%s' % (recv_size, user_dic['file_size']))
    print('%s :上传成功' % file_name)
    movie = models.Movie(name=file_name, path=path, is_free=user_dic['is_free'],
                         user_id=user_dic['user_id'], file_md5=user_dic['file_md5'])
    movie.save()
    back_dic = {'flag': True, 'msg': '上传成功'}
    return back_dic


def delete_movie(user_dic):
    movie = models.Movie.select_one(id=user_dic['movie_id'])
    movie.is_delete = 1
    movie.update()
    back_dic = {'flag': True, 'msg': '电影删除成功'}
    return back_dic


def release_notice(user_dic):
    notice = models.Notice(name=user_dic['notice_name'], content=user_dic['notice_content'],
                           user_id=user_dic['user_id'])
    notice.save()
    back_dic = {'flag': True, 'msg': '公告发布成功'}
    return back_dic


def check_movie(user_dic):
    movie = models.Movie.select_one(file_md5=user_dic['file_md5'])
    if movie:
        back_dic = {'flag': False, 'msg': '该电影已经存在'}
    else:
        back_dic = {'flag': True}
    return back_dic
