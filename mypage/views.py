import collections
import json
import os.path
from datetime import datetime

import boto3
import numpy as np
from django.http import HttpResponse, JsonResponse

from blog.models import Keywords
from blog.models import User as Question
from common.forms import FileUploadForm
from common.models import User, Profile
from config import my_settings


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def index(request, userid):
    # 마이페이지 접근
    if request.method == 'GET':
        # 해당 userid를 가지는 사용자가 존재한다면
        if User.objects.filter(userid=userid).exists():
            user = User.objects.get(userid=userid)

            # user의 질문 수 계산
            question_count = count_all_questions(user)
            # user의 키워드 빈도 수 계산
            keyword_cnt_info = check_freq_keyword(user)

            img = None

            # 마이페이지에 대한 정보(이미지)가 있다면 S3에서 이미지 다운로드
            if Profile.objects.filter(userid=userid).exists():

                # 출발지 (S3 이미지 경로) (DB에 저장된 경로에는 큰따옴표가 붙어 있어 이를 슬라이싱으로 제거하였음)
                src_path = json.dumps(str(Profile.objects.get(userid=userid).img))[1:-1]
                print(f'src_path: {src_path}')
                # 목적지 (프로젝트 내 이미지 저장 경로)
                dest_path = 'media/'
                print(f'dest_path: {dest_path}')
                # 파일 이름
                file_name = os.path.basename(src_path)
                print(f'file_name: {file_name}')

                img = my_settings.AWS_S3_BUCKET_LINK + src_path

            # 잔디 기능 구현: default 값은 현재 연월
            year = datetime.today().year
            print(f'잔디 기능 구현...year: {year}')
            month = datetime.today().month
            print(f'잔디 기능 구현...month: {month}')

            tmp = number_of_question(userid, year, month)
            if tmp is None:
                tmp = 0
            my_grass = {month: tmp}

            context = {
                'info': {
                    'email': user.email,
                    'questionCount': question_count,
                    'image': img,
                    'username': user.username
                },
                'keywords': keyword_cnt_info,
                'grass': my_grass
            }

            # return render(request, 'mypage/index.html', context)
            return JsonResponse({'context': context, 'status': 200}, status=200)

        # 해당 userid를 가지는 사용자가 없으므로 에러 반환
        else:
            return JsonResponse({'message': 'This ID does not exist.', 'status': 401}, status=401)

    # 사용자 프로필 등록
    elif request.method == 'POST':
        img = request.FILES['img']

        # 사용자가 있다면
        if User.objects.filter(userid=userid).exists():
            user = User.objects.get(userid=userid)

            # 이미 등록된 이미지가 있다면
            if Profile.objects.filter(userid=userid).exists():
                # DB에 존재하는 이미지 Get
                target = Profile.objects.get(userid=userid)

                # S3 Bucket에 존재하는 이미지 삭제
                # (... 적용 미정 ...)

                # DB에 존재하는 이미지 삭제
                target.delete()

            # 새로운 이미지 등록
            profile_upload = Profile(
                userid=user,
                img=img
            )
            profile_upload.save()

            # 출발지 (S3 이미지 경로) (DB에 저장된 경로에는 큰따옴표가 붙어 있어 이를 슬라이싱으로 제거하였음)
            # src_path = 'media/' + img_name
            # print(f'src_path: {src_path}')
            # # 목적지 (프로젝트 내 이미지 저장 경로)
            dest_path = json.dumps(str(Profile.objects.get(userid=userid).img))[1:-1]
            print(f'dest_path: {dest_path}')
            # # 파일 이름
            # file_name = os.path.basename(src_path)
            # print(f'file_name: {file_name}')

            try:
                # s3 객체 생성
                s3 = boto3.resource(
                    's3',
                    aws_access_key_id=my_settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=my_settings.AWS_SECRET_ACCESS_KEY
                )
                # s3에 이미지 추가
                s3.Bucket(my_settings.AWS_STORAGE_BUCKET_NAME) \
                    .put_object(Key=dest_path, Body=img, ContentType='image/jpg')

            except:
                # S3 ERROR가 발생하고 있지만, S3에 이미지 저장은 잘 되고 있으므로 일단은 정상 진행되게끔...
                # 에러 발생 이유는 아직 자세히 알지 못함...
                print('S3 ERROR!!!')
                return JsonResponse({'message': "S3 ERROR... However, the image has been saved successfully, "
                                                "so continue", 'status': 200}, status=200)
                # return JsonResponse({'message': "S3 ERROR!", 'status': 400}, status=400)

            # return redirect('/mypage/profile')
            return JsonResponse({'message': "Success", 'status': 200}, status=200)

        else:
            return JsonResponse({'message': "This User doesn't exist", 'status': 400}, status=400)


