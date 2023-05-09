from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from ..models import room, rack, log, current
from decimal import Decimal

bp = Blueprint('modal', __name__, url_prefix='/modal')

#모달창 실행
@bp.route('/add/<doc>')
def addForm(doc):
    result = 'modal/add/' + doc + '.html'
    return render_template(result)

@bp.route('/detail/<room_idx>', methods = ['GET', 'PUT'])
def getRoomDetail(room_idx):
    ro = room.Room(room_idx)

    #GET
    if request.method == 'GET':
        data = ro.getOne()

        for k, v in data.items():
            data[k] = simpleJson(v)

        return render_template("modal/detail/room.html", data = data)

    #PUT
    if request.method == 'PUT':
        data = request.get_json()

        for k, v in data.items():
            if v.strip() == "":
                data[k] = None

        result = ro.update(data)
        return result
    
@bp.route('/detail/<room_idx>/<int:row>/<int:col>/<int:ord>', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def getDetailModal(room_idx, row, col, ord):
    ro = room.Room(room_idx)
    ra = rack.Rack()
    lo = log.Log()

    #GET
    if request.method == 'GET':
        room_data = ro.getOne()
        d = ra.getDetail(room_idx, row, col, ord)
        data = {
            'row': row,
            'col': col,
            'ord': ord
        }

        if len(d) < 1:
            return render_template('modal/add/rack.html', data = data)

        sensors = {x['position']: x['mac'] for x in d}
        standard_apply = {}
        default_data = d.pop()
        
        try:
            for k, v in default_data.items():
                if v == None:                   
                    standard_apply[k] = simpleJson(room_data[k]) #detail_data 중 null 값인 경우 room_data의 설정값을 적용
                data[k] = simpleJson(v)
        except:
            pass
        
        default_data['sensors'] = sensors
        data['sensors'] = sensors
        
        #log_data
        logs = lo.getDetail(default_data['title'], list(default_data['sensors'].keys())[0], page = 1)
        total_cnt = lo.totalCount(default_data['title'], list(default_data['sensors'].keys())[0])
        for l in logs:
            for k, v in l.items():
                l[k] = simpleJson(v)

        log_data = {
            'log': logs,
            'total': total_cnt['total']
        }
        return render_template('modal/detail/rack.html', data = data, log_data = log_data, standard_apply = standard_apply)

    #POST
    if request.method == 'POST':
        data = request.get_json()
        result = ra.set(data)
        return result

    #PUT
    if request.method == 'PUT':
        data = request.get_json()   
        location = {
            'room_idx': room_idx,
            '`row`': row,
            'col': col,
            'ord': ord
        }
        result = ra.update(data, location)
        return result

    #DELETE
    if request.method == 'DELETE':
        data = {
            'room_idx': room_idx,
            '`row`': row,
            'col': col,
            'ord': ord
        }
        result = ra.delete(data)
        return result

@bp.route('/detail/log/<rack>/<position>', methods = ['GET', 'DELETE'])
def getLogData(rack, position):
    lo = log.Log()
    cu = current.Current()

    #GET
    if request.method == 'GET':
        page = request.args.get('page')
        data = lo.getDetail(rack, position, page)
        total = lo.totalCount(rack, position)["total"]
        log_data = []
        
        for d in data:
            for k, v in d.items():
                d[k] = simpleJson(v)
            log_data.append(d)

        result = {
            'log': log_data,
            'total': total
        }
        return jsonify(result)

    #DELETE
    if request.method == 'DELETE':
        result = cu.delete()
        return result
    
def simpleJson(data):
    if isinstance(data, Decimal):
        data = float(data)
    
    if isinstance(data, datetime):
        data = str(data)
    
    return data