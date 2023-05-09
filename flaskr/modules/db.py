import pymysql

def connection():
    connection = pymysql.connect(host='',
                                user='',
                                password='',
                                database='',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection