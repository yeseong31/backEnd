from django.urls import path

from blog.views import index

app_name = 'kodeal'

urlpatterns = [
    # main page
    path('', index, name='index'),

]