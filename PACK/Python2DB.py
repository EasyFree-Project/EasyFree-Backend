import pymysql

EF_DB = pymysql.connect(host='220.90.200.176',
                        port=3306,
                        user='multi',
                        passwd='multi!)@(',
                        db='EasyFree',
                        charset='utf8')

# cursor = EF_DB.cursor()

def select(table, column):
    cursor = EF_DB.cursor()
    sql_qr = """
        SELECT {0} FROM {1}
    """.format(column, table)
    cursor.execute(sql_qr)
    return cursor.fetchall()

def insert(table, columns, values):
    cursor = EF_DB.cursor()
    sql_qr2 = """
        INSERT INTO {0}({1})
        VALUES ({2})
    """.format(table, columns, values)
    cursor.execute(sql_qr2)
    EF_DB.commit()

def update(table, set_content, where_content):
    cursor = EF_DB.cursor()
    sql_qr3 = """
        UPDATE {0}
        SET {1}
        WHERE {2}
    """.format(table, set_content, where_content)
    cursor.execute(sql_qr3)
    EF_DB.commit()

def delete(table, where_content):
    cursor = EF_DB.cursor()
    sql_qr4 = """
        DELETE FROM {0} WHERE {1}
    """.format(table, where_content)
    cursor.execute(sql_qr4)
    EF_DB.commit()