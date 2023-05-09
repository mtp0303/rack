from ..modules import db, err
from pymysql.err import MySQLError
from pprint import pprint as pp

class Rack():
    def __init__(self):
        self.conn = db.connection()
        self.err = err.Err()

    def connect(self):
        if not self.conn.open:
            self.conn.connect()

    def getAll(self, room_idx):
        sql = """
        SELECT 
            room_idx,
            title, 
            `row`, 
            col, 
            ord, 
            temp_low, 
            temp_max,
            alarm_message, 
            alarm_sound, 
            cycle_message, 
            cycle_message 
        FROM rack WHERE room_idx = %s
        """

        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, (room_idx))
                    result = cursor.fetchall()
                    return result
                except Exception as e:
                    print(e)

    def getDetail(self, room_idx, row, col, ord):
        sql = """
        SELECT 
            RA.room_idx,
            RA.title, 
            RA.`row`, 
            RA.col, 
            RA.ord, 
            RA.temp_low,
            RA.temp_max,
            RA.alarm_message, 
            RA.alarm_sound, 
            RA.cycle_message, 
            RA.cycle_sound,
            C.position,
            C.mac
        FROM rack AS RA
        LEFT JOIN current AS C
        ON RA.title = C.rack
        WHERE room_idx = %s AND `row` = %s AND col = %s AND ord = %s
        """
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, (room_idx, row, col, ord))
                    result = cursor.fetchall()
                    return result
                except Exception as e:
                    print(e)
    
    def delete(self, data):
        location = " AND ".join(["{} = {}".format(k, v) for k, v in data.items()])
        sql = """
        DELETE FROM rack WHERE {}
        """.format(location)
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql)
                    self.conn.commit()
                    return "success"
                except MySQLError as e:
                    err_code = e.args[0]
                    err = self.err.print(err_code)
                    return err

    def set(self, data):
        data["`row`"] = data.pop("row")

        col = ", ".join(["{} = %s".format(x) for x in data.keys()])
        val = []
        for x in data.values():
            if x == '':
                x = None
            val.append(x)
        sql ="""
        INSERT INTO rack SET {}
        """.format(col)

        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, val)
                    self.conn.commit()
                    return "success"
                except MySQLError as e:
                    print(e)
                    err_code = e.args[0]
                    err = self.err.print(err_code)
                    return err
    
    def update(self, data, location):
        if data.get("row"):
            data["`row`"] = data.pop("row")

        col = ", ".join(["{} = %s".format(x) for x in data.keys()])
        val = tuple(data.values())
        lo = " AND ".join(["{} = {}".format(k, v) for k, v in location.items()])
        sql = """
        UPDATE rack SET {} 
        WHERE {}
        """.format(col, lo)
        print(sql)
        pp(data)
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql, val)
                    self.conn.commit()
                    return "success"
                except MySQLError as e:
                    print(e)
                    err_code = e.args[0]
                    err = self.err.print(err_code)
                    return err
    
    def setLastSoundAlarm(self, room_idx, alarm_sound):
        sql = """
        UPDATE rack 
        SET date_sound = now()
        WHERE room_idx = {} AND title = %s
        """.format(room_idx)
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.executemany(sql, alarm_sound)
                    self.conn.commit()
                    return "success"
                except Exception as e:
                    print(e)
                    return "fail"
    
    def setAlarmDate(self, alarm_type, alarm_list):
        self.connect()

        sql = """
        UPDATE rack 
        SET date_{} = NOW()
        WHERE room_idx = %s AND title = %s
        """.format(alarm_type)
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.executemany(sql, alarm_list)
                    self.conn.commit()
                    return "success"
                except Exception as e:
                    print(e)
                    return "fail"

    def getAlarm(self, alarm_type, room_idx = None):
        where = "AND room_idx = {}".format(room_idx) if room_idx else ""
        sql = """
        SELECT
            C.rack,
            C.position,
            C.temperature,
            C.humidity,
            C.date_update,
            C.mac,
            RA.room_idx,
            RM.title,
            RM.department_code,
            D.name,
            IF(C.temperature < IFNULL(RA.temp_low, RM.temp_low) OR C.temperature > IFNULL(RA.temp_max, RM.temp_max), "temp", null) AS err_temp,
            IF(C.date_update < DATE_SUB(NOW(), INTERVAL 10 MINUTE), "time", null) AS err_time,
            IF(RA.date_{0} IS NULL, NOW(), DATE_ADD(RA.date_{0}, INTERVAL IFNULL(RA.cycle_{0}, RM.cycle_{0}) MINUTE)) AS timer
        FROM rack AS RA

        LEFT JOIN room AS RM
        ON RA.room_idx = RM.idx

        LEFT JOIN current AS C
        ON RA.title = C.rack

        LEFT JOIN department AS D
        ON RM.department_code = D.code

        WHERE C.temperature IS NOT NULL
            AND RA.alarm_{0} = "Y"
            {1}
        """.format(alarm_type, where)
        with self.conn:
            with self.conn.cursor() as cursor:
                try:
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    return result
                except MySQLError as e:
                    print(e)
                    return "err"

