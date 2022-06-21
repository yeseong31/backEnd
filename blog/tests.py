from django.test import TestCase

# Create your tests here.
from django.utils import timezone

from blog.models import User as Question
from common.models import User

for i in range(5, 101):
    Question(
        question=f'테스트 질문...{i}',
        question_papago=f'Test Question...{i}',
        code=f'result code...{i}',
        star=5,
        language='Python 3' if i < 50 else 'Javascript',
        preprocess='...',
        userid=User(userid='kjh')
    ).save()
