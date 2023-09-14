from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse

def graph_api(request):
    
    # GET 요청에서 파라미터 추출
    child_id = request.GET.get('child_id')
    period = request.GET.get('period')
    type = request.GET.get('type')

    # 데이터 처리 또는 API 응답 생성
    # 예시로 JsonResponse를 사용하여 응답을 생성합니다.

    '''
    여기서 그래프 pandas 지지고 볶고 하기
    '''
    data = {
        'child_id': child_id,
        'period': period,
        'type': type,
        'message': 'API 요청이 성공적으로 처리되었습니다.',
    }



    #return JsonResponse(data)
