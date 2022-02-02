import json

from django.contrib import auth
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View

from .mail import email_auth_num

from common.models import User
from django.core.mail import EmailMessage


def index(request):
    return render(request, 'home.html')


# 회원가입을 진행하는 함수
def signup(request):
    # GET 방식 호출일 때
    if request.method == 'GET':
        return render(request, 'common/signup.html')
    # POST 방식 호출일 때
    elif request.method == 'POST':
        username = request.POST.get('username', None)  # 이름
        userid = request.POST.get('userid', None)  # 아이디
        password1 = request.POST.get('password1', None)  # 비밀번호
        password2 = request.POST.get('password2', None)  # 비밀번호(확인)
        email = request.POST.get('email', None)  # 이메일
        res_data = {}

        # 빈 칸 확인
        if not (username and userid and password1 and password2 and email):
            res_data['error'] = "입력하지 않은 칸이 있습니다."
        # 아이디 중복 확인
        if User.objects.filter(userid=userid).exists():  # 아이디 중복 체크
            messages.warning(request, '이미 존재하는 아이디입니다!')
            return render(request, 'common/signup.html')
        # 비밀번호 일치 여부 확인
        if password1 != password2:
            res_data['error'] = '비밀번호가 일치하지 않습니다.'
        else:
            # 이메일 인증번호 발송
            auth_num = email_auth_num()
            print(auth_num)
            EmailMessage(subject='이메일 인증 코드입니다.',
                         body=f'다음의 코드를 입력하세요\n{auth_num}',
                         to=[email]).send()

            user = User.objects.create_user(userid=userid, username=username, email=email,
                                            password=password1, auth_num=auth_num)
            user.save()
        return render(request, 'common/auth_email.html', {'userid': userid})


# 일반 로그인
def login_main(request):
    if request.method == 'POST':
        userid = request.POST['userid']
        password = request.POST['password']
        user = auth.authenticate(request, userid=userid, password=password)

        if user is None:
            print('userid 또는 password가 틀렸습니다.')
            return render(request, 'common/login.html', {'error': 'username 또는 password가 틀렸습니다.'})
        else:
            auth.login(request, user)
            return redirect('/')
    elif request.method == 'GET':
        return render(request, 'common/login.html')


# 일반 로그아웃
def logout_main(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('/')
    return render(request, 'home.html')


def duplicate_id_check(request):
    if request.method == 'POST':
        check_userid = request.POST.get('check_userid', None)  # 아이디
        print(check_userid)
        if User.objects.filter(userid=check_userid).exists():  # 아이디 중복 체크
            print('이미 존재하는 아이디입니다.')
            messages.warning(request, '이미 존재하는 아이디입니다!')
            return render(request, 'common/duplicate_id_check.html')
        else:
            print('사용 가능한 아이디입니다.')
            messages.warning(request, '사용 가능한 아이디입니다!')
            return render(request, 'common/duplicate_id_check.html')


# ++++++++++++++++++++++++++ JSON으로 회원가입/로그인 ++++++++++++++++++++++++++
# 회원가입
class SignupView(View):
    # POST 요청: 전달 받은 데이터를 DB에 저장
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']  # 이름
        userid = data['userid']  # 아이디
        password1 = data['password1']  # 비밀번호
        password2 = data['password2']  # 비밀번호(확인)
        email = data['email']  # 이메일
        # username = request.POST.get('username', None)  # 이름
        # userid = request.POST.get('userid', None)  # 아이디
        # password1 = request.POST.get('password1', None)  # 비밀번호
        # password2 = request.POST.get('password2', None)  # 비밀번호(확인)
        # email = request.POST.get('email', None)  # 이메일

        # 입력하지 않은 칸 확인
        if not (username and userid and password1 and password2 and email):
            return JsonResponse({'message': "There's a space that I didn't enter."}, status=400)
        # 아이디 중복 확인
        if User.objects.filter(userid=userid).exists():
            return JsonResponse({'message': 'This ID already exists.'}, status=400)
        # 비밀번호 비교
        if password1 != password2:
            return JsonResponse({'message': "The password doesn't match."}, status=400)

        # 이메일 인증번호 발송
        auth_num = email_auth_num()
        # print(auth_num)
        EmailMessage(subject='이메일 인증 코드입니다.',
                     body=f'다음의 코드를 입력하세요\n{auth_num}',
                     to=[email]).send()

        # 사용자 생성
        user = User.objects.create_user(
            username=username,
            userid=userid,
            password=password1,
            email=email,
            auth_num=auth_num
        )
        user.save()

        # 이메일 인증 페이지로 이동
        # return render(request, 'common/auth_email.html', {'userid': userid})
        return JsonResponse({'message': "Go to... '/signup/auth/email'"}, status=200)

    # GET 요청: common 테이블에 저장된 리스트를 출력(임시)
    def get(self, request):
        # return render(request, 'common/signup.html')
        return JsonResponse({'message': "Go to... '/signup'"}, status=200)


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
                    return JsonResponse({'message': "Go to... '/home'"}, status=200)
                else:
                    return JsonResponse({'message': "Enter invalid authentication information"}, status=401)
            else:
                return JsonResponse({'message': "Bad Request"}, status=400)
        except KeyError:
            return JsonResponse({'message': 'INVALID_KEYS'}, status=400)

    def get(self, request):
        return JsonResponse({'message': "Go to... '/login'"}, status=200)


# 인증번호 입력에 대한 처리
class Auth(View):
    def post(self, request):
        # 1) 입력한 정보를 전달받음
        data = json.loads(request.body)
        auth_num = data['auth_num']
        userid = data['userid']
        # auth_num = request.POST['auth_num']
        # userid = request.POST['userid']

        # 2) DB에 저장된 인증번호와 사용자의 입력을 비교
        if User.objects.filter(userid=userid).exists():
            user = User.objects.get(userid=userid)

            # 두 auth_num을 비교... 같으면 회원가입 성공
            if user.auth_num == auth_num:
                user.auth_num = None
                user.save()
                # return redirect('/common/signup/auth/email/comp')
                return JsonResponse({'message': "Go to... '/common/signup/auth/email/comp'"}, status=200)
            # 다르면 사용자 정보 삭제 후 다시 회원가입 진행
            else:
                user.delete()
                # return render(request, 'common/signup.html')
                return JsonResponse({'message': "Go to... '/common/signup'"}, status=200)
        else:
            # return render(request, 'common/signup.html')
            return JsonResponse({'message': "Go to... '/common/signup'"}, status=200)


# 이메일 인증 완료 페이지
def auth_email_complete(request):
    # return render(request, 'common/auth_email_complete.html')
    return JsonResponse({'message': "signup complete."}, status=200)

