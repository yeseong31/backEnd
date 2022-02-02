from django.urls import path
from django.contrib.auth import views as auth_views

from .views import *

app_name = 'common'

urlpatterns = [
    path('', index, name='index'),

    # 회원가입
    # path('signup/', signup, name='signup'),
    path('signup/', SignupView.as_view(), name='signup'),  # Json으로 회원가입 (react에서 사용)

    # 일반 로그인
    # path('login/', login_main, name='login_main'),
    path('logout/', logout_main, name='logout_main'),
    path('login/', LoginView.as_view(), name='login_main'),  # Json으로 로그인 (react에서 사용)

    # 아이디 중복 확인
    path('signup/check/id/', duplicate_id_check, name='duplicate_id_check'),
    # 이메일 인증번호 확인
    path('signup/auth/email', Auth.as_view(), name='auth_email'),
    path('signup/auth/email/comp', Auth.as_view(), name='auth_email'),
]