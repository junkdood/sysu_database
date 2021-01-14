# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection, transaction
from urllib import parse
import time


def get_home_page(request):
    return render(request, 'home_page.html')


def search(request):
    """
    :param request:
    request.GET['search_key_value'] 由用户输入 在查询中需要参数化处理 防止sql注入
    :return:
    """
    search_key = {'番剧表': '番剧名', '声优表': '声优名', '制作公司表': '公司名', '曲目表': '曲名'}
    keyStr = request.GET.get('search_key_value')
    table_name = request.GET.get('table_name')
    context = {}
    if table_name == None:
        table_name = '番剧表'
    sql_str = "select * from {} where {} like concat('%%',%s,'%%')".format(table_name, search_key[table_name])
    with connection.cursor() as cursor:
        cursor.execute(sql_str, [keyStr])
        dataInfo = cursor.fetchall()
    dataInfo = [(parse.quote_plus(dataInfo[i][0]), dataInfo[i][0], table_name) for i in range(len(dataInfo))]
    context['search_result_list'] = dataInfo
    context['search_key'] = keyStr
    return render(request, "new_search_result.html", context)


def get_result_page(request, result_id, table_name):
    """
    :param request:
    :param result_id: 查询的主属性值 由用户输入 在查询中需要参数化处理 防止sql注入
    :param table_name: 查询的表
    :return:
    context['main_info']:
    context['other_info']:
    context['related_info']:
    context['picpath']: 图片路径，为空字符串的时候前端用默认图片
    context['current_name']: 番剧名
    """
    search_key = {'番剧表': '番剧名', '声优表': '声优名', '制作公司表': '公司名', '曲目表': '曲名'}
    multi_res_relation = {'番剧表': (('参演表', '番名', '参演声优'), ('曲目放送表', '番名', '放送曲目'),
                                  ('续作关系表', '续作番名', '前作'), ('续作关系表', '前作番名', '续作')),
                          '声优表': (('参演表', '声优名', '参演番剧'),),
                          '制作公司表': (('制作表', '公司名', '制作番剧'),),
                          '曲目表': (('曲目放送表', '曲名', '所属番剧'),)}
    single_res_relation = {'番剧表': (('制作表', '番名', '制作信息'),), '声优表': (), '制作公司表': (), '曲目表': ()}
    isHyper = {'前作番名':1, '续作番名':1, '番名':1,'番剧名':1,'声优名':1,'公司名':1,'曲名':1}
    itsTableName = {'番剧名':'番剧表','番名':'番剧表','声优名':'声优表','公司名':'制作公司表','曲名':'曲目表'}
    context = {'current_name':parse.unquote_plus(result_id), 'main_info':[], 'other_info':[], 'related_info':[], 'picpath':''}
    context['tablename'] = table_name
    context['picpath'] = []
    context['relatedurl'] = []
    result_id = parse.unquote_plus(result_id)
    with connection.cursor() as cursor:
        # 如果是番剧则获取图片
        if table_name == '番剧表':
            sql_str = "select 图片路径 from 番剧图片表 where 番名 = %s"
            cursor.execute(sql_str, [result_id])
            pic_path = cursor.fetchall()
            context['picpath'] = [pic_path[i][0] for i in range(len(pic_path))]
            sql_str = "select 链接,链接名称 from 相关链接表 where 番名 = %s"
            cursor.execute(sql_str, [result_id])
            pic_path = cursor.fetchall()
            context['relatedurl'] = [(pic_path[i][0], pic_path[i][1]) for i in range(len(pic_path))]
        # 获取当前表的各个属性
        sql_str = "select column_name from information_schema.COLUMNS where table_name='{}'".format(table_name)
        cursor.execute(sql_str)
        attr = cursor.fetchall()
        attr = [attr[i][0] for i in range(len(attr))]
        # 获取当前元组各个属性值
        sql_str = "select * from {} where {} =%s".format(table_name, search_key[table_name])
        cursor.execute(sql_str, [result_id])
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
            sql_str = "select {} from {} where {} = %s".format(new_attr_str, relate_table, relate_key)
            cursor.execute(sql_str, [result_id])
            new_data = cursor.fetchall()
            new_data = [[(new_data[tuple_i][i],parse.quote_plus(new_data[tuple_i][i]),
                          itsTableName.get(new_attr[i],'番剧表'),isHyper.get(new_attr[i],0)) for i in range(len(new_attr))]
                        for tuple_i in range(len(new_data))]
            if i < sinle_relate_num:
                if new_data:
                    new_data = new_data[0]
                context['other_info'].append((relate_name, zip(new_attr, new_data)))
            else:
                context['related_info'].append((relate_name, new_attr, new_data))
    return render(request, 'new_result_page.html', context)


