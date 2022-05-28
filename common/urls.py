from django.urls import path

from .views import *

app_name = 'common'

urlpatterns = [
    path('', index, name='index'),

    # 회원가입
    path('signup/', SignupView.as_view(), name='signup'),  # Json으로 회원가입 (react용)
    path('signup/comp/', signup_complete, name='signup_complete'),

    # 일반 로그인
    path('login/', LoginView.as_view(), name='login_main'),  # Json으로 로그인 (react용)
    path('login/test/', LoginTestView.as_view(), name='login_main_test'),  # HTML5로 로그인 (backend 테스트용)
    path('logout/', logout_main, name='logout_main'),


    # 아이디 중복 확인
    path('signup/check/id/', CheckID.as_view(), name='duplicate_id_check'),

    # 이메일 인증번호 확인
    path('signup/auth/email/', EmailAuth.as_view(), name='auth_email'),
    path('signup/auth/email/comp/', EmailAuthComplete.as_view(), name='auth_email_complete'),

]