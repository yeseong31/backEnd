"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() kodeal: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from blog.urls import router as blog_router
from django.conf.urls import url, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('kodeal.urls')),                          # kodeal page
    path('', RedirectView.as_view(url='/home/', permanent=True)),
    path('common/', include('common.urls')),                        # common(login)
    path('google/', include('allauth.urls')),                       # common(google login)
    url(r'^api/', include(blog_router.urls)),
]
