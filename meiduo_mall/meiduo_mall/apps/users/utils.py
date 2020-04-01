from django.contrib.auth.backends import ModelBackend

import re
from .models import User


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
