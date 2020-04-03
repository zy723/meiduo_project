from django.contrib.auth.backends import ModelBackend
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

import re

from django.conf import settings
from . import constants
from .models import User


def check_verify_email_token(token):
    """
    反序列化token, 获取user
    :param token: 待反序列化的token
    :return:
    """
    s = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = s.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


def generate_verify_email_url(user):
    """
    生成用户激活链接
    :param user: 当前user
    :return: http://www.meiduo.site:8000/emails/verification/?token= + token
    """
    s = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {'user_id': user.id, 'email': user.email}
    token = s.dumps(data).decode()

    return settings.EMAIL_VERIFY_URL + '?token=' + token


def get_user_by_account(account):
    """
    根据 account 查询账户
    :param account:  用户名或者手机号
    :return:
    """

    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            # 手机号
            user = User.objects.get(mobile=account)

        else:
            # 用户名
            user = User.objects.get(username=account)
    except User.DoseNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """
    重写认证方法, 实现多账号登录
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """

        :param request:
        :param username: 用户名
        :param password: 密码
        :param kwargs:
        :return:
        """
        user = get_user_by_account(username)

        # 校验用户是否存在并检验密码

        if user and user.check_password(password):
            return user
        else:
            return None
