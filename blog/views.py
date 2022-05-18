# coding: utf-8
import math
import ssl
import urllib
import urllib.request

from django.core.paginator import Paginator
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
import json
from django.core.serializers import serialize
from nltk import sent_tokenize
from rest_framework import viewsets

from config.my_settings import CLIENT_ID, CLIENT_SECRET
from kodeal.views import papago, extract_answer_sentences

from .serializer import EntrySerializer
from common.models import User as Login_User
from blog.models import User, Entry

from config import my_settings
import openai

openai.api_key = my_settings.OPENAI_CODEX_KEY
openai.Engine.list()


class IndexView(View):
    def get(self, request):
        # 로그인 한 사용자인지 확인
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

    # Codex 기능 수행 함수 (프론트엔드와 연동되어 실질적인 기능 수행)
    def post(self, request):
        request = json.loads(request.body)
        question = request['question']
        userid = request['userid']

        # 한글로 입력된 문장을 Papago API를 통해 번역 수행
        # 파이썬 분야에 대한 질문에 한정하기 위해 'Python 3' 문장 삽입
        translate_question = papago(question)
        pre_question = 'Python 3' + '\n' + translate_question + 'with code'

        # OpenAI Codex의 반환값 전체를 받아옴
        response = question_to_response(pre_question)
        # 반환값 중 질문에 대한 답변만 추출
        answer = extract_answer_sentences(response)

        # 전달 받은 아이디가 DB에 있으면
        if Login_User.objects.filter(userid=userid).exists():
            user = Login_User.objects.get(userid=userid)

            friend = User(question=question,
                          question_papago=translate_question,
                          code=answer,
                          userid=user,
                          star=5.0,
                          language='Python 3',
                          preprocess=response)
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
        translate_question = papago(question)
        pre_question = 'Python 3' + '\n' + translate_question + 'with code'

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
        friend = User(question=question,
                      question_papago=translate_question,
                      code=answer,
                      userid=user,
                      star=5.0,
                      language='Python 3',
                      preprocess=response)

        friend.save()

        return render(request, 'common/qna_answer.html', {'answer': answer})
    else:
        page = '1' if request.GET.get('page') is None else request.GET.get('page')
        question_list = User.objects.order_by('-time').all()

        # 페이징
        paginator = Paginator(question_list, 10)
        page_obj = paginator.get_page(page)

        # 시작 번호
        temp_end = int(math.ceil(page_obj.number / 10.0)) * 10
        start = temp_end - 9
        # 끝 번호
        total_page = math.ceil(len(question_list) / 10)
        end = temp_end if total_page > temp_end else total_page

        context = {'question_list': page_obj,
                   'start': start,
                   'end': end,
                   'total_page': total_page,
                   'page': page}

        return render(request, 'common/qna_main.html', context)


# blog의 question을 전달 받아 codex 답변(OpenAIObject 객체)을 return
def question_to_response(question):
    # codex 변환 과정
    response = openai.Completion.create(
        engine='text-davinci-002',  # 현재 Davinci 모델의 최신 버전(03.20 기준)
        prompt=question,
        temperature=0.1,
        max_tokens=2000,  # Codex가 답할 수 있는 최대 문장 바이트 수 (text-davinci-001의 경우 2048 Byte 였음)
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response


# Question Read Page (04/27)
def read(request):
    if request.method == 'GET':
        qid = request.GET.get('id')
        page = request.GET.get('page')
        question = get_object_or_404(User, pk=qid)

        context = {'question': question, 'page': page}
        return render(request, 'common/qna_read.html', context)
