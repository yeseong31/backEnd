from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request):
    if request.method == 'POST':
        userid = request.POST.get('userid', None)

        return HttpResponse("마이페이지 테스트")
