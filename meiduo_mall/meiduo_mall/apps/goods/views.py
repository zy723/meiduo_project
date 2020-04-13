import logging
from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View

from contents.utils import get_categories
from goods import constants
from goods.models import GoodsCategory, SKU
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
        # 接收sort参数, 用户不传, 就是默认排序
        sort = request.GET.get('sort', 'default')

        # 查询商品分类频道
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(category)

        # 按照排序规格查询分类的SKU信息
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = 'create_time'

        # 分页和排序查询：category查询sku,一查多,一方的模型对象.多方关联字段.all/filter
        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)

        # 创建分页器： 每页page_num条记录
        paginator = Paginator(skus, constants.GOODS_LIST_LIMIT)
        try:
            page_skus = paginator.page(page_num)
        except EmptyPage:
            return http.HttpResponseNotFound('empty page')

        # 获取总页数
        total_page = paginator.num_pages

        # 渲染页面
        context = {
            'categories': categories,  # 频道分类
            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        return render(request, 'list.html', context)
