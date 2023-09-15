# KOOKCHILD-AI
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
