from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request):
    if request.method == 'POST':
        return HttpResponse("마이페이지 테스트")
