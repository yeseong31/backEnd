import json

from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View

from common.models import User

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
            user = User.objects.create_user(userid=userid, username=username, email=email, password=password1)
            user.save()
        return render(request, 'home.html', res_data)


# 회원가입을 진행하는 함수2
@method_decorator(csrf_exempt, name='dispatch')
def signup2(request):
    if request.method == 'POST':
        # 비밀번호 일치 시
        if request.POST['password1'] == request.POST['password2']:
            user = User.objects.create_user(
                username=request.POST['username'],
                password=request.POST['password1'],
                email=request.POST['email'],
            )
            auth.login(request, user)
            return redirect('/')  # 메인 페이지(index)로 이동
        # 비밀번호 불일치 시
        else:
            return render(request, 'common/signup.html')
    else:
        # 정상적인 회원가입 확인을 위해 로그인, 로그아웃 기능 추가
        form = UserCreationForm
        return render(request, 'common/signup.html', {'form': form})


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


# models.py에서 생성한 데이터를 주고 받고 저장하는 클래스(회원가입)
class SignupView(View):
    # POST 요청 시 userid와 password를 저장
    def post(self, request):
        data = json.loads(request.body)
        User.objects.create_user(
            username=data['username'],
            userid=data['userid'],
            password=data['password1'],
            email=data['email'],
        )
        return HttpResponse(status=200)

    # GET 요청 시 common 테이블에 저장된 리스트를 출력
    def get(self, request):
        user_data = User.objects.values()
        return JsonResponse({'users': list(user_data)}, status=200)


# 로그인
# class LoginView(View):
#     def post(self, request):
#         data = json.loads(request.body)
#
#         # Http request로 받은 json 파일을 통헤 테이블에 저장된 userid와 password를 비교
#         try:
#             if User.objects.filter(userid=data['userid']).exists():
#                 user = User.objects.get(userid=data['userid'])
#
#                 if user.password == data['password']:
#                     return HttpResponse(status=200)  # 200: OK
#                 else:
#                     return HttpResponse(status=401)  # 401: 인증 정보 부족으로 진행 X
#             else:
#                 return HttpResponse(status=400)  # 400: Bad request
#         except KeyError:
#             return JsonResponse({'message': 'INVALID_KEYS'}, status=400)





