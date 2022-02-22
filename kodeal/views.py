import ctypes
import os

from django.http import JsonResponse
from django.shortcuts import render

from common.models import User
from config import my_settings

import openai

# OpenAI API 키, 항상 비워놓고 push하기
openai.api_key = my_settings.OPENAI_CODEX_KEY
openai.Engine.list()


# main page
def index(request):
    return render(request, 'home.html')


# qna
def qna_answer(request):
    return render(request, 'common/qna_answer.html')


# qna action
def qna_main(request):
    if request.method == 'POST':
        user_code = request.POST['code_area']  # 코드 영역
        user_text = request.POST['text_area']  # 질문 영역

        response = question_to_answer(user_text)
        return render(request, 'common/qna_answer.html', {'response': response})
    else:
        # 로그인 한 상태라면...
        # user = User.objects.get(userid=request.session.get('userid_session', False))
        # ctypes.windll.user32.MessageBoxW(0, f'지금 로그인 중인 사용자: {user.userid}', '로그인 확인 창          ')
        return render(request, 'common/qna_main.html')


# blog의 question을 전달 받아 codex 답변을 return 해주는 함수
def question_to_answer(question):
    # codex 변환 과정
    response = openai.Completion.create(
        engine="text-davinci-001",
        prompt=question,
        temperature=0.7,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response
