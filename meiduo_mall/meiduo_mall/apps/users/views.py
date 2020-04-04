import json
import re, logging

from django import http
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import View

from celery_tasks.email.tasks import send_verify_email
from .utils import generate_verify_email_url, check_verify_email_token
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from .models import User

logger = logging.getLogger('django')


class AddressView(LoginRequiredMixin, View):
    """
    用户收获地址
    """

    def get(self, request):
        return render(request, 'user_center_site.html')


class VerifyEmailView(View):
    """
    验证邮箱
    验证邮箱的核心：就是将用户的email_active字段设置为True
    """

    def get(self, request):
        token = request.GET.get('token')
        # 验证token
        if not token:
            return http.HttpResponseBadRequest('缺少token')
        user = check_verify_email_token(token)
        if not user:
            http.HttpResponseForbidden('无效的token')

        # 修改email_active = true

        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活失败')

        else:

            return redirect(reverse('users:info'))


class EmailView(LoginRequiredJSONMixin, View):
    """
    添加邮箱验证
    """

    def put(self, request):

        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        # 校验参数
        if not email:
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email格式有误')

        # 保存邮箱
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})
        else:
            veriffy_url = generate_verify_email_url(request.user)
            # 发送邮件
            send_verify_email.delay(email, veriffy_url)

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class UserInfoView(LoginRequiredMixin, View):
    """
    用户中心
    """

    def get(self, request):
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        return render(request, 'user_center_info.html', context)


class LogoutView(View):
    """
    退出登录
    """

    def get(self, request):
        """
        实现退出登录逻辑
        :param request:
        :return:
        """
        logout(request)

        # 退出后重定向到首页
        response = redirect(reverse('contents:index'))

        response.delete_cookie('username')

        return response


class LoginView(View):
    """
    登录页面
    """

    def get(self, request):
        """提供登录页面"""
        return render(request, 'login.html')

    def post(self, request):
        """
        实现登录逻辑
        :param request:
        :return:
        """
        # 获取参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必要参数')

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')

        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.HttpResponseForbidden('密码最少为8位,最长为20位')

        # 用户登录

        user = authenticate(username=username, password=password)  # 重写该方法实现多用户登录

        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 状态保持

        login(request, user)

        if remembered != 'on':
            # 没有记住用户, 关闭浏览器会话即过期
            request.session.set_expiry(0)
        else:
            # None 表示两周后过期
            request.session.set_expiry(None)

        # 响应登录结果
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))
        # 写入cookie 有效期 15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response


class MobileCountView(View):
    """
    判断手机号是否存在重复
    """

    def get(self, request, mobile):
        """

        :param request:
        :param mobile: 手机号
        :return:
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})

    def post(self, request):
        pass


class UsernameCountView(View):
    """
    判断用户名是否重复注册
    """

    def get(self, request, username):
        """

        :param request:
         :param username:
        :return:
        """
        # 实现主体业务逻辑：使用username查询对应的记录的条数(filter返回的是满足条件的结果集)
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


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
            return http.HttpResponseForbidden("缺少必要参数")
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden("请输入5-20个字符的用户名")
        # 判断密码是否是8-20个数字
        if not re.match(r'^[a-zA-Z0-9]{8,20}', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password2 != password:
            return http.HttpResponseForbidden('两次输入密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        # 保存用户信息到数据库
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            # http.HttpResponseForbidden('注册失败')
            return render(request, 'register.html', {'register_errmsg': '注册失败'})
        # 登陆状态保持
        login(request, user)
        # 注册成功 重定向到首页
        # return http.HttpResponseForbidden('注册成功,重定向到首页')

        response = redirect(reverse('contents:index'))

        # 写入cookie 有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response
