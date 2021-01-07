"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app.views import *

urlpatterns = [
	path('admin/', admin.site.urls),
	path('test/',testt,name='test'),
	path('testshow/<table_name>/',testshow,name='testshow'),
	path('test_with_type/<typee>/', test_with_type,name='test_with_type'),
	path('result_page/<result_id>/', get_result_page,name='result_page'),
	path('test_list/', test_list,name='test_list'),
	path('', get_home_page,name='home'),
	path('search/', search, name='search')
]
