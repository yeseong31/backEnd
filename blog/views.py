# coding: utf-8
import ssl
import urllib
import urllib.request

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
import json
from django.core.serializers import serialize
from nltk import sent_tokenize
from rest_framework import viewsets

from config.my_settings import CLIENT_ID, CLIENT_SECRET
from .models import User, Entry
from .serializer import EntrySerializer

from common.models import User as Login_User
from blog.models import User

from config import my_settings  # 2.12 추가
import openai  # 2.12 추가

openai.api_key = my_settings.OPENAI_CODEX_KEY  # 2.12 추가
openai.Engine.list()  # 2.12 추가


class IndexView(View):
    def get(self, request):
        # 로그인 한 사용자인지 확인
        # data = json.loads(request.body)
        # userid = data['userid']
        userid = request.GET.get('userid')

        if Login_User.objects.filter(userid=userid).exists():
            user = Login_User.objects.get(userid=userid)

            # 해당 userid에 대한 '질문 목록'을 넘겨줘야 함
            questions = User.objects.filter(userid=user).order_by('time')
            data = json.loads(serialize('json', questions))
            return JsonResponse({'items': data, 'status': 200}, status=200)

        # 만약 서비스 이용자가 아니라면 400 error
        else:
            return JsonResponse({'message': 'The user id does not exist.', 'status': 400}, status=400)

    # Codex 기능 수행 함수 (프론트엔드와 연동되는 실질적인 기능 담당)
    def post(self, request):
        request = json.loads(request.body)
        question = request['question']
        userid = request['userid']

        # 한글로 입력된 문장을 Papago API를 통해 번역 수행
        # 파이썬 분야에 대한 질문에 한정하기 위해 'Python 3' 문장 삽입
        pre_question = 'Python 3' + '\n' + papago(question)

        # OpenAI Codex의 반환값 전체를 받아옴
        response = question_to_response(pre_question)
        # 반환값 중 질문에 대한 답변만 추출
        answer = extract_answer_sentences(response)

        # 전달 받은 아이디가 DB에 있으면
        if Login_User.objects.filter(userid=userid).exists():
            user = Login_User.objects.get(userid=userid)

            friend = User(question=question, code=answer, userid=user)
            friend.save()

            return JsonResponse({'answer': answer, 'status': 200}, status=200)
        # 전달받은 아이디가 DB에 없으면 400 에러
        else:
            # 테스트 데이터 삽입
            user = Login_User.objects.get(userid='testid')
            friend = User(question=question, code=answer, userid=user)
            friend.save()

            return JsonResponse({'message': 'The user id does not exist.', 'status': 400}, status=400)

    def put(self, request):
        request = json.loads(request.body)
        id = request['id']
        question = request['question']
        code = request['code']

        friend = get_object_or_404(User, pk=id)
        friend.question = question
        friend.code = code
        friend.save()
        return HttpResponse(status=200)

    def delete(self, request):
        request = json.loads(request.body)
        id = request['id']
        friend = get_object_or_404(User, pk=id)
        friend.delete()
        return HttpResponse(status=200)


class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer


# 03/31 부로 kodeal 디렉터리의 내용을 blog 디렉터리로 통합

# 파파고 api 함수 - 3.20
def papago(text):
    client_id = CLIENT_ID  # 개발자센터에서 발급받은 Client ID 값 (my_settings.py 참고)
    client_secret = CLIENT_SECRET  # 개발자센터에서 발급받은 Client Secret 값 (my_settings.py 참고)
    encText = urllib.parse.quote(text)
    data = "source=ko&target=en&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    context = ssl._create_unverified_context()
    response = urllib.request.urlopen(request, data=data.encode("utf-8"), context=context)
    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read()
        # Papago API의 반환값 중에서 "translatedText"에 해당하는 값만 추출해야 함
        return extract_question_sentences(response_body.decode('utf-8'))
    else:
        print("Error Code:" + rescode)
        return 'ERROR'


# main page
def index(request):
    return render(request, 'home.html')


# qna
def qna_answer(request):
    return render(request, 'common/qna_answer.html')


# qna action (백엔드)
def qna_main(request):
    if request.method == 'POST':
        question = request.POST['text_area']  # 질문 영역 (03.20 수정: user_text → question 으로 이름 변경)

        # 한글로 입력된 문장을 Papago API를 통해 번역 수행
        # 파이썬 분야에 대한 질문에 한정하기 위해 'Python 3' 문장 삽입
        pre_question = 'Python 3' + '\n' + papago(question) + 'with code'

        # OpenAI Codex의 반환값 전체를 받아옴
        response = question_to_response(pre_question)
        # 반환값 중 질문에 대한 답변만 추출
        answer = extract_answer_sentences(response)

        # 답변 목록을 메모장으로 저장하여 문장 확인(테스트용 파일 생성)
        with open('answer_test_file.txt', 'w') as f:
            sentences = sent_tokenize(answer)
            for sentence in sentences:
                f.write(sentence + '\n')

        # 테스트 데이터 삽입
        user = Login_User.objects.get(userid='testid')
        friend = User(question=question, code=answer, userid=user)
        friend.save()

        return render(request, 'common/qna_answer.html', {'answer': answer})
    else:
        return render(request, 'common/qna_main.html')


# blog의 question을 전달 받아 codex 답변(OpenAIObject 객체)을 return
def question_to_response(question):
    # codex 변환 과정
    response = openai.Completion.create(
        engine="text-davinci-002",  # 현재 Davinci 모델의 최신 버전(03.20 기준)
        prompt=question,
        temperature=0.1,
        max_tokens=4000,  # Codex가 답할 수 있는 최대 문장 바이트 수 (text-davinci-001의 경우 2048 Byte 였음)
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response


# Codex의 입력으로 넣을 문장을 번역한 결과(Papago) 중에서 사용자의 질문에 해당하는 부분만 추출하는 함수
def extract_question_sentences(response):
    json_object = json.loads(response)
    return json_object['message']['result']['translatedText']


# Codex로부터 반환된 answer 값 전체 중에서 사용자의 질문에 대한 답변만 추출하는 함수
def extract_answer_sentences(response):
    # 반환된 response 중에서 질문에 대한 답변이 포함된 'choices' 부분만 get
    choices = json.dumps(*response['choices'])

    # 위의 과정에서 choices의 값은 str 타입이기 때문에 JSON 형태로 변환해야 함
    json_choices = json.loads(choices)

    # JSON 형태로 변환된 문자열 중 키가 'text'인 값을 return
    answer = json_choices['text']

    # 전처리 과정을 거친 결과 반환
    return perform_preprocessing(answer)


# ※※※ 전처리 기능을 총괄하는 함수 ※※※
def perform_preprocessing(answer):
    # 문장 앞뒤로 불필요한 문자 제거
    answer = remove_unnecessary_char(answer)

    return answer


# answer 문장 앞뒤로 불필요한 문자 제거
def remove_unnecessary_char(sentence):
    # 첫 글자가 콜론(:)이라면 제거
    def remove_first_colon(answer):
        if answer[0] == ':':
            return answer[2:]
        else:
            return answer

    # 결과로 전달되는 answer 문장에서 맨 앞의 개행 문자 전처리
    def remove_two_newline_char(answer):
        return answer.strip()

    sentence = remove_first_colon(sentence)
    sentence = remove_two_newline_char(sentence)
    return sentence
