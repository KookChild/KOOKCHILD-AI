from django.http import JsonResponse
from django.db import connection # settings.py 에 있는 DB 랑 연결 됨
import pandas as pd
from datetime import datetime
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes,permission_classes
from rest_framework import permissions
# from rest_framework.response import Response
# from .models import Users
import jwt
from KOOKCHILD.settings import SECRET_KEY
# @authentication_classes([JWTAuthentication])

    
child_id =''
period = ''

def get_query():

    if (True):
        query = """
            SELECT amount, created_date, category, is_deposit
            FROM account_history 
            WHERE user_id = :childid
            AND TO_CHAR(created_date, 'YYYY-MM') BETWEEN :start_date AND :end_date
            AND category not in ('리워드', '적금')
        """

        
        return query
    
def get_ratio_query():


    query = """SELECT amount, category 
        FROM account_history
        WHERE user_id = :childid AND category not in ('예금', '리워드', '적금')  
        """
    
    return query

def get_params(child_id,period):
    stdt, enddt = map(str, period.split('~'))


    params = {
        'childid':child_id,
        'start_date' : stdt,
        'end_date' : enddt
    }

    return params

def get_year():
    stdt, enddt = map(str, period.split('~'))
    
    result = [ i for i in range(int(stdt[:4]),int(enddt[:4])+1)]
    return result


def get_year_and_month():
    stdt, enddt = map(str, period.split('~'))
    start_date = datetime.strptime(stdt, '%Y-%m')
    end_date = datetime.strptime(enddt, '%Y-%m') 
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


# def get_datetime():
#     stdt, enddt = map(str, period.split('~'))
#     stdtor = datetime.strptime(stdt.strip(), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
#     enddtor = datetime.strptime(enddt.strip(), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
#     return stdtor, enddtor


def get_df(cursor:connection) -> pd:
    
    results = cursor.fetchall()    

    columns = [desc[0] for desc in cursor.description]
    data = pd.DataFrame(results, columns=columns)

    #print(data)
    data.dropna(inplace = True) # null 값 처리 / 실 데이터에는 없을 것이므로 삭제 가능
    data.reset_index(drop=True, inplace = True)
    # 날짜 분해
    try:
        data['YEAR']=data['CREATED_DATE'].dt.year.astype(int)
        data['MONTH']=data['CREATED_DATE'].dt.month.astype(int)
    except:
        data['YEAR']=0
        data['MONTH']=0
    

    data.drop('CREATED_DATE', axis=1, inplace=True)
    # print(df)

    return data


def get_pie_chart(df:pd, dtype:int,isParent:bool):
    
    pie_df = df[df['IS_DEPOSIT']== 0] # 예금이 아닌 값들만 취하기
    pie_df = pie_df.drop('IS_DEPOSIT' , axis = 1).reset_index() # IS_DEPOSIT column 버리기
    

    '''
    세분화 안되어있는 데이터
    '''
    pie_chart = pie_df.drop(["YEAR", "MONTH"], axis=1)
    pie_chart=pie_chart.groupby("CATEGORY").agg({"AMOUNT": "sum", "CATEGORY": "count"}).rename(columns={"CATEGORY": "COUNT"})
    pie_chart = pie_chart.reset_index()
    
    if(isParent):
        pie_chart['PERCENTAGE']  = (pie_chart['AMOUNT'] /pie_chart['AMOUNT'].sum() * 100).round(2)
        pie_chart.drop(['AMOUNT'], axis=1, inplace=True)
        pie_chart['PERCENTAGE'] = pie_chart['PERCENTAGE'].apply(lambda x: f'{x:.2f}')
    
    #year_pie_chart = year_pie_chart.to_dict(orient='list')
    pie_chart = pie_chart.to_dict(orient='index')
    print("===========pie chart===============")
    for key, value in pie_chart.items():
        print(f"{key}: {value}")
    return pie_chart



    if(dtype == 1):# 1 : year
        yearly_grouped = pie_df.groupby('YEAR')
        year_pie_chart = yearly_grouped.apply(lambda x: x.groupby('CATEGORY').agg({
            'CATEGORY': 'count',
            'AMOUNT': 'sum'
        }).rename(columns={'CATEGORY': 'COUNT'}))
        year_pie_chart= year_pie_chart.reset_index()

        if(isParent):
            year_pie_chart['PERCENTAGE']  = (year_pie_chart['AMOUNT'] /year_pie_chart['AMOUNT'].sum() * 100).round(2)
            year_pie_chart.drop(['AMOUNT'], axis=1, inplace=True)
            year_pie_chart['PERCENTAGE'] = year_pie_chart['PERCENTAGE'].apply(lambda x: f'{x:.2f}')
        
        #year_pie_chart = year_pie_chart.to_dict(orient='list')
        year_pie_chart = year_pie_chart.to_dict(orient='index')
        for key, value in year_pie_chart.items():
            print(f"{key}: {value}")
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
            month_pie_chart['PERCENTAGE'] = month_pie_chart['PERCENTAGE'].apply(lambda x: f'{x:.2f}')
        
        # month_pie_chart = month_pie_chart.to_dict(orient='list')
        month_pie_chart = month_pie_chart.to_dict(orient='index')
        for key, value in month_pie_chart.items():
             print(f"{key}: {value}")
        return month_pie_chart
    