def edit_table(request, table_name):
    context = {}
    sql_str = "show tables"
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        dataInfo = cursor.fetchall()[:12]
    context['table_list'] = [dataInfo[i][0] for i in range(len(dataInfo))]
    sql_str = "select column_name from information_schema.COLUMNS where table_name='" + str(table_name) + "'"
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        attr = cursor.fetchall()
    sql_str = "select * from " + str(table_name)
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        data = cursor.fetchall()
    context['attr'] = attr
    if data:
        data = [[str(data[i][j]) if data[i][j] != None else 'None' for j in range(len(data[0]))] for i in range(len(data))]
    context['data'] = data
    context['table_name'] = table_name
    return render(request, 'edit_table.html', context)


def update_table(request):
    """
    :param request:
    request.GET['attr']由用户输入 需要在查询中需要参数化处理 防止sql注入 这里的’attr‘是指当前表的属性
    :return:
    """
    if request.method == 'POST':
        option = request.POST['option']
        selected = request.POST['selected'] if 'selected' in request.POST else None
        table_name = request.POST['table_name']
        sql_str = "select column_name from information_schema.COLUMNS where table_name='{}'".format(table_name)
        with connection.cursor() as cursor:
            cursor.execute(sql_str)
            attr = cursor.fetchall()
        values = tuple(request.POST['{}'.format(attr[i][0])] for i in range(len(attr)))
        not_null_attr = [attr[i][0] for i in range(len(attr)) if values[i] != '']
        not_null_values = [val for val in values if val != '']
        if option == '插入':
            # 方法1：使用insert ignore插入数据 主键重复则不插入
            # 方法2：使用insert 失败则捕获异常
            values_str = ""
            for val in values:
                values_str += "%s," if val != '' else "NULL,"
            values_str = values_str[:-1]
            sql_str = "insert into {} values ({})".format(table_name, values_str)
            with connection.cursor() as cursor:
                try:
                    cursor.execute(sql_str, not_null_values)
                except:
                    return HttpResponse("输入数据无效或重复 插入失败！")
        elif option == '删除' or option == '替换':
            if selected == None:
                return HttpResponse("请选中一条数据！")
            selected = tuple([i.strip("'") for i in selected.strip("()[]").split("', '")])
            sql_str = "select column_name from INFORMATION_SCHEMA.`KEY_COLUMN_USAGE` where table_name='{}' and constraint_name='PRIMARY'".format(table_name)
            with connection.cursor() as cursor:
                cursor.execute(sql_str)
                pri_attr = cursor.fetchall()
                pri_attr = [pri_attr[i][0] for i in range(len(pri_attr))]
            attr_value = ()
            for att, val in zip(attr, selected):
                if att[0] in pri_attr:
                    attr_value += (att[0], val)
            cond = " {} = '{}' and " * (len(attr_value) // 2 - 1) + "{} = '{}'"
            cond = cond.format(*attr_value)
            if option == '删除':
                sql_str = "delete from {} where {}".format(table_name, cond)
                with connection.cursor() as cursor:
                    try:
                        cursor.execute(sql_str)
                    except:
                        return HttpResponse("删除失败！")
            else:
                upd = "{} = %s, " * (len(not_null_attr) - 1) + "{} = %s "
                upd = upd.format(*not_null_attr)
                sql_str = "update {} set {} where {}".format(table_name, upd, cond)
                with connection.cursor() as cursor:
                    try:
                        cursor.execute(sql_str, not_null_values)
                    except:
                        return HttpResponse("输入数据无效 更新失败！")
        return HttpResponse("")


def add_pic(request):
    if request.method == 'POST':
        img = request.FILES.get('pic')
        exist_img_num = request.POST['p_num'] + str(time.time())
        current = request.POST['c_name']
        imgpath = 'app/static/image/' + parse.quote_plus(current).replace('%','_') + str(exist_img_num) + "." + img.name.split('.')[-1]
        with open(imgpath, 'wb+') as f:
            f.write(img.read())
        sql_str = "insert into 番剧图片表 values('{}','{}')".format(current, imgpath[11:])
        with connection.cursor() as cursor:
            try:
                cursor.execute(sql_str)
            except:
                return HttpResponse("添加失败！")
    return HttpResponse("添加成功！")
