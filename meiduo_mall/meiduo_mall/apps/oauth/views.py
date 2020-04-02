import re

from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
# Create your views here.
from django.views.generic.base import View

import logging
from QQLoginTool.QQtool import OAuthQQ
from django_redis import get_redis_connection

from meiduo_mall.apps.oauth.utils import generate_token, check_access_token
from users.models import User

from .models import OAuthQQUser
from meiduo_mall.utils.response_code import RETCODE

logger = logging.getLogger('django')


class QQAuthUserView(View):
    """
    QQ 用户扫码回调处理
    """

    def get(self, request):
        code = request.GET.get('code')
        # next = request.GET.get('next')
        if not code:
            http.HttpResponseForbidden('缺少code参数')

        # 创建 oauth QQ对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            # 向QQ服务器请求获取access——token
            access_token = oauth.get_access_token(code=code)

            # 使用access_token换取openid

            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('OAuth 2.0 认证失败')
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 没有绑定用户
            access_token = generate_token(openid)
            context = {'access_token_openid': access_token}
            return render(request, 'oauth_callback.html', context)
        else:
            # 已绑定用户
            qq_user = oauth_user.user
            login(request, qq_user)

            # 响应结果
            next = request.GET.get('state')
            response = redirect(next)
            response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 15)
            return response

    def post(self, request):
        """
        绑定openid 到用户
        :param request:
        :return:
        """
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token_openid = request.POST.get('access_token_openid')

        # 判断参数是否都存在
        if not all([mobile, password, sms_code_client]):
            return http.HttpResponseForbidden('缺少必穿参数')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号')
        # 判断密码是否合法
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 校验短信
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)

        if sms_code_server is None:
            render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效短信验证码'})

        if sms_code_client != sms_code_client:
            render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})

        # 取出openid
        openid = check_access_token(access_token_openid)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': 'openid 已失效'})

        # 使用是手机号查询 用户是否存在

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 不存在则 新建新用户
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            # 校验密码是否正确
            if not user.check_password(password):
                return render(request, 'oauth_callback.html', {'account_errmsg': '账号或密码错误'})

        # 绑定openid
        try:
            oauth_qq_user = OAuthQQUser.objects.create(user=user, openid=openid)
        except Exception as e:
            logger.error(e)
            return render(request, 'oauth_callback.html', {'account_errmsg': '账号或密码错误'})

        # 登陆用户
        login(request, oauth_qq_user.user)

        next = request.GET.get('state')
        response = redirect(next)
        response.set_cookie('username', oauth_qq_user.user.username, max_age=3600 * 24 * 15)
        return response


class QQAuthURLView(View):
    """
    提供QQ扫码登录页面
    """

    def get(self, request):
        # 接收参数 next
        next = request.GET.get('next')

        # 创建 oauth QQ登录对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)

        # 生成QQ登录的扫码链接
        login_url = oauth.get_qq_url()

        # 响应登录链接
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})
