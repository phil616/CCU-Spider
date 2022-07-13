import pymysql
import json
from global_kits import Logger


class SqlServer(object):
    MYSQL_HOST = ""
    MYSQL_USER = ""
    MYSQL_PASSWORD = ""
    MYSQL_DATABASE = ""
    MYSQL_CHARSET = ""
    conn = None
    cursor = None
    __insert_call = 0

    def __init__(self, config_path):
        conf = json.load(open(config_path, 'r', encoding='utf8'))
        self.MYSQL_HOST = conf['mysql']['hostname']
        self.MYSQL_USER = conf['mysql']['user']
        self.MYSQL_PASSWORD = conf['mysql']['passwd']
        self.MYSQL_DATABASE = conf['mysql']['database']
        conn = pymysql.connect(host=self.MYSQL_HOST,
                               user=self.MYSQL_USER,
                               password=self.MYSQL_PASSWORD,
                               database=self.MYSQL_DATABASE,
                               autocommit=True)
        conn.ping()
        self.conn = conn
        self.cursor = conn.cursor()

    def test_conn(self):
        try:
            self.conn.ping()
        except Exception as e:
            print(e)
            self.conn = pymysql.connect(
                host=self.MYSQL_HOST,
                user=self.MYSQL_USER,
                password=self.MYSQL_PASSWORD,
                database=self.MYSQL_DATABASE,
                charset=self.MYSQL_CHARSET,
                autocommit=True)
            self.cursor = self.conn.cursor()

    def sql_post(self, sql):
        self.test_conn()
        try:
            self.cursor.execute(sql)
        except Exception as e:
            log_info = " *sql_post S SQL " + str(e) + str(sql)
            Logger.warning(log_info)
        else:
            self.__insert_call += 1
            Logger.info(" *sql_post No. " + str(self.__insert_call) + " Insert Success " + str(sql))
        return self.__insert_call
