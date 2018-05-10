from conf import setting
import pymysql


class Mysql:
    __instance = None
    def __init__(self):
        self.conn = pymysql.connect(host=setting.host,
                                    user=setting.user,
                                    password=setting.password,
                                    database=setting.database,
                                    charset=setting.charset,
                                    autocommit=setting.autocommit)
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def close_db(self):
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
        return affected

    @classmethod
    def singleton(cls):
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance
