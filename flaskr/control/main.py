from flask import Blueprint, request, render_template, jsonify
from werkzeug.utils import redirect
from ..models import log, current
from decimal import Decimal
from datetime import datetime
from pprint import pprint as pp

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    return redirect('/room')

@bp.route('/list')
def listTable():
    return render_template('list.html')

#임시 api(나중에 정리하면서 수정할 예정)
@bp.route('/list/update', methods = ['GET'])
def listUpdate():
    cu = current.Current()

    if request.method == 'GET':
        data = cu.listUpdate()
        for i, d in enumerate(data):
            d['no'] = i + 1

            for k, v in d.items():
                if isinstance(v, Decimal):
                    d[k] = float(v)
                if isinstance(v, datetime):
                    d[k] = str(v)

        return jsonify(data)

#로그 데이터 입력
@bp.route('/insert.html', methods = ['GET'])
def logInsert():
    #log Class 객체 생성(DB control)
    lo = log.Log()
    
    #data 정의 type = dict
    data = request.args.to_dict()

    #필수값 정의
    req = {
        'rack': 'rack',
        'pos': 'position',
        'temp': 'temperature',
        'humi': 'humidity'
    }

    #데이터 확인
    for k, v in req.items():

        #데이터 안에 필수값이 없으면 return
        if k not in data:
            return "필수값이 없습니다"

        # key name 다시 정의 
        # ex) temp -> temperature
        else:
            val = data.pop(k)
            data[v] = val

    #insert 실행
    result = lo.insert(data)
    
    #성공했을경우 return "success"
    #실패했을경우 return "err"
    return result

@bp.route('/test', methods = ['GET'])
def test():
    return render_template('test.html')