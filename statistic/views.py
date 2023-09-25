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

    query = """
        SELECT amount, created_date, category, is_deposit
        FROM account_history 
        WHERE user_id = :child_id
        AND TO_CHAR(created_date, 'YYYY-MM') BETWEEN :start_date AND :end_date
        AND category not in ('리워드', '적금')
    """

    return query


def get_ratio_query():

    query = """SELECT amount, category 
        FROM account_history
        WHERE user_id = :child_id AND category not in ('예금', '리워드', '적금')  
        AND TO_CHAR(created_date, 'YYYY-MM') BETWEEN :start_date AND :end_date
        """
    
    return query


def get_params(child_id,period):
    stdt, enddt = map(str, period.split('~'))

    params = {
        'child_id':child_id,
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


def get_df(cursor:connection) -> pd:
    
    results = cursor.fetchall()    

    columns = [desc[0] for desc in cursor.description]
    data = pd.DataFrame(results, columns=columns)

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

    return data


def get_pie_chart(df:pd, dtype:int,isParent:bool,child_id:int):
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
    #pie_chart['CATEGORY'] = pie_chart['CATEGORY'].sort_value()
    pie_chart = pie_chart.sort_values(by=['CATEGORY'], ascending=True).reset_index() # category 내림차순으로 정렬
    pie_chart.drop(columns=['index'], axis = 1, inplace = True)
    #year_pie_chart = year_pie_chart.to_dict(orient='list')
    ratio_chart = get_ratio_chart(child_id)
    #print(ratio_chart)
    pie_chart['RATIO'] = ratio_chart#['MY_DATA']
  
    pie_chart = pie_chart.to_dict(orient='index')
   
    # print("===========pie chart===============")
    # for key, value in pie_chart.items():
    #     print(f"{key}: {value}")
    return dict(sorted(pie_chart.items(), reverse=True))


def get_stack_chart(df:pd, dtype:int,isParent:bool):
    
    if (dtype == 1): # yearly 

        year_stack_chart = df.groupby(['IS_DEPOSIT','YEAR']).sum().drop(['CATEGORY', 'MONTH'],  axis = 1).sort_values(by='YEAR').reset_index()
        year_stack_chart['IS_DEPOSIT'] = year_stack_chart['IS_DEPOSIT'].replace({0: '소비', 1: '예금'})
        
        if(isParent):   
            #year_stack_chart = year_stack_chart.groupby(['YEAR',  'IS_DEPOSIT'])['AMOUNT'].sum().reset_index()
            # year_stack_chart['PERCENTAGE']  = (year_stack_chart['AMOUNT'] /year_stack_chart['AMOUNT'].sum() * 100).round(2)
            # YEAR 및 MONTH로 그룹화하고 각 IS_DEPOSIT의 AMOUNT 합산값을 가져옴
            total_amounts = year_stack_chart.groupby(['YEAR'])['AMOUNT'].transform('sum')

            # AMOUNT를 해당 월의 총 AMOUNT로 나누어 비율을 구함
            year_stack_chart['PERCENTAGE'] = (year_stack_chart['AMOUNT'] / total_amounts * 100).round(2)
            
            
            year_stack_chart.drop(['AMOUNT'], axis=1, inplace=True)
            year_stack_chart['PERCENTAGE'] = year_stack_chart['PERCENTAGE'].apply(lambda x: f'{x:.2f}')
            
        # year_stack_chart = year_stack_chart.to_dict(orient='list')
        year_stack_chart = year_stack_chart.to_dict(orient='index')
        #year_stack_chart = dict(sorted(year_stack_chart.items(), reverse=True))
        # print("===========stack chart===============")
        # for key, value in year_stack_chart.items():
        #      print(f"{key}: {value}")

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
        # print("===========before dividng stack chart===============")
        # print(month_stack_chart)
        # for key, value in month_stack_chart.to_dict(orient='index').items():
        #     print(f"{key}: {value}")
        #     pass

        if(isParent):
            # YEAR, MONTH 및 IS_DEPOSIT로 그룹화하고 AMOUNT의 합을 계산
            month_stack_chart = month_stack_chart.groupby(['YEAR', 'MONTH', 'IS_DEPOSIT'])['AMOUNT'].sum().reset_index()

            # YEAR 및 MONTH로 그룹화하고 각 IS_DEPOSIT의 AMOUNT 합산값을 가져옴
            total_amounts = month_stack_chart.groupby(['YEAR', 'MONTH'])['AMOUNT'].transform('sum')

            # AMOUNT를 해당 월의 총 AMOUNT로 나누어 비율을 구함
            month_stack_chart['PERCENTAGE'] = (month_stack_chart['AMOUNT'] / total_amounts * 100).round(2)


            #month_stack_chart['PERCENTAGE']  = (month_stack_chart['AMOUNT'] /month_stack_chart['AMOUNT'].sum() * 100)
            month_stack_chart.drop(['AMOUNT'], axis=1, inplace=True)     
            month_stack_chart['PERCENTAGE'] = month_stack_chart['PERCENTAGE'].apply(lambda x: f'{x:.2f}')
               
        #month_stack_chart = month_stack_chart.to_dict(orient='list')
        month_stack_chart['YEAR'] = month_stack_chart['YEAR'].astype(str) + '-' + month_stack_chart['MONTH'].astype(str).str.zfill(2)
        month_stack_chart.drop(['MONTH'],axis=1, inplace=True)


        month_stack_chart = month_stack_chart.to_dict(orient='index')
        # month_stack_chart = dict(sorted(month_stack_chart.items()))
        # print("===========stack chart===============")
        # for key, value in month_stack_chart.items():
        #     print(f"{key}: {value}")

        return month_stack_chart

def get_ratio_chart(child_id):
    #global child_id 
    # child_id = request.GET.get('child_id')
    # period = request.GET.get('period')
    # return_json = {}
    cursor = connection.cursor()
    #print(child_id)
    '''아이 나이'''
    cursor.execute("SELECT birthdate FROM Users where id = :id", {"id" : child_id})
    birthdate = cursor.fetchone()[0]
    current_date = datetime.now()
    age = current_date.year - birthdate.year - ((current_date.month, current_date.day) < (birthdate.month, birthdate.day))
    # print(f"나이: {age}세")

    '''모든 아이들'''
    
    all_child_query = """
        SELECT amount, category 
        FROM account_history 
        WHERE category not in ('예금' , '적금' , '리워드')
        AND TO_CHAR(created_date, 'YYYY-MM') BETWEEN :start_date AND :end_date
        """
    stdt, enddt = map(str, period.split('~'))
    cursor.execute(sql=all_child_query,params={"start_date" : stdt , "end_date":enddt})
    query_result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    all_df = pd.DataFrame(query_result, columns=columns)
    all_df.dropna(inplace = True)
    all_df.reset_index(drop=True, inplace = True)
    sum_df = all_df.groupby(['CATEGORY']).sum().reset_index()
    # mean_df = all_df.groupby(['CATEGORY']).mean().reset_index()
    # print("============sum_df===========")
    # print(sum_df)


    '''특정 자녀'''
    # query = "SELECT amount, category FROM account_history WHERE category not in ('예금' , '적금' , '리워드') and user_id = :child_id" 
    # params = {'child_id': child_id}
    cursor.execute(sql=get_ratio_query(),params= get_params(child_id=child_id,period=period))
    query_result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    child_df = pd.DataFrame(query_result, columns=columns)
    child_df.dropna(inplace = True)
    child_df.reset_index(drop=True, inplace = True)
    child_sum_df = child_df.groupby(['CATEGORY']).sum().reset_index()
    # print("============child_sum_df===========")
    # print(child_sum_df)

    '''상위비율구하기'''
    merged_data = child_sum_df.merge(sum_df, on='CATEGORY', suffixes=('_data1', '_data2'))
    # print("===========merged_data===========")
    # print(merged_data)
    # AMOUNT_data1를 AMOUNT_data2로 나누어서 새로운 열을 생성
    merged_data['RESULT'] = merged_data['AMOUNT_data1'] / merged_data['AMOUNT_data2']
    # print("===========merged_data===========")
    # print(merged_data)
    # 필요 없는 열 삭제
    merged_data.drop(['AMOUNT_data1', 'AMOUNT_data2'], axis=1, inplace=True)
    merged_data['RESULT']  = (100 -  merged_data['RESULT']*100).round(2) # 상위 몇 퍼센트인지 
    # print("merged_data!!===========")
    # print(merged_data)





    
    
    # child_sum_df['AMOUNT'] =  ( child_sum_df['AMOUNT'] * 100 / sum_df['AMOUNT'])
    # print(child_sum_df)
    # child_sum_df['AMOUNT']  = (100 -  child_sum_df['AMOUNT']).round(2) # 상위 몇 퍼센트인지 
    # print(child_sum_df['AMOUNT'])
    # child_sum_df = child_sum_df.sort_values(by=['CATEGORY'], ascending=True).reset_index() # category 내림차순으로 정렬
    # child_sum_df.drop(columns=['index'], axis = 1, inplace = True)
    # col = list(child_sum_df.columns)
    # print(f"=========== {child_id} 상위 ===============") # 년도별 월별..?
    # for i in range(child_sum_df.shape[0]):
    #     print( str(child_sum_df.iloc[i][col[0]]) + " 항목에서 상위 "+ str(child_sum_df.iloc[i][col[1]])+" % 소비" )
    
    #child_sum_df = child_sum_df.set_index('CATEGORY')['AMOUNT'].to_dict()#.to_dict(orient='index')
    #print(dict(sorted(child_sum_df.items())))
    #print(child_sum_df)
    cursor.close()
    #return_json={}
    #child_sum_df = dict(sorted(child_sum_df.items(), reverse=True))
    #print("============ child_sum_df =========")
    #print(child_sum_df['AMOUNT'])
    return merged_data['RESULT']
    return child_sum_df['AMOUNT']


  




  

def get_graph_parent(request):
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
    pie_chart = get_pie_chart(df=df, dtype=dtype, isParent = True,child_id=child_id)
    stack_chart = get_stack_chart(df=df, dtype=dtype, isParent = True)
    #ratio_chart = get_ratio_chart(child_id)
    #pie_chart['RATIO'] = ratio_chart['MY_DATA']

    return_json['PIE'] = pie_chart
    return_json['STACK'] = stack_chart

    # return_json['MY_DATA'] = rr['MY_DATA']
    # return_json['AGE'] = rr['AGE']
    #print(return_json)
    cursor.close()
    return JsonResponse(return_json, safe=False)



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
    