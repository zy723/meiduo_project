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
    # 获取订单信息详情
    url(r'^orders/settlement/$', OrderSettlementView.as_view(), name='settlement'),
    # 订单提交接口
    url(r'^orders/commit/$', OrderCommitView.as_view(), name='commit'),
    # 展示下单成功
    url(r'^orders/success/$', OrderSuccessView.as_view(), name='success'),
    # 展示订单信息
    url(r'^orders/info/(?P<page_num>\d+)/$', UserOrderInfoView.as_view(), name='info'),

]
