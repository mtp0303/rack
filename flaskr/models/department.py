
from pymysql.err import MySQLError
from ..modules import db
from decimal import Decimal
from datetime import datetime

class Department():
    def __init__(self):
        self.conn = db.connection()
    
    def simpleJson(self, data):
        if isinstance(data, Decimal):
            data = float(data)
        
        if isinstance(data, datetime):
            data = str(data)
        
        return data
        
    def get(self):
        sql = """
        SELECT
	        *
        FROM department
        """
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql)
                    data = cursor.fetchall()
                    result = [self.simpleJson(x) for x in data]
                    return result
                except MySQLError as e:
                    print(e)



