# KOOKCHILD-AI
현재 사용 중인 가상환경 python 버전

![KakaoTalk_20230915_212720139](https://github.com/KookChild/KOOKCHILD-AI/assets/76734572/39a141a5-7033-4a37-820d-4f8216d6ae09)


현재 환경에서 설치한 패키지를 알려주는 명령어

```
pip freeze
```
그 결과 설치되어있는 패키지들을 확인할 수 있습니다.
```
certifi==2018.11.29
chardet==3.0.4
defusedxml==0.5.0
Django==2.1.7
django-allauth==0.39.1
django-appconf==1.0.3
django-imagekit==4.0.2
idna==2.8
oauthlib==3.0.1
pilkit==2.0
Pillow==5.4.1
python3-openid==3.1.0
pytz==2018.9
requests==2.21.0
requests-oauthlib==1.2.0
six==1.12.0
urllib3==1.24.1
```
이제 이를 파일에 담아주어 같이 버젼관리를 해줌으로서 협업자에게 전달하게 됩니다.

이를 파일에 담아주기 위해서는
```
pip freeze > requirements.txt
```
다음이 같이 패키지의 내용들을 requirements.txt 에 담아줄 수 있다.
명령어를 실행한 폴더에 txt파일 생성됨.

그 후 함께 버젼관리를 해주면 협업자도 내가 무슨 패키지를 사용하였는지 확인이 가능합니다.

그렇다면 패키지를 하나씩 확인하면서 설치를 해야할까요?

다행히도 이를 한 번에 install 할 수 있습니다.
```
pip install -r requirements.txt
```
현재 없는 패키지만 빠르게 설치할 수 있습니다.

---

현재 사용중 오라클 버전 확인 명령어

![image](https://github.com/KookChild/KOOKCHILD-AI/assets/76734572/80060994-72e6-4771-ba8a-1b581faf207d)

---

테이블 정보를 그대로 models.py 로 불러오는 명령어

```
python manage.py inspectdb > bourne_users/models.py
```

참고 링크: [장고, 오라클연결](https://antilibrary.org/m/700)


맨 처음 실행시키면 다음과 같은 에러가 뜬다
```
django.db.utils.DatabaseError: ORA-12638: Credential retrieval failed
```
이는 처음 ORACLE을 설치할 때 admin 권한으로 설치하지 않아서 생긴 문제

해결 방법

1. Oracle 설치 경로 찾기

- Oracle Home으로 지정한 경로를 찾아 network\admin 폴더로 이동한다. 

(디폴트로 설치 했을 경우 : C:\app\사용자명\product\11.2.0\client_1\network\admin)

2. sqlnet.ora.rooh 파일 수정

sqlnet.ora 파일을 메모장으로 열어서 SQLNET.AUTHENTICATION_SERVICES= (NTS) <- 이부분을 주석처리한다.
```
# SQLNET.AUTHENTICATION_SERVICES= (NTS)
```
저장시에 권한문제가 생기면 바탕화면에 임시로 저장 후 해당 파일을 덮어씌우기해서 바꿔치기하면 된다.

