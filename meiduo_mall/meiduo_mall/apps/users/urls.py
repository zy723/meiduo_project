"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from .views import *

urlpatterns = [
    # 用户注册
    url(r'^register/$', RegisterView.as_view(), name='register'),
    # 判断用户名是否重复
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', UsernameCountView.as_view()),
    # 判断手机号是否重复
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', MobileCountView.as_view()),
    # 登录
    url(r'^login/$', LoginView.as_view(), name='login'),
    # 退出登录
    url(r'^logout/$', LogoutView.as_view(), name='logout'),

    # ---------------------------------------------------------------------
    # 用户中心
    url(r'^info/$', UserInfoView.as_view(), name='info'),
    # 添加邮箱
    url(r'^emails/$', EmailView.as_view(), name='emails'),
    # 验证邮箱
    url(r'^emails/verification/$', VerifyEmailView.as_view(), name='emails_verification'),
    # 展示用户收货地址
    url(r'^addresses/$', AddressView.as_view(), name='address'),
    # 创建收货地址
    url(r'^addresses/create/$', CreateAddressView.as_view(), name='addresses_create'),
    # 修改收货地址
    url(r'^addresses/(?P<address_id>\d+)/$', UpdateDestroyAddressView.as_view(), name='addresses_change'),
    # 设置默认地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', DefaultAddressView.as_view(), name='addresses_default'),
    # 修改默认标题
    url(r'^addresses/(?P<address_id>\d+)/title/$', UpdateTitleAddressView.as_view(), name='addresses_title'),
    # 修改密码
    url(r'^change_pwd/$', ChangePasswordView.as_view(), name='change_pwd'),

]
