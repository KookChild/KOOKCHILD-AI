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


def graph_api(request):
    
    # GET 요청에서 파라미터 추출
    child_id = request.GET.get('child_id')

    period = request.GET.get('period') # 2022-09-23~2023-09-11
    stdt, enddt = map(str, period.split('~'))
    stdtor = datetime.strptime(stdt.strip(), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
    enddtor = datetime.strptime(enddt.strip(), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
    
    dtype = request.GET.get('type') # 1 : year / 2 : month
    # if dtype == '1' : dtype = 'YEAR'
    # else : dtype = 'MONTH'
    
    query = "SELECT amount, created_date, category, is_deposit FROM account_history "+ \
    " WHERE user_id = :childid and id >= :account_history_id " +\
    "and CREATED_DATE >= :start_date and CREATED_DATE <= :end_date " +\
    "and is_deposit != 1 " +\
    "  ORDER BY created_date "
    params = {
    'childid':child_id,
    'account_history_id' : '300',
    'start_date' : stdtor,
    'end_date' : enddtor
    }

    # query = "SELECT amount, created_date, category, is_deposit FROM account_history WHERE user_id = %s and id >= %s" 
    #params = [child_id,200]

    cursor = connection.cursor()
    #with connection.cursor() as cursor:
        #cursor.execute("select amount, created_date, category,is_deposit from account_history where user_id=22 and id >= 300")
    cursor.execute(sql=query,params=params)
    results = cursor.fetchall()
    # for r in results: print(r)

    
    columns = [desc[0] for desc in cursor.description]
    # print(columns)


    # pandas 처리
    df = pd.DataFrame(results, columns=columns)
    # print(df) # 처음 data
    df.dropna(inplace = True)
    df.reset_index(drop=True, inplace = True)
    df['YEAR']=df['CREATED_DATE'].dt.year
    df['MONTH']=df['CREATED_DATE'].dt.month
    df['DAY']=df['CREATED_DATE'].dt.day
    df['YEAR'] = df['YEAR'].astype(int)
    df['MONTH'] = df['MONTH'].astype(int)
    df['DAY'] = df['DAY'].astype(int)
    df.drop('CREATED_DATE' , axis = 1, inplace = True)


    df1 = df.groupby('CATEGORY').agg(SUM_AMOUNT=('AMOUNT', 'sum'), COUNT=('CATEGORY', 'count')).reset_index()
    df1['SUM_AMOUNT'].sum()
    df1['SUM_AMOUNT']  = df1['SUM_AMOUNT'] /df1['SUM_AMOUNT'].sum() * 100
    df1['SUM_AMOUNT'] = df1['SUM_AMOUNT'].round(2)

    # json_data = df1.to_json(orient='list')
    # print(type(json_data))
    # return JsonResponse(json_data,safe=False)


    # return 해야 하는 pandas. json 파일로 바꿔야 함
    print(df1)
    print("========to_dict========")
    print(df1.to_dict(orient='list'))
    df1 = df1.to_dict(orient='list')
    # json_data = open()
    # json_data = json.dumps( df1, ensure_ascii=False)
    print("========json_data========")
    return JsonResponse(df1, safe=False)

    # 이미 필요한 data가 column에 있어서 시리얼 필요없음

    print("========serilaizer========")
    serializer = DataFrameSerializer(data=df1)#.to_dict(orient='list'))
    # serializer.is_valid(raise_exception=True)
    print(serializer)

    return Response(serializer.data)








    '''
    여기서 그래프 pandas 지지고 볶고 하기 쿼리문도 받으면 될듯...? type에 따라서 case 쓰고..? 
    '''
    data = {
        'child_id': child_id,
        'period': period,
        'type': dtype,
        'message': 'API 요청이 성공적으로 처리되었습니다.',
    }
    #data = df1.to_json(force_ascii=False, orient='split')
    # print(data)
    #data = df1.to_json()
    print(df1.to_dict(orient='records'))

    with open('data.json', 'w') as json_file:
        json.dump(result_data, json_file)


    cursor.close()
    return JsonResponse(data)
