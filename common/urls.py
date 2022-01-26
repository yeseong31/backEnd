from django.urls import path
from django.contrib.auth import views as auth_views

from .views import *

app_name = 'common'

urlpatterns = [
    path('', index, name='index'),

    # 회원가입
    path('signup/', signup, name='signup'),
    path('signup2/', SignupView.as_view()),  # Json으로 회원가입

    # 일반 로그인
    path('login/', login_main, name='login_main'),
    path('logout/', logout_main, name='logout_main'),
    # path('login2/', LoginView.as_view()),  # Json으로 로그인

    # 아이디 중복 확인
    path('signup/check/id/', duplicate_id_check, name='duplicate_id_check'),
]