import collections
import json
import os.path

import boto3
import numpy as np
from botocore.config import Config
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from matplotlib import pyplot as plt

from blog.models import Keywords
from blog.models import User as Question
from common.forms import FileUploadForm
from common.models import User, Profile
from config import my_settings
from mypage.S3UpDownLoader import S3UpDownLoader


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def index(request):
    if request.method == 'GET':
        # ----- JSON -----
        # data = json.loads(request.body)
        # userid = data['userid']
        # ----- HTML -----
        userid = request.GET.get('userid', None)

        # 해당 userid를 가지는 사용자가 존재한다면
        if User.objects.filter(userid=userid).exists():
            user = User.objects.get(userid=userid)

            # user의 질문 수 계산
            question_count = count_questions(user)
            # user의 키워드 빈도 수 계산
            keyword_cnt_info = check_freq_keyword(user)

            img = None

            # 마이페이지에 대한 정보(이미지)가 있다면 S3에서 이미지 다운로드
            if Profile.objects.filter(userid=userid).exists():

                # 출발지 (S3 이미지 경로) (DB에 저장된 경로에는 큰따옴표가 붙어 있어 이를 슬라이싱으로 제거하였음)
                src_path = json.dumps(str(Profile.objects.get(userid=userid).img))[1:-1]
                print(f'src_path: {src_path}')
                # 목적지 (프로젝트 내 이미지 저장 경로)
                dest_path = 'static/image/'
                print(f'dest_path: {dest_path}')
                # 파일 이름
                file_name = os.path.basename(src_path)
                print(f'file_name: {file_name}')

                try:
                    # S3에서 이미지 다운로드
                    S3UpDownLoader(
                        bucket_name=my_settings.AWS_STORAGE_BUCKET_NAME,
                        access_key=my_settings.AWS_ACCESS_KEY_ID,
                        secret_key=my_settings.AWS_SECRET_ACCESS_KEY,
                        verbose=False
                    ).download_file(src_path, dest_path)

                    # 로컬에 저장된 파일을 JSON으로 전달
                    img = json.dumps(plt.imread(dest_path + file_name), cls=NumpyEncoder)

                except Exception as e:
                    print(e)

            context = {
                'info': {
                    'email': user.email,
                    'questionCount': question_count,
                    'image': img
                },
                'keywords': keyword_cnt_info
            }

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

    result = []
    for cnt in collections.Counter(keyword_list).most_common(10):
        result.append(list(cnt))
    # print(f'result = {result}')
    return sorted(result, key=lambda x: x[1], reverse=True)  # 키워드 빈도수, 사전순 정렬


# 이미지 업로드
def image_upload(request):
    if request.method == 'POST':
        # ----- JSON -----
        data = json.loads(request.body)
        img = data['img']
        img_name = data['img_name']
        userid = data['userid']
        # ----- HTML -----
        # img = request.FILES['image']
        # img_name = request.POST['img_name']
        # userid = request.POST['userid']

        print(f'img_name: {img_name}')

        if User.objects.filter(userid=userid).exists():
            user = User.objects.get(userid=userid)

            # 이미 등록된 이미지가 있다면
            if Profile.objects.filter(userid=userid).exists():
                # DB에 존재하는 이미지 Get
                target = Profile.objects.get(userid=userid)

                # S3 Bucket에 존재하는 이미지 삭제
                # s3_client = boto3.client(
                #     's3',
                #     aws_access_key_id=my_settings.AWS_ACCESS_KEY_ID,
                #     aws_secret_access_key=my_settings.AWS_SECRET_ACCESS_KEY,
                # )
                # s3_client.delete_object(
                #     Bucket=my_settings.AWS_STORAGE_BUCKET_NAME,
                #     Key=target.img    # 이미지 객체가 아니라 문자열이라서 에러 발생..
                # )

                # DB에 존재하는 이미지 삭제
                target.delete()

            # 새로운 이미지 등록
            profile_upload = Profile(
                userid=user,
                img=img
            )
            profile_upload.save()

            # Amazon S3 Bucket에 이미지 저장
            try:
                s3 = boto3.resource(
                    's3',
                    aws_access_key_id=my_settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=my_settings.AWS_SECRET_ACCESS_KEY,
                    config=Config(signature_version='s3v4')
                )
                s3.Bucket(my_settings.AWS_STORAGE_BUCKET_NAME) \
                    .put_object(Key=img_name, Body=img, ContentType='image/jpg')
            except:
                print('S3 ERROR!!!')
                return JsonResponse({'message': "S3 ERROR!", 'status': 400}, status=400)

            # return redirect('/mypage/profile')
            return JsonResponse({'message': "Success", 'status': 200}, status=200)

        else:
            return JsonResponse({'message': "This User doesn't exist", 'status': 400}, status=400)
    else:
        profile_form = FileUploadForm
        context = {
            'profileUpload': profile_form,
        }
        # return render(request, 'mypage/profile.html', context)
        return JsonResponse({'message': "profile get...", 'status': 200}, status=200)
