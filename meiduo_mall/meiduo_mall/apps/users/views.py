import re

from django import http
from django.db import DatabaseError
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View

from meiduo_mall.meiduo_mall.apps.users.models import User


class RegisterView(View):
    """
    注册页面
    """

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            http.HttpResponseForbidden("缺少必要参数")
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            http.HttpResponseForbidden("请输入5-20个字符的用户名")
        # 判断密码是否是8-20个数字
        if not re.match(r'^[a-zA-Z0-9]{8,20}', password):
            http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password2 != password:
            http.HttpResponseForbidden('两次输入密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            http.HttpResponseForbidden('请输入正确的手机号')
        # 判断是否勾选用户协议
        if allow != 'on':
            http.HttpResponseForbidden('请勾选用户协议')

        # 保存用户信息到数据库
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            # http.HttpResponseForbidden('注册失败')
            render(request, 'register.html', {'register_errmsg': '注册失败'})

        # 注册成功 重定向到首页
        http.HttpResponseForbidden('注册成功,重定向到首页')
