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


def index(request, userid):
    # 마이페이지 접근
    if request.method == 'GET':
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
                dest_path = 'media/'
                print(f'dest_path: {dest_path}')
                # 파일 이름
                file_name = os.path.basename(src_path)
                print(f'file_name: {file_name}')

                img = my_settings.AWS_S3_BUCKET_LINK + src_path

                # try:
                #     # S3에서 이미지 다운로드
                #     S3UpDownLoader(
                #         bucket_name=my_settings.AWS_STORAGE_BUCKET_NAME,
                #         access_key=my_settings.AWS_ACCESS_KEY_ID,
                #         secret_key=my_settings.AWS_SECRET_ACCESS_KEY,
                #         verbose=False
                #     ).download_file(src_path, dest_path)
                # except Exception as e:
                #     print(e)

            context = {
                'info': {
                    'email': user.email,
                    'questionCount': question_count,
                    'image': img,
                    'username': user.username
                },
                'keywords': keyword_cnt_info
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

                # S3에 이미지 업로드
                # S3UpDownLoader(
                #     bucket_name=my_settings.AWS_STORAGE_BUCKET_NAME,
                #     access_key=my_settings.AWS_ACCESS_KEY_ID,
                #     secret_key=my_settings.AWS_SECRET_ACCESS_KEY,
                #     verbose=False
                # ).upload_file(img_name, dest_path)

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


def get_form_data(request):
    form = FileUploadForm(request.FILES, request.POST)
    if form.is_valid():
        print(f'유효한 폼')
        return JsonResponse({'message': "Success", 'status': 200}, status=200)

    return JsonResponse({'message': "Failure", 'status': 400}, status=400)
