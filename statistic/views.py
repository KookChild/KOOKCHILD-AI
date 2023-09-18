from unittest import case
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
# import json
from datetime import datetime

period = ''

def get_query():
    # AND id >= :account_history_id
    # AND is_deposit != 1 
    # ORDER BY created_date 
    # 나중에는 지워야 함
    query = "SELECT amount, created_date, category, is_deposit " \
        "FROM account_history " \
        "WHERE user_id = :childid " \
        "AND id >= :account_history_id " \
        "AND created_date >= :start_date " \
        "AND created_date <= :end_date " \
        "AND is_deposit != 2" \
        "ORDER BY created_date "
    
    return query

def get_params(child_id,stdtor,enddtor):

    params = {
        'childid':child_id,
        'account_history_id' : '0',
        'start_date' : stdtor,
        'end_date' : enddtor
    }

    return params



def get_year_and_month():
    stdt, enddt = map(str, period.split('~'))
    start_date = datetime.strptime(stdt, '%Y-%m-%d')
    end_date = datetime.strptime(enddt, '%Y-%m-%d') 
    result = []

    # 시작 날짜부터 끝 날짜까지 루프
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        result.append((year, month))
        
        # 다음 달로 이동 (day를 항상 1로 설정)
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1, day=1)

    return result


def get_datetime():
    stdt, enddt = map(str, period.split('~'))
    stdtor = datetime.strptime(stdt.strip(), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
    enddtor = datetime.strptime(enddt.strip(), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
    return stdtor, enddtor





def get_df(cursor) -> pd:
    
    results = cursor.fetchall()    
    '''
    pandas 처리
    '''
    columns = [desc[0] for desc in cursor.description]
    data = pd.DataFrame(results, columns=columns)

    
    data.dropna(inplace = True) # null 값 처리 / 실 데이터에는 없을 것이므로 삭제 가능
    data.reset_index(drop=True, inplace = True)
    # 날짜 분해
    data['YEAR']=data['CREATED_DATE'].dt.year.astype(int)
    data['MONTH']=data['CREATED_DATE'].dt.month.astype(int)
    data['DAY']=data['CREATED_DATE'].dt.day.astype(int)

    data.drop('CREATED_DATE', axis=1, inplace=True)
    # print(df)

    return data

# 연간 pie chart
# 부모인지 자녀인지에 따라서도 여기서 나눌 수 있을듯
def get_pie_chart(df:pd, dtype:int,isParent:bool):
    
    pie_df = df[df['IS_DEPOSIT']== 0] # 예금이 아닌 값들만 취하기
    pie_df = pie_df.drop('IS_DEPOSIT' , axis = 1) # IS_DEPOSIT column 버리기

    if(dtype == 1):# 1 : year
        yearly_grouped = pie_df.groupby('YEAR')
        year_pie_chart = yearly_grouped.apply(lambda x: x.groupby('CATEGORY').agg({
            'CATEGORY': 'count',
            'AMOUNT': 'sum'
        }).rename(columns={'CATEGORY': 'COUNT'}))

        year_pie_chart= year_pie_chart.reset_index()
        # print(year_pie_chart)
        if(isParent):
            year_pie_chart['PERCENTAGE']  = (year_pie_chart['AMOUNT'] /year_pie_chart['AMOUNT'].sum() * 100).round(2)
            year_pie_chart.drop(['AMOUNT'], axis=1, inplace=True)
        year_pie_chart = year_pie_chart.to_dict(orient='list')
        return year_pie_chart
    
    elif(dtype == 2): # month
        mothly_grouped = pie_df.groupby(['YEAR','MONTH'])
        month_pie_chart = mothly_grouped.apply(lambda x: x.groupby('CATEGORY').agg({
            'CATEGORY': 'count',
            'AMOUNT': 'sum'
        }).rename(columns={'CATEGORY': 'COUNT'}))

        month_pie_chart = month_pie_chart.reset_index()
        if(isParent):
            month_pie_chart['PERCENTAGE']  = (month_pie_chart['AMOUNT'] /month_pie_chart['AMOUNT'].sum() * 100).round(2)
            month_pie_chart.drop(['AMOUNT'], axis=1, inplace=True)
        #print(month_pie_chart)
        month_pie_chart = month_pie_chart.to_dict(orient='list')
        return month_pie_chart
    


def get_stack_chart(df:pd, dtype:int,isParent:bool):
    
    if (dtype == 1): # yearly 
        # period 기간 내에서 연도별 소비 내역
        year_stack_chart = df.groupby(['IS_DEPOSIT','YEAR']).sum().drop(['CATEGORY', 'DAY','MONTH'],  axis = 1).sort_values(by='YEAR').reset_index()
        year_stack_chart['IS_DEPOSIT'] = year_stack_chart['IS_DEPOSIT'].replace({0: '소비', 1: '예금'})
        
        if(isParent):   
            year_stack_chart['PERCENTAGE']  = (year_stack_chart['AMOUNT'] /year_stack_chart['AMOUNT'].sum() * 100).round(2)
            year_stack_chart.drop(['AMOUNT'], axis=1, inplace=True)        
        year_stack_chart = year_stack_chart.to_dict(orient='list')

        return year_stack_chart
    
    elif(dtype == 2): # monthly
        year_and_month = get_year_and_month() # 시작과 끝의 이 동안의 년, 월을 받음
        deposit_list = [0,1]
        # period 기간 내에서 연도별 소비 내역
        month_stack_chart = df.groupby(['IS_DEPOSIT','YEAR','MONTH']).sum().drop(['CATEGORY', 'DAY'],  axis = 1).reset_index()
        # print("=======month_stack_df=========")
        # print(month_stack_df)
        
        for r in year_and_month :
            for dp in deposit_list:
                tempdf = month_stack_chart[(month_stack_chart['YEAR'] == r[0]) & (month_stack_chart['MONTH'] == r[1]) & (month_stack_chart['IS_DEPOSIT'] == dp)]
                if(tempdf.empty):
                    # print(r, dp)
                    new_row={'IS_DEPOSIT':dp, 'YEAR': r[0], 'MONTH':r[1],'AMOUNT' : 0}
                    month_stack_chart = pd.concat([month_stack_chart, pd.DataFrame([new_row])], ignore_index = True)
        
        month_stack_chart=month_stack_chart.sort_values(by=['YEAR','MONTH']).reset_index(drop = True)
        month_stack_chart['IS_DEPOSIT'] = month_stack_chart['IS_DEPOSIT'].replace({0: '소비', 1: '예금'})

        if(isParent):
            month_stack_chart['PERCENTAGE']  = (month_stack_chart['AMOUNT'] /month_stack_chart['AMOUNT'].sum() * 100).round(2)
            month_stack_chart.drop(['AMOUNT'], axis=1, inplace=True)        
        month_stack_chart = month_stack_chart.to_dict(orient='list')
        
        return month_stack_chart
        


def graph_api_parent(request):
    global period

    return_json = {}

    '''
    GET 요청에서 파라미터 추출
    '''

    child_id = request.GET.get('child_id')
    period = request.GET.get('period') # 2022-09-23~2023-09-11
    dtype = int(request.GET.get('type')) # 1 : yearly / 2 : monthly

    stdtor, enddtor = get_datetime() # datetime 형태로 시작, 끝 날짜를 받음. oracle 형식으로
    
    
    '''
    쿼리문과 params 설정:: account_history_id 는 임의의 데이터라 나중에 삭제해야함
    ''' 
    cursor = connection.cursor()
    cursor.execute(sql=get_query(),params=get_params(child_id,stdtor,enddtor))
    
    # 데이터프레임으로 받기
    df = get_df(cursor=cursor)

    # dtype에 따른 pie graph 
    pie_chart = get_pie_chart(df=df, dtype=dtype, isParent = True)
    stack_chart = get_stack_chart(df=df, dtype=dtype, isParent = True)
    return_json['PIE'] = pie_chart
    return_json['STACK'] = stack_chart
    return JsonResponse(return_json, safe=False)




def graph_api_child(request):
    global period

    return_json = {}

    '''
    GET 요청에서 파라미터 추출
    '''

    child_id = request.GET.get('child_id')
    period = request.GET.get('period') # 2022-09-23~2023-09-11
    dtype = int(request.GET.get('type')) # 1 : yearly / 2 : monthly

    stdtor, enddtor = get_datetime() # datetime 형태로 시작, 끝 날짜를 받음. oracle 형식으로
    
    
    '''
    쿼리문과 params 설정:: account_history_id 는 임의의 데이터라 나중에 삭제해야함
    ''' 
    cursor = connection.cursor()
    cursor.execute(sql=get_query(),params=get_params(child_id,stdtor,enddtor))
    
    # 데이터프레임으로 받기
    df = get_df(cursor=cursor)

    # dtype에 따른 pie graph 
    pie_chart = get_pie_chart(df=df, dtype=dtype, isParent = False)
    stack_chart = get_stack_chart(df=df, dtype=dtype, isParent = False)
    return_json['PIE'] = pie_chart
    return_json['STACK'] = stack_chart
    return JsonResponse(return_json, safe=False)