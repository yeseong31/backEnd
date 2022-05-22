from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from blog.models import Keywords
from common.models import User, Profile


def index(request):
    if request.method == 'POST':
        userid = request.POST.get('userid', None)

        # 해당 userid를 가지는 사용자가 존재한다면
        if User.objects.filter(userid=userid).exists():
            user = User.objects.get(userid=userid)
            # 마이페이지에 대한 정보(이미지)가 있다면
            if Profile.objects.filter(userid=userid).exists():
                profile = Profile.objects.get(userid=userid)
                context = {
                    'image': profile.path,
                    'info': {
                        'email': user.email,
                        'questionCount': 0
                    },
                    'keywords': 0
                }
            # 마이페이지에 대한 정보가 없으므로 빈 화면 출력
            else:
                context = None
            return render(request, 'mypage/index.html', context)

        # 해당 userid를 가지는 사용자가 없으므로 에러 반환
        else:
            return JsonResponse({'message': 'This ID does not exist.', 'status': 400}, status=400)
