import json
import re

from django.shortcuts import render
from nltk import sent_tokenize

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
        # user_code = request.POST['code_area']  # 코드 영역
        user_text = request.POST['text_area']    # 질문 영역

        # 파이썬 분야에 대한 질문에 한정하기 위함
        question = 'Python 3' + '\n' + user_text

        # OpenAI Codex의 반환값 전체를 받아옴
        response = question_to_response(question)
        # 반환값 중 질문에 대한 답변만 추출
        answer = extract_answer_sentences(response)

        # 답변 목록을 메모장으로 저장하여 문장 확인(테스트용)
        with open('answer_test_file.txt', 'w') as f:
            sentences = sent_tokenize(answer)
            for sentence in sentences:
                f.write(sentence + '\n')

        return render(request, 'common/qna_answer.html', {'answer': answer})
    else:
        return render(request, 'common/qna_main.html')


# blog의 question을 전달 받아 codex 답변(OpenAIObject 객체)을 return
def question_to_response(question):
    # codex 변환 과정
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=question,
        temperature=0.1,
        max_tokens=4000,    # Codex가 답할 수 있는 최대 문장 바이트 수 (text-davinci-code의 경우 2048B)
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

    # ———————————————————— 테스트 ————————————————————
    # 문장 앞뒤로 불필요한 문자 제거
    answer = remove_unnecessary_char(answer)
    # 콜론(:)을 만나면 개행 (프론트엔트에서 해결하는 것으로 변경)
    # answer = insert_a_newline_when_encountering_colons(answer)
    # 결과에 한글이 포함되어 있는지 확인
    answer = check_korean_answer(answer)

    # ————————————————————————————————————————————————

    return answer


# answer 문장 앞뒤로 불필요한 문자 제거
def remove_unnecessary_char(answer):
    answer = remove_first_colon(answer)
    answer = remove_two_newline_char(answer)
    return answer


# 결과로 전달되는 answer 문장에서 맨 앞의 개행 문자 전처리
def remove_two_newline_char(answer):
    return answer.strip()


# 첫 글자가 콜론(:)이라면 제거
def remove_first_colon(answer):
    if answer[0] == ':':
        return answer[2:]
    else:
        return answer


# 콜론(:)을 만나면 개행 문자 삽입 (사용하지 않음)
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


# 반환된 결과에 한글이 포함되는지 확인
# 단, "print('예시')"와 같이 코드로써 한글이 반환되는 경우는 제외해야 함
def check_korean_answer(answer):
    # 한글을 포함하는지 판별하는 정규식
    regex = re.compile(r'[가-힣ㄱ-ㅎㅏ-ㅣ]')

    for ans in answer:
        # 문장 내에 한글이 포함되어 있으면
        if regex.match(ans):
            break

    return answer
