# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.shortcuts import render

from django.db import connection

from django.http import Http404

def get_home_page(request):
	return render(request, 'home_page.html')

def search(request):
	keyStr = request.GET.get('mykey')
	context={}
	sql_str = "select * from 番剧表 where 番剧名 like '%{}%'".format(keyStr)
	with connection.cursor() as cursor:
		cursor.execute(sql_str)
		dataInfo = cursor.fetchall()
	context['search_result_list']=dataInfo
	return render(request,"search_result.html",context)


def get_result_page(request,result_id):
	# 获取番剧表的各个属性
	sql_str = "select column_name from information_schema.COLUMNS where table_name='番剧表'"
	with connection.cursor() as cursor:
		cursor.execute(sql_str)
		attr = cursor.fetchall()
	# 获取当前番剧的各个属性值
	sql_str = "select * from 番剧表 where 番剧名={}".format(result_id)
	with connection.cursor() as cursor:
		cursor.execute(sql_str)
		data = cursor.fetchall()
	context={}
	context['attr']=attr
	context['data']=data
	return render(request,'result_page.html',context)


def test_list(request):
	sql_str = "select * from 番剧表"
	with connection.cursor() as cursor:
		cursor.execute(sql_str)
		dataInfo1 = cursor.fetchall()
	sql_str = "select * from 番剧表"
	with connection.cursor() as cursor:
		cursor.execute(sql_str)
		dataInfo2 = cursor.fetchall()
	context={}
	context['articles_list']=dataInfo1
	context['articles_type']=dataInfo2
	return render(request,"testList.html",context)

def test_with_type(request,typee):
	sql_str = "select * from 番剧表 where 番剧名 like '%{}%'".format(str(typee))
	with connection.cursor() as cursor:
		cursor.execute(sql_str)
		dataInfo = cursor.fetchall()
	context={}
	context['articles_Type']=dataInfo
	return render(request,"test_with_type.html",context)

def testt(request):
	#sql_str = "select CID,CNAME from CUSTOMERS"
	sql_str = "show tables"
	with connection.cursor() as cursor:
		cursor.execute(sql_str)
		dataInfo = cursor.fetchall()
	return render(request,'testt.html',{'list':dataInfo})

def testshow(request,table_name):
	#sql_str = "select CID,CNAME from CUSTOMERS"
	#sql_str = "show tables"
	sql_str = "select column_name from information_schema.COLUMNS where table_name='"+str(table_name)+"'"
	with connection.cursor() as cursor:
		cursor.execute(sql_str)
		attr = cursor.fetchall()
	sql_str = "select * from "+str(table_name)
	with connection.cursor() as cursor:
		cursor.execute(sql_str)
		data = cursor.fetchall()
	context={}
	context['attr']=attr
	context['data']=data
	context['name']=data
	return render(request,'testshow.html',context)
