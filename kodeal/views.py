import json

from django.shortcuts import render

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
        user_text = request.POST['text_area'] + " with python code" # 질문 영역

        # OpenAI Codex의 반환값 전체를 받아옴
        response = question_to_response(user_text)

        # 반환값 중 질문에 대한 답변만 추출
        answer = extract_answer_sentences(response)

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