# 해당 사용자의 모든 질문의 수를 카운트
def count_all_questions(user):
    return len(Question.objects.filter(userid=user).all())


# 전달받은 user의 키워드 빈도 수 계산
def check_freq_keyword(user):
    keywords_obj = Keywords.objects.filter(userid=user).all()

    keyword_list = []
    for keyword_obj in keywords_obj:
        target = keyword_obj.keyword
        keyword_list.append(target)

    result = []
    for cnt in collections.Counter(keyword_list).most_common(10):
        result.append(list(cnt))
    # print(f'result = {result}')
    return sorted(result, key=lambda x: x[1], reverse=True)  # 키워드 빈도수, 사전순 정렬


# 연 단위 사용자 질문 횟수 카운트
def questions_per_year(request, userid, year):
    if request.method == 'GET':
        result = {}
        for month in range(1, 13):
            tmp = number_of_question(userid, year, month)
            if tmp is None:
                continue
            result[month] = tmp
        return JsonResponse({'result': result, 'status': 200}, status=200)
    else:
        return JsonResponse({'message': 'invalid request', 'status': 400}, status=400)


# 월 단위 사용자 질문 횟수 카운트
def questions_per_month(request, userid, year, month):
    if request.method == 'GET':
        tmp = number_of_question(userid, year, month)
        if tmp is None:
            tmp = 0
        result = {month: tmp}
        return JsonResponse({'result': result, 'status': 200}, status=200)
    else:
        return JsonResponse({'message': 'invalid request', 'status': 400}, status=400)


# 일 단위 사용자 질문 횟수 및 정보 확인
def questions_per_day(request, userid, year, month, day):
    if request.method == 'GET':
        # 사용자가 없다면 에러 메시지와 함께 그대로 return
        if not User.objects.filter(userid=userid).exists():
            return JsonResponse({'message': "This User doesn't exist", 'status': 400}, status=400)

        target_questions = find_target_questions(userid, year, month, day)

        questions = {}
        for target_question in target_questions:
            h, m, s = target_question.time.hour, target_question.time.minute, target_question.time.second

            # 시간 전처리 (한 자리수 -> 두 자리수)
            h = str(h) if h >= 10 else '0' + str(h)
            m = str(h) if m >= 10 else '0' + str(m)
            s = str(s) if s >= 10 else '0' + str(s)

            key = h + ':' + m + ':' + s
            questions[key] = target_question.question
        print(questions)
        return JsonResponse({'result': questions, 'status': 200}, status=200)

    else:
        return JsonResponse({'message': 'invalid request', 'status': 400}, status=400)


# 해당 연월에 해당하는 사용자의 질문 수 계산
def number_of_question(userid, year, month):
    # 사용자가 없다면 에러 메시지와 함께 그대로 return
    if not User.objects.filter(userid=userid).exists():
        return JsonResponse({'message': "This User doesn't exist", 'status': 400}, status=400)

    # 해당 사용자의 전체 질문들 중 원하는 시간대(월 단위)의 질문들로 필터링
    target_questions = find_target_questions(userid, year, month)
    if not target_questions.exists():
        return None

    day_cnt_list = collections.defaultdict(int)

    # 질문들에 대해 일 단위로 카운트
    for target_question in target_questions:
        day_cnt_list[target_question.time.day] += 1

    return day_cnt_list


# 사용자의 질문 조회(전달받은 시간 기준)
def find_target_questions(userid, year, month, day=None):
    target_time = str(year) + '-'
    target_time += str(month) if month >= 10 else '0' + str(month)
    if day is not None:
        target_time += '-' + str(day) if day >= 10 else '0' + str(day)

    user = User.objects.get(userid=userid)
    return Question.objects.filter(userid=user, time__startswith=target_time)
