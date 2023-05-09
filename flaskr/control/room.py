from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import redirect
from ..models import room, rack, current
from datetime import datetime

from pprint import pprint as pp

bp = Blueprint('room', __name__, url_prefix='/room')

@bp.route('/', methods = ['GET', 'POST'])
def index():
    ro = room.Room()

    if request.method == 'GET':
        room_data = ro.getAll()
        frist_room = ""

        #room_data가 있을경우 첫번째 room 으로 redirect
        if room_data:
            frist_room = room_data[0]["idx"]

        return redirect('/room/{}'.format(frist_room))
    
    #POST
    if request.method == 'POST':
        data = request.get_json() 
        title = data['title']

        for k, v in data.items():
            if not v:
                data[k] = None
        #vaildation (추후 다른곳에서 적용할 예정)
        if title.strip() == '':
            return "이름을 입력해주세요"

        result = ro.set(data)
        return result

@bp.route('/<room_idx>', methods = ['GET', 'DELETE', 'PUT'])
def main(room_idx):
    ro = room.Room(room_idx)
    ra = rack.Rack()
    cu = current.Current()

    #GET
    if request.method == 'GET':
        room_data = ro.getAll()
        rack_data = ra.getAll(room_idx)
        max_data = ro.getMax()
        current_data = cu.getAll(room_idx)
        main_data = {
            'room_idx': room_idx,
            'room': room_data,
            "container": [],
        }

        #랙 데이터가 없을경우 바로 return
        if not rack_data:
            return render_template('main.html', main_data = main_data)
        
        #랙 데이터가 있을경우
        #container, current data 생성
        main_data['container'] = makeContainerData(rack_data, max_data)
        main_data['current'] = makeCurrentData(current_data)

        return render_template('main.html', main_data = main_data)

    #DELETE
    if request.method == 'DELETE':
        result = ro.delete()
        return result   

    #PUT
    if request.method == 'PUT':
        data = request.get_json()

        #validation
        title = data['title']

        if title.strip() == '':
            return "이름을 입력해주세요"

        result = ro.update(data)
        return result

@bp.route('/<room_idx>/rack', methods = ['DELETE'])
def rackControl(room_idx):
    ra = rack.Rack()

    #DELETE
    if request.method == 'DELETE':
        data = request.get_json()
        result = ra.delete(data)
        return result

@bp.route('/<room_idx>/currentData', methods = ['GET', 'DELETE'])
def getcurrentData(room_idx):
    cu = current.Current()
    
    #GET
    if request.method == 'GET':
        data = cu.getAll(room_idx)
        result = makeCurrentData(data)
        return jsonify(result)
    
    #DELETE
    if request.method == 'DELETE':
        data = request.get_json()
        result = cu.delete(data['rack'], data['position'])
        return result


@bp.route('/<room_idx>/soundAlarm', methods = ['POST'])
def soundAlarm(room_idx):
    ra = rack.Rack()

    #POST
    if request.method == 'POST':
        alarm_sound = request.form.getlist('alarm_sound[]')
        result = ra.setLastSoundAlarm(room_idx, alarm_sound)
        return result

@bp.route('/<room_idx>/messageAlarm', methods = ['POST'])
def messageAlarm(room_idx):
    ra = rack.Rack()

    #POST
    if request.method == 'POST':
        alarm_message = request.form.getlist('alarm_message[]')
        result = ra.setLastMessageAlarm(room_idx, alarm_message)
        return result

#데이터 재가공
#json 형태로 보낼 데이터를 재가공하여 return
def makeContainerData(rack_data, max_data):
    max_row = sorted(max_data, key=lambda location: (location['row']), reverse=True)[0]['row']
    max_col = sorted(max_data, key=lambda location: (location['col']), reverse=True)[0]['col']
    
    result = []
    for r in range(max_row):
        row = []
        
        for c in range(max_col):
            container = []
            ord = list(filter(lambda x: x['row'] == r + 1 and x['col'] == c + 1, max_data))
            max_ord = ord[0]['ord'] if len(ord) > 0 else 0
            
            for o in range(max_ord): 
                rack = {}
                
                for ra in rack_data:
                    if ra["row"] == r + 1 and ra["col"] == c + 1 and ra["ord"] == o + 1:

                        rack = {
                            'title': ra['title'],
                        }

                container.append(rack)
            row.append(container)
        result.append(row)
    return result

def makeCurrentData(current_data):
    err_list = [x for x in current_data if x["err_temp"] > 0 or x["err_time"] > 0]
    in_data = []
    result = {
        "rack": [],
        "alarm_sound": [],
        "alarm_message": []
    }

    for cu in current_data:
        sensor = {
            "position": cu["position"],
            "temperature": float(cu["temperature"]),
            "humidity": float(cu["humidity"]),
            "time": str(cu["time"]),
            "err_time": cu["err_time"],
            "err_temp": cu["err_temp"]
        }

        if cu["rack"] not in in_data:
            c_data = {
                    "title": cu["rack"],
                    "row": cu["row"],
                    "col": cu["col"],
                    "ord": cu["ord"],
                    "temp_low": float(cu["temp_low"]),
                    "temp_max": float(cu["temp_max"]),
                    "color": "black",
                    "sensors": [sensor]
                }

            in_data.append(cu["rack"])
            result["rack"].append(c_data)

        else:
            target = result['rack'][in_data.index(cu["rack"])]['sensors']
            target.append(sensor)

        
    for c in result["rack"]:
        c["color"] = makeColor(c)

    result["alarm_sound"] = makeSoundAlarm(err_list)
    result["alarm_message"] = makeMassageAlarm(err_list)

    return result

def makeColor(c):
    err = []
    color = 'black'
    
    for i in range(len(c["sensors"])):
        s = c["sensors"][i]
        
        # err 센서가 존재할 경우 pass
        if s["err_time"] > 0 or s["err_temp"] > 0:
            continue
        
        temp_max = float(c["temp_max"]) 
        temp_low = float(c["temp_low"])
        temp = float(s["temperature"])
        section = 510 / (temp_max - temp_low)
        val = (temp - temp_low) * section
        
        r = 0
        g = 0
        b = 51
        
        if val > 255:
            r = 255
            g = 510 - val
        else:
            r = val
            g = 255
            
        return "rgb({}, {}, {})".format(r, g, b)
    return color
    
def makeSoundAlarm(err_list):
    isinresult = []
    result = []
    now = datetime.now().replace(microsecond=0)

    for e in err_list:
        if e["rack"] in isinresult or e["alarm_sound"] != "Y" or now < e["timer_sound"]:
            continue

        isinresult.append(e['rack'])
        result.append(e['rack'])
    
    return result

def makeMassageAlarm(err_list):
    isinresult = []
    result = []
    now = datetime.now().replace(microsecond=0)

    for e in err_list:
        if e["rack"] in isinresult or e["alarm_message"] != "Y" or now < e["timer_message"]:
            continue
        
        isinresult.append(e['rack'])
        result.append(e['rack'])
    
    return result




