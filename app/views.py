# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.db import connection
from urllib import parse

#searchType = 0

def get_home_page(request):
    #global searchType
    #searchType = request.GET.get('shengyou')
    #logText = open('logType.txt','w')
    #logText.write("type "+str(searchType))
    #logText.close()
    return render(request, 'home_page.html')


def search(request):
    keyStr = request.GET.get('mykey')
    if keyStr == '*':
        keyStr = '%'
    context = {}
    sql_str = "select * from 番剧表 where 番剧名 like '%{}%'".format(keyStr)
    searchType = request.GET.get('searchType')
    #logText = open('logType2.txt','w')
    #logText.write("type "+str(searchType))
    #logText.close()
    print("searchType is {}".format(searchType))
    if searchType == 'shengyou':
        sql_str = "select * from 声优表 where 声优名 like '%{}%'".format(keyStr)
    if searchType == 'gequ':
        sql_str = "select * from 曲目表 where 曲名 like '%{}%'".format(keyStr)
    if searchType == 'gongsi':
        sql_str = "select * from 制作公司表 where 公司名 like '%{}%'".format(keyStr)
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        dataInfo = cursor.fetchall()
    #dataInfo = [(parse.quote_plus(dataInfo[i][0]), dataInfo[i][0]) for i in range(len(dataInfo))]
    dataInfo = [(parse.quote_plus(dataInfo[i][0]), dataInfo[i][0],searchType) for i in range(len(dataInfo))]
    context['search_result_list'] = dataInfo
    print(context)
    return render(request, "search_result.html", context)


#def get_result_page(request, result_id):
def get_result_page(request, result_id, searchType):
    result_id = parse.unquote_plus(result_id)
    context = {}
    with connection.cursor() as cursor:
        # 获取番剧表的各个属性
        sql_str = "select column_name from information_schema.COLUMNS where table_name='番剧表'"
        if searchType == "shengyou" :
            sql_str = "select column_name from information_schema.COLUMNS where table_name='声优表'"
        if searchType == "gequ" :
            sql_str = "select column_name from information_schema.COLUMNS where table_name='曲目表'"
        if searchType == "gongsi" :
            sql_str = "select column_name from information_schema.COLUMNS where table_name='制作公司表'"
        cursor.execute(sql_str)
        attr = cursor.fetchall()
        print(attr)
        # 获取当前番剧的各个属性值
        sql_str = "select * from 番剧表 where 番剧名='{}'".format(result_id)
        if searchType == "shengyou" :
            sql_str = "select * from 声优表 where 声优名='{}'".format(result_id)
        if searchType == "gequ" :
            sql_str = "select * from 曲目表 where 曲名='{}'".format(result_id)
        if searchType == "gongsi" :
            sql_str = "select * from 制作公司表 where 公司名='{}'".format(result_id)
        cursor.execute(sql_str)
        data = cursor.fetchall()
        print(data)
        if searchType == "fanju" or searchType == "shengyou":
        #sql_str = "select 声优名, 角色名 from 参演表 where 番名 = '{}'".format(result_id)
           sql_str = "select * from 参演表 where 番名 = '{}'or 声优名 = '{}'".format(result_id,result_id) 
        cursor.execute(sql_str)
        context['声优和角色'] = cursor.fetchall()
        sql_str = "select 曲名,类型,出现集数范围 from 曲目放送表 where 番名 = '{}'".format(result_id)
        cursor.execute(sql_str)
        context['曲名和类型和范围'] = cursor.fetchall()
        sql_str = "select 公司名,监督,原创类型,原创作者 from 制作表 where 番名 = '{}'".format(result_id)
        cursor.execute(sql_str)
        context['公司和监督和类型和作者'] = cursor.fetchall()
        sql_str = "select 前作番名 from 续作关系表 where 本作番名 = '{}'".format(result_id)
        cursor.execute(sql_str)
        context['前作和'] = cursor.fetchall()

    context['column_value_pairs'] = [(attr[i][0], data[0][i]) for i in range(len(attr))]
    print(context)
    return render(request, 'result_page.html', context)


def test_list(request):
    sql_str = "select * from 番剧表"
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        dataInfo1 = cursor.fetchall()
    sql_str = "select * from 番剧表"
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        dataInfo2 = cursor.fetchall()
    context = {}
    context['articles_list'] = dataInfo1
    context['articles_type'] = dataInfo2
    return render(request, "testList.html", context)


def test_with_type(request, typee):
    sql_str = "select * from 番剧表 where 番剧名 like '%{}%'".format(str(typee))
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        dataInfo = cursor.fetchall()
    context = {}
    context['articles_Type'] = dataInfo
    return render(request, "test_with_type.html", context)


def testt(request):
    # sql_str = "select CID,CNAME from CUSTOMERS"
    sql_str = "show tables"
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        dataInfo = cursor.fetchall()
    return render(request, 'testt.html', {'list': dataInfo})


def testshow(request, table_name):
    # sql_str = "select CID,CNAME from CUSTOMERS"
    # sql_str = "show tables"
    sql_str = "select column_name from information_schema.COLUMNS where table_name='" + str(table_name) + "'"
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        attr = cursor.fetchall()
    sql_str = "select * from " + str(table_name)
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        data = cursor.fetchall()
    context = {}
    context['attr'] = attr
    context['data'] = data
    context['name'] = data
    return render(request, 'testshow.html', context)
