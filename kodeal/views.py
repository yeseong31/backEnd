import ssl
import urllib
import urllib.request


from blog.views import extract_question_sentences
from config.my_settings import CLIENT_ID, CLIENT_SECRET

# Create your views here.

# 파파고 api 함수 - 3.20
def papago(text):
    client_id = CLIENT_ID  # 개발자센터에서 발급받은 Client ID 값 (my_settings.py 참고)
    client_secret = CLIENT_SECRET  # 개발자센터에서 발급받은 Client Secret 값 (my_settings.py 참고)
    encText = urllib.parse.quote(text)
    data = "source=ko&target=en&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    context = ssl._create_unverified_context()
    response = urllib.request.urlopen(request, data=data.encode("utf-8"), context=context)
    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read()
        # Papago API의 반환값 중에서 "translatedText"에 해당하는 값만 추출해야 함
        return extract_question_sentences(response_body.decode('utf-8'))
    else:
        print("Error Code:" + rescode)
        return 'ERROR'