from django.db import models

from common.models import User as Login_user

DELETED_USER = "deleted_user"


class User(models.Model):
    qid = models.AutoField(primary_key=True)
    userid = models.ForeignKey(Login_user, related_name="%(class)s_userid", on_delete=models.SET_DEFAULT,
                               default=DELETED_USER, db_column='userid', verbose_name='사용자 아이디')
    question = models.CharField(max_length=4000, verbose_name='질문')
    question_papago = models.CharField(max_length=4000, verbose_name='질문(papago)',
                                       null=True, blank=True, default=question)
    code = models.CharField(max_length=4000, verbose_name='답변')
    time = models.DateTimeField(verbose_name='작성일', help_text="time", auto_now_add=True)
    star = models.FloatField(verbose_name='별점', null=True, blank=True, default=5.0)
    language = models.CharField(max_length=100, verbose_name='사용 언어', null=True, blank=True, default='Python 3')
    preprocess = models.CharField(max_length=2000, verbose_name='전저리 전 Codex 반환값', null=True, blank=True,
                                  default='TEST')

    def __str__(self):
        return self.qid

    class Meta:
        db_table = 'question'


# 키워드
class Keywords(models.Model):
    kid = models.AutoField(primary_key=True)
    qid = models.ForeignKey(User, related_name="%(class)s_qid", on_delete=models.SET_DEFAULT,
                            default=DELETED_USER, db_column='qid', verbose_name='질문 아이디')
    keyword = models.CharField(max_length=255, verbose_name='키워드')
    userid = models.ForeignKey(Login_user, related_name="%(class)s_userid", on_delete=models.SET_DEFAULT,
                               default=DELETED_USER, db_column='userid', verbose_name='사용자 아이디')

    def __str__(self):
        return self.qid

    class Meta:
        db_table = 'keyword'
