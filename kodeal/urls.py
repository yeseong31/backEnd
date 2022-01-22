from django.urls import path

from .views import qna_main, index, qna_answer

app_name = 'kodeal'

urlpatterns = [
    # main page
    path('', index, name='index'),

    # QnA화면
    path('qna_main/', qna_main, name='qna_main'),
    path('qna_answer/', qna_answer, name='qna_answer'),
]