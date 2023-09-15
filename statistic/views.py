from django.shortcuts import render
# import cx_Oracle as cx

from .serializers import DataFrameSerializer
# Create your views here.
from .models  import *
from django.http import JsonResponse
from rest_framework.response import Response
from django.db import connection # settings.py 에 있는 DB 랑 연결 됨
from django.core import serializers
import pandas as pd
import json
from datetime import datetime

'''
같은 api, 하면 try catch 로 받기? 
'''


def graph_api_parent(request):
    
    '''
    GET 요청에서 파라미터 추출
    '''

    child_id = request.GET.get('child_id')

    period = request.GET.get('period') # 2022-09-23~2023-09-11
    stdt, enddt = map(str, period.split('~'))
    stdtor = datetime.strptime(stdt.strip(), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
    enddtor = datetime.strptime(enddt.strip(), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
    
    dtype = request.GET.get('type') # 1 : year / 2 : month
    # if dtype == '1' : dtype = 'YEAR'
    # else : dtype = 'MONTH'
    
    '''
    쿼리문과 params 설정:: account_history_id 는 임의의 데이터라 나중에 삭제해야함
    '''
    query = "SELECT amount, created_date, category, is_deposit"+\
        "FROM account_history " +\
        "WHERE user_id = :childid " +\
        "AND id >= :account_history_id " +\
        "AND created_date >= :start_date " +\
        "AND created_date <= :end_date " +\
        "AND is_deposit != 1 " +\
        "ORDER BY created_date "


    params = {
        'childid':child_id,
        'account_history_id' : '300',
        'start_date' : stdtor,
        'end_date' : enddtor
    }


    cursor = connection.cursor()
    cursor.execute(sql=query,params=params)
    results = cursor.fetchall()

    
    '''
    pandas 처리
    '''
    columns = [desc[0] for desc in cursor.description]
    
    df = pd.DataFrame(results, columns=columns)
    
    df.dropna(inplace = True) # null 값 처리 / 실 데이터에는 없을 것이므로 삭제 가능
    df.reset_index(drop=True, inplace = True)

    # 날짜 분해
    df['YEAR']=df['CREATED_DATE'].dt.year.astype(int)
    df['MONTH']=df['CREATED_DATE'].dt.month.astype(int)
    df['DAY']=df['CREATED_DATE'].dt.day.astype(int)




    '''
    dtype에 따라서 yearly, monthly 코드 다르게
    '''

    df = df.groupby('CATEGORY').agg(SUM_AMOUNT=('AMOUNT', 'sum'), COUNT=('CATEGORY', 'count')).reset_index()




    df['SUM_AMOUNT'].sum()
    df['PERCENTAGE']  = (df['SUM_AMOUNT'] /df['SUM_AMOUNT'].sum() * 100).round(2)
    #df.drop(['SUM_AMOUNT','CREATED_DATE'] , axis = 1, inplace = True)
    df.drop(['SUM_AMOUNT'], axis=1, inplace=True)
    #df['PERCENTAGE'] = df['PERCENTAGE'].round(2)

    # json_data = df.to_json(orient='list')
    # print(type(json_data))
    # return JsonResponse(json_data,safe=False)


    # return 해야 하는 pandas. json 파일로 바꿔야 함
    print(df)
    print("========to_dict========")
    print(df.to_dict(orient='list'))
    df = df.to_dict(orient='list')
    
    print("========json_data========")
    return JsonResponse(df, safe=False) # dictionary 바로 json으로 가능

    # 이미 필요한 data가 column에 있어서 시리얼 필요없음


def graph_api_child(request):

    period = request.GET.get('period') # 2022-09-23~2023-09-11
    stdt, enddt = map(str, period.split('~'))
    stdtor = datetime.strptime(stdt.strip(), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
    enddtor = datetime.strptime(enddt.strip(), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
    
    dtype = request.GET.get('type') # 1 : year / 2 : month

    data = {


    }
    return JsonResponse(data)
