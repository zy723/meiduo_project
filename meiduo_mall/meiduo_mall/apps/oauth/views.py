from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
# Create your views here.
from django.views.generic.base import View

import logging
from QQLoginTool.QQtool import OAuthQQ
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
            pass
        else:
            # 已绑定用户
            qq_user = oauth_user.user
            login(request, qq_user)

            # 响应结果
            next = request.GET.get('state')
            response = redirect(next)
            response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 15)
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
