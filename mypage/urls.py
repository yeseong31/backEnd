from django.urls import path
from django.views.generic import RedirectView

from mypage.views import *

app_name = 'mypage'

urlpatterns = [
    # main page
    path('', index, name='index'),
    path('home/', RedirectView.as_view(url='/', permanent=True)),

]