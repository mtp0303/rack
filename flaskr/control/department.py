from flask import Blueprint, request, jsonify
from ..models import department

bp = Blueprint('department', __name__, url_prefix='/department')

#부서 모든 데이터 호출
@bp.route('/', methods = ['GET'])
def getAll():
    if request.method == 'GET':
        d = department.Department()
        result = d.get()
        return jsonify(result)
        
