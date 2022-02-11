import json
import re

from django.contrib import auth
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View

from .mail import email_auth_num

from common.models import User, UserAuth
from django.core.mail import EmailMessage


def index(request):
    return render(request, 'home.html')


# 로그아웃... 0211 쿠키 적용
def logout_main(request):
    if request.method == 'POST':
        response = render(request, 'home.html')
        response.delete_cookie('userid')
        response.delete_cookie('password')
        auth.logout(request)
        return redirect('/')
    return render(request, 'home.html')


# ++++++++++++++++++++++++++ 아이디 입력 및 중복확인 ++++++++++++++++++++++++++
class CheckID(View):
    def post(self, request):
        data = json.loads(request.body)
        check_userid = data['userid']
        # 중복되는 아이디가 DB에 존재한다면
        if User.objects.filter(userid=check_userid).exists():
            return JsonResponse({'message': 'This ID already exists.', 'status': 400}, status=400)
        # 사용 가능한 아이디라면
        else:
            return JsonResponse({'message': "It's a usable ID", 'status': 200}, status=200)

    def get(self, request):
        return JsonResponse({'message': "Go to... '/common/signup/check/id'", 'status': 200}, status=200)


# ++++++++++++++++++++++++++ 쿠키 기능을 포함한 로그인(HTML ver) ++++++++++++++++++++++++++
def login_with_cookie(request):
    # 해당 cookie에 값이 없으면 return None
    if request.COOKIES.get('userid') is not None:
        userid = request.COOKIES.get('userid')
        password = request.COOKIES.get('password')
        user = auth.authenticate(request, userid=userid, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            return render(request, 'common/login.html')
    elif request.method == 'POST':
        userid = request.POST['userid']
        password = request.POST['password']
        # 해당 user가 있으면 userid, 없으면 None
        user = auth.authenticate(request, userid=userid, password=password)
        if user is not None:
            auth.login(request, user)
            if request.POST.get('keep_login'):
                response = render(request, 'kodeal/index.html')
                response.set_cookie('userid', userid)
                response.set_cookie('password', password)
                return response
            return redirect('/')
        else:
            return render(request, 'common/login.html', {'error': 'username or password is incorrect}'})
    elif request.method == 'GET':
        return render(request, 'common/login.html')
    return render(request, 'common/login.html')


# ++++++++++++++++++++++++++ JSON으로 회원가입/로그인 ++++++++++++++++++++++++++
# 회원가입
class SignupView(View):
    # POST 요청: 전달 받은 데이터를 DB에 저장
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']  # 이름
        userid = data['userid']  # 아이디
        password1 = data['password']  # 비밀번호
        email = data['email']  # 이메일
        # username = request.POST.get('username', None)  # 이름
        # userid = request.POST.get('userid', None)  # 아이디
        # password1 = request.POST.get('password', None)  # 비밀번호
        # email = request.POST.get('email', None)  # 이메일

        # 입력하지 않은 칸 확인
        if not (username and userid and password1 and email):
            return JsonResponse({'message': "There's a space that I didn't enter.", 'status': 400}, status=400)
        # 비밀번호 비교
        # if password1 != password2:
        #     return JsonResponse({'message': "The password doesn't match.", 'status': 400}, status=400)

        # 사용자 생성
        user = User.objects.create_user(
            username=username,
            userid=userid,
            password=password1,
            email=email
        )
        user.save()

        # 이메일 인증 페이지로 이동
        # return render(request, 'common/auth_email.html', {'userid': userid})
        return JsonResponse({'message': "Go to... '/common/signup/auth/email'", 'status': 200}, status=200)

    # GET 요청: common 테이블에 저장된 리스트를 출력(임시)
    def get(self, request):
        # return render(request, 'common/signup.html')
        return JsonResponse({'message': "Go to... '/common/signup'", 'status': 200}, status=200)


# 로그인
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        userid = data['userid']
        password = data['password']
        # userid = request.POST['userid']
        # password = request.POST['password']

        try:
            # 해당 아이디의 사용자가 존재한다면
            if User.objects.filter(userid=userid).exists():
                user = User.objects.get(userid=userid)
                # 입력한 비밀번호가 사용자의 비밀번호와 일치한다면
                if user.password == password:
                    # 로그인 완료
                    auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    # return redirect('/')
                    return JsonResponse({'message': "Go to... '/home'",
                                         'userid': user.userid,
                                         'username': user.username,
                                         'email': user.email,
                                         'status': 200}, status=200)
                # 그렇지 않다면 400 Error
                return JsonResponse({'message': "Enter invalid authentication information", 'status': 401}, status=401)
            else:
                return JsonResponse({'message': "Bad Request", 'status': 400}, status=400)
        except KeyError:
            return JsonResponse({'message': 'INVALID_KEYS', 'status': 400}, status=400)

    def get(self, request):
        # return render(request, 'common/login.html')
        return JsonResponse({'message': "Go to... '/login'", 'status': 200}, status=200)


# ++++++++++++++++++++++++++ 이메일 인증 확인 ++++++++++++++++++++++++++
class EmailAuth(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        # 이메일이 유효하지 않은 형태라면
        # regex = re.compile("^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+[.][a-zA-Z0-9-.]+$")

        # print(regex.match('yeseong31@naver.com'))
        # print(regex.match('ex@ex'))

        if email == '':
            return JsonResponse({'message': 'KEY_ERROR', 'status': 400}, status=400)
        # if regex.match(email) is None:
        #     return JsonResponse({'message': 'This email is not valid', 'status': 400}, status=400)

        # 유효한 이메일이라면 인증번호 발송
        auth_num = email_auth_num()
        EmailMessage(subject='이메일 인증 코드입니다.',
                     body=f'아래의 코드를 입력하세요!!\n\n{auth_num}',
                     to=[email]).send()

        # 인증번호 전용 사용자 생성
        if UserAuth.objects.filter(email=email):
            user_auth = UserAuth.objects.get(email=email)
            user_auth.auth_num = auth_num
        else:
            user_auth = UserAuth.objects.create(
                email=email,
                auth_num=auth_num
            )
        user_auth.save()
        return JsonResponse({'message': "I sent the authentication number to the email you entered.\n"
                                        "Go to... '/common/signup/auth/email'",
                             'email': email, 'status': 200}, status=200)

    def get(self, request):
        return JsonResponse({'message': "Go to... '/common/signup/auth/email'", 'status': 200}, status=200)


class EmailAuthComplete(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        auth_num = data['auth_num']

        # DB에 해당 이메일이 저장되어 있는지 살핌
        if UserAuth.objects.filter(email=email).exists():
            user_auth = UserAuth.objects.get(email=email)

            # 두 auth_num을 비교... 같으면 회원가입 성공
            if user_auth.auth_num == auth_num:
                user_auth.auth_num = None
                user_auth.save()
                return JsonResponse({'message': "Go to... '/common/signup/auth/email/comp'", 'status': 200}, status=200)
            # 두 auth_num이 다르다면 사용자가 잘못 입력했음을 알려줌
            else:
                return JsonResponse({'message': 'This authentication number is not valid', 'status': 400}, status=400)
        # DB에 해당 이메일이 저장되어 있지 않으면 회원가입 페이지에서 이메일을 다시 입력하게끔 조치
        else:
            return JsonResponse({'message': "This email is not valid\n"
                                            "Go to... '/common/signup'", 'status': 400}, status=400)

    def get(self, request):
        return JsonResponse({'message': "Go to... '/common/signup/auth/email/comp'", 'status': 200}, status=200)


# 이메일 인증 페이지
def auth_email(request):
    return render(request, 'common/auth_email.html')
    # return JsonResponse({'message': "Go to... '/common/auth/email'", 'status': 200}, status=200)


# 이메일 인증 완료 페이지
def auth_email_complete(request):
    return render(request, 'common/auth_email_complete.html')
    # return JsonResponse({'message': "signup complete.", 'status': 200}, status=200)


# 회원가입 완료 페이지
def signup_complete(request):
    return render(request, 'common/signup_complete.html')
    # return JsonResponse({'message': "signup complete.", 'status': 200}, status=200)
