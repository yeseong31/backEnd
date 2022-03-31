from django.db import models

from common.models import User as Login_user

DELETED_USER = "deleted_user"


class User(models.Model):
    userid = models.ForeignKey(Login_user, related_name="%(class)s_userid", on_delete=models.SET_DEFAULT,
                               default=DELETED_USER, db_column='userid', verbose_name='사용자 아이디')
    question = models.CharField(max_length=4000, verbose_name='질문')
    question_papago = models.CharField(max_length=4000, verbose_name='질문(papago)',
                                       null=True, blank=True)
    code = models.CharField(max_length=4000, verbose_name='답변')
    time = models.DateTimeField(verbose_name='작성일', help_text="time", auto_now_add=True)
    star = models.FloatField(verbose_name='별점', null=True, blank=True)
    language = models.CharField(max_length=100, verbose_name='사용언어', null=True, blank=True, default='Python 3')


class Entry(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLIC = "public"
    STATUS_SET = (
        (STATUS_DRAFT, "초안"),
        (STATUS_PUBLIC, "공공의"),
    )
    title = models.CharField(max_length=128)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=STATUS_SET, default=STATUS_DRAFT, max_length=8)
    author = models.ForeignKey(User, related_name='entries', on_delete=models.CASCADE)
