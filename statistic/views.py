from django.shortcuts import render
import cx_Oracle as cx
# Create your views here.
from .models  import *
from django.http import JsonResponse

def graph_api(request):
    
    # GET 요청에서 파라미터 추출
    child_id = request.GET.get('child_id')
    period = request.GET.get('period')
    type = request.GET.get('type')
    conn = cx.connect("1234","10.3.3.118:1521/XE") #DB연동
    cur = conn.cursor()
    cur.execute("select amount, created_date, category,is_deposit from account_history where user_id=22 and id >= 200")


    # 데이터 처리 또는 API 응답 생성
    # 예시로 JsonResponse를 사용하여 응답을 생성합니다.

    '''
    여기서 그래프 pandas 지지고 볶고 하기 쿼리문도 받으면 될듯...? type에 따라서 case 쓰고..? 
    '''
    data = {
        'child_id': child_id,
        'period': period,
        'type': type,
        'message': 'API 요청이 성공적으로 처리되었습니다.',
    }



    #return JsonResponse(data)
