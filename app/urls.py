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
	path('tables/',show_tables,name='show_tables'),
	path('edit/<table_name>/',edit_table,name='edit_table'),
	path('update/', update_table, name='update'),
	path('result_page/<result_id>/<table_name>', get_result_page,name='new_result_page'),
	path('addpic/', add_pic, name='addpic'),
	path('', get_home_page,name='home'),
	path('search/', search, name='search')
]
