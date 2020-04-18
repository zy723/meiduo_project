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
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 搜索引擎的建立
    url(r'^search/', include('haystack.urls')),
    # user 模块
    url(r'^', include('users.urls', namespace='users')),
    # contents 首页模块
    url(r'^', include('contents.urls', namespace='contents')),
    # verifications 模块
    url(r'^', include('verifications.urls', namespace='verifications')),
    # oauth 认证模块
    url(r'^', include('oauth.urls', namespace='oauth')),
    # area 省市区模块
    url(r'^', include('areas.urls', namespace='areas')),
    # goods 商品展示详情模块
    url(r'^', include('goods.urls', namespace='goods')),
    # carts 购物车模块
    url(r'^', include('carts.urls', namespace='carts')),
    # orders 订单中心
    url(r'^', include('orders.urls', namespace='orders')),
]
