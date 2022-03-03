# coding: utf-8
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
import json
from django.core.serializers import serialize
from rest_framework import viewsets

from kodeal.views import question_to_answer
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

    def post(self, request):
        request = json.loads(request.body)
        question = request['question']
        userid = request['userid']

        # 전달 받은 아이디가 DB에 있으면
        if Login_User.objects.filter(userid=userid).exists():
            user = Login_User.objects.get(userid=userid)

            tmp = question_to_answer(question)
            answer = str(tmp['choices'][0]['text'])

            friend = User(question=question,
                          code=answer,
                          userid=user)
            friend.save()

            return JsonResponse({'answer': answer, 'status': 200}, status=200)
        # 전달받은 아이디가 DB에 없으면 400 에러
        else:
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
