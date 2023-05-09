from pymysql.err import MySQLError
from ..modules import db
from datetime import datetime

class Log():
    def __init__(self):
        self.conn = db.connection()
        self.show_row_cnt = 5
        self.day = 30
        self.table = "log"

    def connect(self):
        if not self.conn.open:
            self.conn.connect()

    def getDetail(self, rack, position, page):
        self.connect()
        l = int(page) * self.show_row_cnt
        sql = """
        SELECT
            *
        FROM {}
        WHERE rack = %s AND position = %s
        ORDER BY date_insert DESC
        LIMIT %s, %s
        """.format(self.table)
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, (rack, position, l, self.show_row_cnt))
                    result = cursor.fetchall()
                    return result
                except Exception as e:
                    print(e)
                    return "error"

    def totalCount(self, rack, position):
        self.connect()

        sql = """
        SELECT
            COUNT(*) AS total
        FROM {}
        WHERE rack = %s 
            AND position = %s
        """.format(self.table)
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, (rack, position))
                    result = cursor.fetchone()
                    return result
                except MySQLError as e:
                    print(e)
                    return "error"
    
    def insert(self, data):
        col = ", ".join(["{} = %s".format(x) for x in data.keys()])
        val = tuple(data.values())
        sql = """
        INSERT INTO log SET {}
        """.format(col)
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, val)
                    self.conn.commit()
                    result = "success"
                    return result
                except MySQLError as e:
                    print(e) 
                    return "error"
