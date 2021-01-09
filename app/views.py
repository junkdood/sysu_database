# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.db import connection
from urllib import parse


def get_home_page(request):
    return render(request, 'home_page.html')


def search(request):
    search_key = {'番剧表': '番剧名', '声优表': '声优名', '制作公司表': '公司名', '曲目表': '曲名'}
    keyStr = request.GET.get('search_key_value')
    table_name = request.GET.get('table_name')
    context = {}
    sql_str = "select * from {} where {} like '%{}%'".format(table_name, search_key[table_name], keyStr)
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        dataInfo = cursor.fetchall()
    dataInfo = [(parse.quote_plus(dataInfo[i][0]), dataInfo[i][0], table_name) for i in range(len(dataInfo))]
    context['search_result_list'] = dataInfo
    return render(request, "search_result.html", context)


def get_result_page(request, result_id, table_name):
    """
    :param request:
    :param result_id: 查询的主属性值
    :param table_name: 查询的表
    :return:
    context['main_info']: 主要内容的关键词列表[m1,m2,...] 通过contex[m1]可获得相应内容 是一个 (attr,data)的列表 其中data不是列表
    context['other_info']: 次要内容（制作信息） ... 同上
    context['related_info']: 相关内容 ... data是列表 即不同元组的data attr和data分开放
    """
    search_key = {'番剧表': '番剧名', '声优表': '声优名', '制作公司表': '公司名', '曲目表': '曲名'}
    multi_res_relation = {'番剧表': (('参演表', '番名', '参演声优'), ('曲目放送表', '番名', '放送曲目'),
                                  ('续作关系表', '本作番名', '前作'), ('续作关系表', '前作番名', '续作')),
                          '声优表': (('参演表', '声优名', '参演番剧'),),
                          '制作公司表': (('制作表', '公司名', '制作番剧'),),
                          '曲目表': (('曲目放送表', '曲名', '所属番剧'),)}
    single_res_relation = {'番剧表': (('制作表', '番名', '制作信息'),), '声优表': (), '制作公司表': (), '曲目表': ()}
    result_id = parse.unquote_plus(result_id)
    context = {'main_info':[], 'other_info':[], 'related_info':[]}
    with connection.cursor() as cursor:
        # 获取当前表的各个属性
        sql_str = "select column_name from information_schema.COLUMNS where table_name='{}'".format(table_name)
        cursor.execute(sql_str)
        attr = cursor.fetchall()
        attr = [attr[i][0] for i in range(len(attr))]
        # 获取当前元组各个属性值
        sql_str = "select * from {} where {} ='{}'".format(table_name, search_key[table_name], result_id)
        cursor.execute(sql_str)
        data = cursor.fetchall()
        data = [data[0][i] for i in range(len(attr))]
        context['main_info'].append(('主要信息', zip(attr, data)))
        # 将一对一联系\一对一联系内容 添加到属性和属性值
        sinle_relate_num = len(single_res_relation[table_name])
        for i, (relate_table, relate_key, relate_name) in enumerate(single_res_relation[table_name] + multi_res_relation[table_name]):
            sql_str = "select column_name from information_schema.COLUMNS where table_name='{}' and column_name != '{}'".format(
                relate_table, relate_key)
            cursor.execute(sql_str)
            new_attr = cursor.fetchall()
            new_attr = [new_attr[i][0] for i in range(len(new_attr))]
            new_attr_str = ("{}," * (len(new_attr) - 1) + "{}").format(*new_attr)
            sql_str = "select {} from {} where {} = '{}'".format(new_attr_str, relate_table, relate_key, result_id)
            cursor.execute(sql_str)
            new_data = cursor.fetchall()
            new_data = [[new_data[tuple_i][i] for i in range(len(new_attr))] for tuple_i in range(len(new_data))]
            if i < sinle_relate_num:
                new_data = new_data[0]
                context['other_info'].append((relate_name, zip(new_attr, new_data)))
            else:
                context['related_info'].append((relate_name, new_attr, new_data))
    return render(request, 'new_result_page.html', context)


def insert_to_table(request, table_name):
    sql_str = "select column_name from information_schema.COLUMNS where table_name='{}'".format(table_name)
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        attr = cursor.fetchall()
        values = tuple(request.GET.get(attr[i][0]) for i in range(len(attr)))
        sql_str = "insert into {} values {}".format(table_name, values)
        cursor.execute(sql_str)


def show_tables(request):
    sql_str = "show tables"
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        dataInfo = cursor.fetchall()
    return render(request, 'show_tables.html', {'list': dataInfo})


def edit_table(request, table_name):
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
    return render(request, 'edit_table.html', context)
