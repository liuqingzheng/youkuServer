import pymysql
from ormpool import db_pool
from threading import current_thread


class MysqlPool:
    def __init__(self):
        self.conn = db_pool.POOL.connection()
        print(db_pool.POOL)
        # print(current_thread().getName(), '拿到连接', self.conn)
        # print(current_thread().getName(), '池子里目前有', db_pool.POOL._idle_cache, '\r\n')
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def close_db(self):
        self.cursor.close()
        self.conn.close()

    def select(self, sql, args=None):
        self.cursor.execute(sql, args)
        rs = self.cursor.fetchall()
        return rs

    def execute(self, sql, args):

        try:
            self.cursor.execute(sql, args)
            affected = self.cursor.rowcount
            # self.conn.commit()
        except BaseException as e:
            print(e)
        finally:
            self.close_db()
        return affected