def get_stack_chart(df:pd, dtype:int,isParent:bool):
    
    if (dtype == 1): # yearly 

        year_stack_chart = df.groupby(['IS_DEPOSIT','YEAR']).sum().drop(['CATEGORY', 'MONTH'],  axis = 1).sort_values(by='YEAR').reset_index()
        year_stack_chart['IS_DEPOSIT'] = year_stack_chart['IS_DEPOSIT'].replace({0: '소비', 1: '예금'})
        
        if(isParent):   
            year_stack_chart['PERCENTAGE']  = (year_stack_chart['AMOUNT'] /year_stack_chart['AMOUNT'].sum() * 100).round(2)
            year_stack_chart.drop(['AMOUNT'], axis=1, inplace=True)
            year_stack_chart['PERCENTAGE'] = year_stack_chart['PERCENTAGE'].apply(lambda x: f'{x:.2f}')
            
        # year_stack_chart = year_stack_chart.to_dict(orient='list')
        year_stack_chart = year_stack_chart.to_dict(orient='index')
        print("===========stack chart===============")
        for key, value in year_stack_chart.items():
             print(f"{key}: {value}")
        return year_stack_chart
    
    elif(dtype == 2): # monthly
        year_and_month = get_year_and_month() # 시작과 끝의 이 동안의 년, 월을 받음
        deposit_list = [0,1]

        month_stack_chart = df.groupby(['IS_DEPOSIT','YEAR','MONTH']).sum().drop(['CATEGORY'],  axis = 1).reset_index()
        
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
            month_stack_chart['PERCENTAGE'] = month_stack_chart['PERCENTAGE'].apply(lambda x: f'{x:.2f}')
               
        #month_stack_chart = month_stack_chart.to_dict(orient='list')
        month_stack_chart['YEAR_MONTH'] = month_stack_chart['YEAR'].astype(str) + '-' + month_stack_chart['MONTH'].astype(str).str.zfill(2)
        month_stack_chart.drop(['YEAR','MONTH'],axis=1, inplace=True)
        month_stack_chart = month_stack_chart.to_dict(orient='index')
        print("===========stack chart===============")
        for key, value in month_stack_chart.items():
             print(f"{key}: {value}")
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

   
    
    
    '''
    쿼리문과 params 설정:: account_history_id 는 임의의 데이터라 나중에 삭제해야함
    ''' 
    cursor = connection.cursor()
    cursor.execute(sql=get_query(),params=get_params(child_id,period))
    
    # 데이터프레임으로 받기
    df = get_df(cursor=cursor)
    
    # dtype에 따른 pie graph 
    pie_chart = get_pie_chart(df=df, dtype=dtype, isParent = True)
    stack_chart = get_stack_chart(df=df, dtype=dtype, isParent = True)
    return_json['PIE'] = pie_chart
    return_json['STACK'] = stack_chart
    
    cursor.close()
    return JsonResponse(return_json, safe=False)

