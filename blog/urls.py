from rest_framework import routers
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:id>/', views.IndexView.as_view()),

    # QnA화면
    path('qna_main/', views.qna_main, name='qna_main'),
    path('qna_answer/', views.qna_answer, name='qna_answer'),

    # Question read page
    path('read/', views.read, name='read'),
]

router = routers.DefaultRouter()
