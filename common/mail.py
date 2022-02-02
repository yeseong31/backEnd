# 8자리의 랜덤한 인증번호 생성(알파벳 대문자,소문자,숫자 혼합)
import string, random


def email_auth_num():
    length = 8
    string_pool = string.ascii_letters + string.digits
    auth_num = ""
    for i in range(length):
        auth_num += random.choice(string_pool)
    return auth_num
