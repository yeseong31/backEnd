from rest_framework import routers
from .views import EntryViewSet
from django.urls import path
from . import views
app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:id>', views.IndexView.as_view())
]
router = routers.DefaultRouter()
router.register(r'entries', EntryViewSet)
