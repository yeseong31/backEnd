# coding: utf-8
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
import json
from django.core.serializers import serialize
import django_filters
from rest_framework import viewsets, filters

from .models import User, Entry
from .serializer import UserSerializer, EntrySerializer


class IndexView(View):

    def get(self, request):
        friends = User.objects.all().order_by('-id')
        data = json.loads(serialize('json', friends))
        return JsonResponse({'items': data})

    def post(self, request):
        if request.META['CONTENT_TYPE'] == "application/json":
            request = json.loads(request.body)
            friend = User(question=request['question'],
                          code=request['code'],
                          time=request['time'],)
        else:
            friend = User(question=request.POST['question'],
                          code=request.POST['code'],
                          time=request.POST['time'],)
        friend.save()
        return HttpResponse(status=200)

    def put(self, request):
        request = json.loads(request.body)
        id = request['id']
        question = request['question']
        code = request['code']
        time = request['time']
        friend = get_object_or_404(User, pk=id)
        friend.question = question
        friend.time = time
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
