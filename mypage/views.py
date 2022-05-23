import collections

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from blog.models import Keywords
from blog.models import User as Question
from common.models import User, Profile


def index(request):
    if request.method == 'POST':
        userid = request.POST.get('userid', None)

        # 해당 userid를 가지는 사용자가 존재한다면
        if User.objects.filter(userid=userid).exists():
            user = User.objects.get(userid=userid)

            # user의 질문 수 계산
            question_count = count_questions(user)
            # user의 키워드 빈도 수 계산
            keyword_cnt_info = check_freq_keyword(user)

            # 마이페이지에 대한 정보(이미지)가 있다면
            path = None
            if Profile.objects.filter(userid=userid).exists():
                path = Profile.objects.get(userid=userid).path

            context = {
                'image': path,
                'info': {
                    'email': user.email,
                    'questionCount': question_count
                },
                'keywords': keyword_cnt_info
            }

            # print(context)
            # return render(request, 'mypage/index.html', context)
            return JsonResponse({'context': context, 'status': 200}, status=200)

        # 해당 userid를 가지는 사용자가 없으므로 에러 반환
        else:
            return JsonResponse({'message': 'This ID does not exist.', 'status': 400}, status=400)


def count_questions(user):
    questions_obj = Question.objects.filter(userid=user).all()
    return len(questions_obj)


# 전달받은 user의 키워드 빈도 수 계산
def check_freq_keyword(user):
    keywords_obj = Keywords.objects.filter(userid=user).all()

    keyword_list = []
    for keyword_obj in keywords_obj:
        target = keyword_obj.keyword
        keyword_list.append(target)

    result = collections.Counter(keyword_list).most_common(10)
    # print(result)
    return result


# 마이페이지에 사용자 키워드 통계 출력
def calcul_user_keyword_statistics():
    pass
