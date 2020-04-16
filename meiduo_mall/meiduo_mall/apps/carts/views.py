from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View


class CartsView(View):
    """
    购物车管理
    """

    def get(self, request):
        """
        展示购物车
        :param request:
        :return:
        """
        pass

    def post(self, request):
        """
        添加购物车
        :param request:
        :return:
        """
        pass
