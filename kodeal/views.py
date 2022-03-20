import json

from django.shortcuts import render

from config import my_settings

import openai
import os
import sys
import urllib.request
import ssl

# OpenAI API 키, 항상 비워놓고 push하기
openai.api_key = my_settings.OPENAI_CODEX_KEY
openai.Engine.list()

# 파파고 api 함수 - 3.20
def papago(a):
    text = a
    client_id = "Client ID 값" # 개발자센터에서 발급받은 Client ID 값
    client_secret = "Client Secret 값" # 개발자센터에서 발급받은 Client Secret 값
    encText = urllib.parse.quote(a)
    data = "source=ko&target=en&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)   
    context = ssl._create_unverified_context()
    response = urllib.request.urlopen(request, data=data.encode("utf-8"), context=context)
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        print(response_body.decode('utf-8'))
    else:
        print("Error Code:" + rescode)


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
        user_text = request.POST['text_area'] + " with python code" # 질문 영역

        # OpenAI Codex의 반환값 전체를 받아옴
        response = question_to_response(user_text)
        # 반환값 중 질문에 대한 답변만 추출
        answer = extract_answer_sentences(response)

        # ———————————————————— 테스트 ————————————————————
        # 앞뒤 개행 문자 제거
        answer = remove_two_newline_char(answer)
        # 맨 앞 글자가 콜론(:)이라면 제거
        answer = remove_first_colon(answer)
        # 콜론(:)을 만나면 개행
        answer = insert_a_newline_when_encountering_colons(answer)

        # ————————————————————————————————————————————————

        # 답변 목록을 메모장으로 저장하여 문장 확인(테스트용)
        with open('answer_test_file.txt', 'w') as f:
            f.write(answer)

        return render(request, 'common/qna_answer.html', {'response': answer})
    else:
        return render(request, 'common/qna_main.html')


# blog의 question을 전달 받아 codex 답변(OpenAIObject 객체)을 return
def question_to_response(question):
    # codex 변환 과정
    response = openai.Completion.create(
        engine="text-davinci-001",
        prompt=question,
        temperature=0.1,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response


# Codex로부터 반환된 answer 값 전체 중에서 사용자의 질문에 대한 답변만 추출하는 함수
def extract_answer_sentences(response):
    # 반환된 response 중에서 질문에 대한 답변이 포함된 'choices' 부분만 get
    choices = json.dumps(*response['choices'])

    # 위의 과정에서 choices의 값은 str 타입이기 때문에 JSON 형태로 변환해야 함
    json_choices = json.loads(choices)

    # JSON 형태로 변환된 문자열 중 키가 'text'인 값을 return
    answer = json_choices['text']

    print(answer)
    return answer


# 결과로 전달되는 answer 문장에서 맨 앞의 개행 문자 두 개 제거
def remove_two_newline_char(answer):
    return answer.strip()


# 첫 글자가 콜론(:)이라면 제거
def remove_first_colon(answer):
    if answer[0] == ':':
        return answer[2:]
    else:
        return answer


# 콜론(:)을 만나면 개행 문자 삽입
def insert_a_newline_when_encountering_colons(answer):
    result = []
    # 문장 내의 글자 하나하나를 살핌
    for i, c in enumerate(answer):
        result.append(c)
        # 만약 콜론 발견 시 개행 문자도 같이 삽입
        if c == ':':
            result.append('\n')

    # 생성된 결과 리스트를 문자열로 반환
    return ''.join(map(str, result))
