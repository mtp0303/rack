from pymysql.err import MySQLError
from ..modules import db, err
from datetime import datetime

class Room():
    def __init__(self, idx = None):
        self.idx = idx
        self.conn = db.connection()
        self.err = err.Err()
        self.log_table = datetime.today().strftime("LOG_%Y%m")
    
    #DB 연결상태 확인후 끊어져 있을 경우 다시 연결
    def connect(self):
        if not self.conn.open:
            self.conn.connect()

    #모든 room data 가져오기
    def getAll(self):
        self.connect()
        sql = "SELECT idx, title FROM room ORDER BY ord IS NULL, ord, title"
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    return result
                except MySQLError as e:
                    err_code = e.args[0]
                    err = self.err.print(err_code)
                    return err

    def getOne(self):
        sql = """
        SELECT
	        *
        FROM room AS RM
        LEFT JOIN department AS D
        ON RM.department_code = D.code
        WHERE idx = %s
        """
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, (self.idx))
                    result = cursor.fetchone()
                    return result
                except Exception as e:
                    print(e)
                    return "fail"
        
    def set(self, data):
        col = ", ".join(["{} = %s".format(x) for x in data.keys()])
        val = tuple(data.values())
        sql = """
        INSERT INTO room
        SET {}
        """.format(col)
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, val)
                    self.conn.commit()
                    return str(cursor.lastrowid)
                except MySQLError as e:
                    err_code = e.args[0]
                    err = self.err.print(err_code)
                    return err

    def delete(self):
        self.connect()
        sql = "DELETE FROM room WHERE idx = %s"
        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (self.idx))
                self.conn.commit()
                return "삭제되었습니다"
    
    def update(self, data):
        col = ", ".join(["{} = %s".format(k, v) for k, v in data.items()])
        val = tuple(data.values())
        sql = """
        UPDATE room SET {}
        WHERE idx = {}
        """.format(col, self.idx)
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, val)
                    self.conn.commit()
                    return "success"
                except MySQLError as e:
                    err_code = e.args[0]
                    err = self.err.print(err_code)
                    return err

    def deleteRow(self, r):
        self.connect()
        sql = """
        DELETE FROM rack WHERE room_idx = %s AND `row` = %s
        """
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, (self.idx, r))
                    self.conn.commit()
                    return "삭제되었습니다"
                except Exception as e:
                    return "error: {}".format(e)
    
    def deleteContainer(self, r, c):
        self.connect()
        sql = """
        DELETE FROM rack WHERE room_idx = %s AND `row` = %s AND col = %s
        """
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, (self.idx, r, c))
                    self.conn.commit()  
                    return "삭제되었습니다"
                except Exception as e:
                    return "error: {}".format(e)

    def getMax(self):
        self.connect()
        sql = """
        SELECT 
            `row`, col, max(ord) AS ord 
        FROM rack 
        WHERE room_idx = %s 
        GROUP BY `row`, col
        """
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, (self.idx))
                    result = cursor.fetchall()
                    return result
                except Exception as e:
                    return "error: {}".format(e)


            