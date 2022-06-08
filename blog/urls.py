from rest_framework import routers
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:id>', views.IndexView.as_view()),

    # 03/31 부로 kodeal 디렉터리의 내용을 blog 디렉터리로 통합

    # 05.22 keyward
    # path('key_word/', views.key_word, name='key_word'),

    # QnA화면
    path('qna_main/', views.qna_main, name='qna_main'),
    path('qna_answer/', views.qna_answer, name='qna_answer'),

    # Question read page
    path('read/', views.read, name='read'),
]

router = routers.DefaultRouter()
