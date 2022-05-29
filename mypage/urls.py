from django.conf.urls.static import static
from django.urls import path
from django.views.generic import RedirectView

from config import settings
from mypage.views import *

app_name = 'mypage'

urlpatterns = [
    # main page
    path('<userid>/', index, name='index'),
    path('', RedirectView.as_view(url='<userid>/', permanent=True)),
    path('home/', RedirectView.as_view(url='/', permanent=True)),

    # 이미지 등록
    path('profile/', image_upload, name="profileUpload"),

    # path('image/', Image.as_view(), name='image'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
