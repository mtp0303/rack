from flask import Blueprint, request, jsonify
from ..models import rack
from decimal import Decimal
from datetime import datetime

ALARM_TYPE = ['sound', 'message']

bp = Blueprint('alarm', __name__, url_prefix='/alarm')

def simpleJson(data):
    if isinstance(data, Decimal):
        data = float(data)    
    
    if isinstance(data, datetime):
        data = str(data)

    if data == "true":
        data = True
    
    if data == "false":
        data = False
    
    return data

@bp.route('/', methods = ['GET'])
def alarm():
    ra = rack.Rack()

    if request.method == 'GET':

        #return data
        result = []

        #param data set
        j = request.get_json()

        #default type set
        a_type = "sound"

        #정해진 type 값이 들어왔을 경우 a_type 재정의
        #아닐경우 a_type = "sound"
        try:
            if j['type'] in ALARM_TYPE:
                a_type = j['type']
        except:
            pass

        #정해진 type 의 알람 데이터 가져오기
        data = ra.getAlarm(a_type)
        
        #result data set
        for d in data:
            error = list(filter(None, [d['err_time'], d['err_temp']]))
            timer = d.pop('timer').strftime('%Y-%m-%d %H:%M')

            if error:
                if timer <= datetime.now().strftime('%Y-%m-%d %H:%M'):
                    redifind = {
                        'rack': d['rack'],
                        'room': {'idx': d['room_idx'], 'title': d['title']},
                        'position': d['position'],
                        'mac': d['mac'],
                        'department': {'code': d['department_code'], 'name': d['name']},
                        'temperature': d['temperature'],
                        'humidity': d['humidity'],
                        'error': error,
                        'date_update': d['date_update']
                    }
                    result.append(redifind)
        
        #result data type redefind
        for r in result:
            for k, v in r.items():
                r[k] = simpleJson(v)
        
        alarm_list = [(x['room']['idx'], x['rack']) for x in result]
        ra.setAlarmDate(a_type, alarm_list)

    return jsonify(result)

@bp.route('/<int:room_idx>', methods = ['GET'])
def roomAlarm(room_idx):
    ra = rack.Rack()
    
    if request.method == 'GET':
        #return data
        result = []

        #param data set
        j = request.get_json()

        #default type set
        a_type = "sound"

        #정해진 type 값이 들어왔을 경우 a_type 재정의
        #아닐경우 a_type = "sound"
        try:
            if j['type'] in ALARM_TYPE:
                a_type = j['type']
        except:
            pass

        data = ra.getAlarm(a_type, room_idx)
        
        #result data set
        for d in data:
            error = list(filter(None, [d['err_time'], d['err_temp']]))
            timer = d.pop('timer').strftime('%Y-%m-%d %H:%M')

            if error:
                if timer <= datetime.now().strftime('%Y-%m-%d %H:%M'):
                    redifind = {
                        'rack': d['rack'],
                        'room_idx': d['room_idx'],
                        'position': d['position'],
                        'mac': d['mac'],
                        'department': {'code': d['department_code'], 'name': d['name']},
                        'temperature': d['temperature'],
                        'humidity': d['humidity'],
                        'error': error,
                        'date_update': d['date_update']
                    }
                    result.append(redifind)
        
        #result data type redefind
        for r in result:
            for k, v in r.items():
                r[k] = simpleJson(v)
        
        alarm_list = [(x['room_idx'], x['rack']) for x in result]
        ra.setAlarmDate(a_type, alarm_list)

    return jsonify(result)