"""
增加支持管理员用户登录账号
JWT扩展的登录视图，在收到用户名与密码时，也是调用Django的认证系统中提供的authenticate()来检查用户名与密码是否正确。

我们可以通过修改Django认证系统的认证后端（主要是authenticate方法）来支持登录账号既可以是用户名也可以是手机号。

修改Django认证系统的认证后端需要继承django.contrib.auth.backends.ModelBackend，并重写authenticate方法。

authenticate(self, request, username=None, password=None, **kwargs)方法的参数说明：

request 本次认证的请求对象
username 本次认证提供的用户账号
password 本次认证提供的密码
我们想要让管理员用户才能登录我们的admin后台,这时我们就要修改django原有的用户验证方法。

重写authenticate方法的思路：

根据username参数查找用户User对象，在查询条件中在加上is_staff=True的条件
若查找到User对象，调用User对象的check_password方法检查密码是否正确

"""
from django.contrib.auth.backends import ModelBackend

from users.models import User


class MeiduoModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断是否通过vue组件发送请求
        if request is None:
            try:
                user = User.objects.get(username=username, is_staff=True)
            except:
                return None
            # 检查密码
            if user.check_password(password):
                return user
        else:
            # 变量username的值，可以是用户名，也可以是手机号，需要判断，再查询
            try:
                user = User.objects.get(username=username)
            except:
                # 如果未查到数据，则返回None，用于后续判断
                return None
        # 判断密码
        if user.check_password(password):
            return user
        else:
            return None