def get_ratio(request):
    global child_id 
    child_id = request.GET.get('child_id')
    return_json = {}
    cursor = connection.cursor()


    cursor.execute("SELECT birthdate FROM Users where id = :id", {"id" : child_id})
    birthdate = cursor.fetchone()[0]
    current_date = datetime.now()
    age = current_date.year - birthdate.year - ((current_date.month, current_date.day) < (birthdate.month, birthdate.day))
    print(f"나이: {age}세")

    '''모든 아이들'''
    
    cursor.execute("SELECT amount, category FROM account_history WHERE category not in ('예금' , '적금' , '리워드')")
    query_result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    all_df = pd.DataFrame(query_result, columns=columns)
    all_df.dropna(inplace = True)
    all_df.reset_index(drop=True, inplace = True)
    sum_df = all_df.groupby(['CATEGORY']).sum().reset_index()
    # mean_df = all_df.groupby(['CATEGORY']).mean().reset_index()
    '''특정 자녀'''
    query = "SELECT amount, category FROM account_history WHERE category not in ('예금' , '적금' , '리워드') and user_id = :child_id" 
    params = {'child_id': child_id}
    cursor.execute(query,params)
    query_result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    child_df = pd.DataFrame(query_result, columns=columns)
    child_df.dropna(inplace = True)
    child_df.reset_index(drop=True, inplace = True)
    child_sum_df = child_df.groupby(['CATEGORY']).sum().reset_index()
    child_sum_df['AMOUNT'] =  ( child_sum_df['AMOUNT']*100 / sum_df['AMOUNT']).round(2)
    child_sum_df['AMOUNT']  = 100 -  child_sum_df['AMOUNT'] # 상위 몇 퍼센트인지 
    child_sum_df = child_sum_df.sort_values(by=['AMOUNT'], ascending=False).reset_index() # 내림차순으로 정렬
    child_sum_df.drop(columns=['index'], axis = 1, inplace = True)
    col = list(child_sum_df.columns)
    print(f"=========== {child_id} 상위 ===============") # 년도별 월별..?
    for i in range(child_sum_df.shape[0]):
        print( str(child_sum_df.iloc[i][col[0]]) + " 항목에서 상위 "+ str(child_sum_df.iloc[i][col[1]])+" % 소비" )
    
    child_sum_df = child_sum_df.set_index('CATEGORY')['AMOUNT'].to_dict()#.to_dict(orient='index')
    print(child_sum_df)
    cursor.close()

    return_json['MY_DATA'] = child_sum_df
    return_json['AGE']=age
    return  JsonResponse( return_json, safe = False)











    # return_json['RATIO'] = get_ratio()

    # return JsonResponse(return_json, safe=False)


@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def graph_api_child(request):

    return_json = {}

    global period
    global child_id

    # 토큰을 가지고 아이 id 가져오기
    token = request.headers.get('Authorization')
    token = token.replace('Bearer ', '')
    user_email = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

    cursor = connection.cursor()
    cursor.execute("SELECT id FROM Users where email = :email", {"email" :  user_email['sub']})
    child_id = cursor.fetchone()[0]




    '''
    GET 요청에서 파라미터 추출
    '''

    period = request.GET.get('period') # 2022-09-23~2023-03-11
    dtype = int(request.GET.get('type')) # 1 : yearly / 2 : monthly

   
    
    
    '''
    쿼리문과 params 설정:: account_history_id 는 임의의 데이터라 나중에 삭제해야함
    ''' 
    cursor = connection.cursor()
    cursor.execute(sql=get_query(),params=get_params(child_id,period))
    
    # 데이터프레임으로 받기
    df = get_df(cursor=cursor)

    # dtype에 따른 pie graph 
    pie_chart = get_pie_chart(df=df, dtype=dtype, isParent = False)
    stack_chart = get_stack_chart(df=df, dtype=dtype, isParent = False)
    return_json['PIE'] = pie_chart
    return_json['STACK'] = stack_chart

    
    return JsonResponse(return_json, safe=False)
    