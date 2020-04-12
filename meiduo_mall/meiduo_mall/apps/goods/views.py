import logging
from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View

from contents.utils import get_categories
from goods.models import GoodsCategory
from goods.utils import get_breadcrumb

logger = logging.getLogger('django')


class ListView(View):

    def get(self, request, category_id, page_num):
        """
        商品列表页面
        :param request:
        :return:
        """
        # 判断category_id是否正确
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseNotFound('category_id 不存在')
        # 查询商品分类频道
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(category)
        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
        }
        return render(request, 'list.html', context)
