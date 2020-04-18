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

from carts.views import *

urlpatterns = [
    # 购物车模块
    url(r'^carts/$', CartsView.as_view(), name='carts'),
    # 全选购物车
    url(r'^carts/selection/$', CartsSelectAllView.as_view(), name='selection'),
    # 简单购物车数据
    url(r'^carts/simple/$', CartsSimpleView.as_view(), name='simple'),
]
