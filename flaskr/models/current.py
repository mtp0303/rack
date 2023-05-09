from pymysql.err import MySQLError
from ..modules import db
from pprint import pprint as pp

class Current():
    def __init__(self):
        self.conn = db.connection()
    
    def getAll(self, room_idx = None):
        where = "" if room_idx == None else "WHERE room_idx = {}".format(room_idx)

        sql = """
        SELECT 
            C.rack,
            C.position,
            C.temperature,
            C.humidity,
            C.date_update AS time,
            RA.room_idx,
            RA.row,
            RA.col,
            RA.ord,
            RA.alarm_message,
            RA.alarm_sound,
            IFNULL(RA.temp_low, RM.temp_low) AS temp_low,
            IFNULL(RA.temp_max, RM.temp_max) AS temp_max,
            IF(RA.date_sound IS NULL, NOW(), DATE_ADD(RA.date_sound, INTERVAL IFNULL(RA.cycle_sound, RM.cycle_sound) MINUTE)) AS timer_sound,
            IF(RA.date_message IS NULL, NOW(), DATE_ADD(RA.date_message, INTERVAL IFNULL(RA.cycle_message, RM.cycle_message) MINUTE)) AS timer_message,
            IF(C.temperature < IFNULL(RA.temp_low, RM.temp_low) OR C.temperature > IFNULL(RA.temp_max, RM.temp_max), 1, 0) AS err_temp,
            IF(C.date_update < DATE_SUB(NOW(), INTERVAL 10 MINUTE), 1, 0) AS err_time
        FROM current AS C
            LEFT JOIN rack AS RA ON ( RA.title = C.rack )
            LEFT JOIN room AS RM ON ( RA.room_idx = RM.idx )
        {}
        """.format(where)
        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
    
    def listUpdate(self):
        sql = """
        SELECT
            *
        FROM current
        ORDER BY date_update DESC
        LIMIT 30
        """
        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
    
    def delete(self, rack, position):
        sql = """
        DELETE FROM current WHERE rack = %s AND position = %s
        """
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, (rack, position))
                    self.conn.commit()
                    return "삭제되었습니다" 
                except Exception as e:
                    return "fail"
