# 用单例版
# from orm.fuckorm import Model, StringField, IntegerField


# 用池版
from ormpool.fuckorm_pool import Model, StringField, IntegerField


class User(Model):
    table_name = 'userinfo'
    id = IntegerField('id', primary_key=True)
    name = StringField('name')
    password = StringField('password')
    locked = IntegerField('locked', default=0)
    is_vip= IntegerField('is_vip',default=0)
    user_type = StringField('user_type')


class Movie(Model):
    table_name = 'movie'
    id = IntegerField('id', primary_key=True)
    name = StringField('name')
    path = StringField('path')
    is_free = IntegerField('is_free',default=1)
    is_delete = IntegerField('is_delete',default=0)
    create_time = StringField('create_time')
    user_id = IntegerField('user_id')
    file_md5=StringField('file_md5')


class Notice(Model):
    table_name = 'notice'
    id = IntegerField('id', primary_key=True)
    name = StringField('name')
    content = StringField('content')
    user_id = IntegerField('user_id')
    create_time = StringField('create_time')


class DownloadRecord(Model):
    table_name = 'download_record'
    id = IntegerField('id', primary_key=True)
    user_id = IntegerField('user_id')
    movie_id = IntegerField('movie_id')
