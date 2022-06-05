from django.conf.urls.static import static
from django.urls import path
from django.views.generic import RedirectView

from config import settings
from mypage.views import *

app_name = 'mypage'

urlpatterns = [
    # main page
    path('<str:userid>/', index, name='index'),
    path('home/', RedirectView.as_view(url='/', permanent=True)),

    # 잔디 기능
    path('<str:userid>/<int:year>/', questions_per_year, name="questions_per_year"),
    path('<str:userid>/<int:year>/<int:month>/', questions_per_month, name="questions_per_month"),
    path('<str:userid>/<int:year>/<int:month>/<int:day>/', questions_per_day, name="questions_per_day"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
