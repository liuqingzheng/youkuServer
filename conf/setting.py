import os

host = '127.0.0.1'
port = 3306
user = 'root'
password = '123456'
database = 'youku2'
charset = 'utf8'
autocommit = True

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DB = os.path.join(BASE_DIR, 'db')
BASE_MOVIE = os.path.join(BASE_DIR, 'movie')
BASE_MOVIE_LIST = os.path.join(BASE_DIR, 'movie_list')
server_address = ('127.0.0.1', 8083)
