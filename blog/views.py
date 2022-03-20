# coding: utf-8
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
import json
from django.core.serializers import serialize
from rest_framework import viewsets

from kodeal.views import question_to_response, extract_answer_sentences, papago
from .models import User, Entry
from common.models import User as Login_User
from .serializer import EntrySerializer

from config import my_settings                        # 2.12 추가
import openai                                       # 2.12 추가

openai.api_key = my_settings.OPENAI_CODEX_KEY       # 2.12 추가
openai.Engine.list()                                # 2.12 추가.


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
