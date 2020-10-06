import pymysql


class Python2DB():
    def __init__(self):
        self.EF_DB = pymysql.connect(host='220.90.200.176',
                                port=3306,
                                user='multi',
                                passwd='multi!)@(',
                                db='EasyFree',
                                charset='utf8')

        # self.cursor = self.EF_DB.cursor()

    def select(self, table, column):
        self.cursor = self.EF_DB.cursor()
        sql_qr = """
            SELECT {0} FROM {1}
        """.format(column, table)
        self.cursor.execute(sql_qr)
        return self.cursor.fetchall()

    def insert(self, table, columns, values):
        self.cursor = self.EF_DB.cursor()
        sql_qr2 = """
            INSERT INTO {0}({1})
            VALUES ({2})
        """.format(table, columns, values)
        self.cursor.execute(sql_qr2)
        self.EF_DB.commit()

    def update(self, table, set_content, where_content):
        self.cursor = self.EF_DB.cursor()
        sql_qr3 = """
            UPDATE {0}
            SET {1}
            WHERE {2}
        """.format(table, set_content, where_content)
        self.cursor.execute(sql_qr3)
        self.EF_DB.commit()

    def delete(self, table, where_content):
        self.cursor = self.EF_DB.cursor()
        sql_qr4 = """
            DELETE FROM {0} WHERE {1}
        """.format(table, where_content)
        self.cursor.execute(sql_qr4)
        self.EF_DB.commit()