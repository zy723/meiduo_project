import logging
from django import http
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View

from contents.utils import get_categories
from goods import constants
from goods.models import GoodsCategory, SKU
from goods.utils import get_breadcrumb
from meiduo_mall.utils.response_code import RETCODE

logger = logging.getLogger('django')


class DetailView(View):
    """
    商品详情页面
    """

    def get2(self, request, sku_id):

        # 接收sku_id 并且校验参数是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')
        # 查询商品的分类信息
        categories = get_categories()

        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格建
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)

        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()

        # 构建不同规格参数的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)

            # 向规格参数-sku字典中添加记录
            spec_sku_map[tuple(key)] = s.id

        # 获取当前商品的规格信息
        goods_spacs = sku.spu.specs.order_by('id')
        # 若当前sku信息不完整,则不再继续
        if len(sku_key) < len(goods_spacs):
            return render(request, '404.html')

        for index, spec in enumerate(goods_spacs):
            key = sku_key[:]
            spec_options = spec.options.all()
            for option in spec_options:
                key[index] = option.id
                option.sku_id = spec_options
            spec.spec_options = spec_options

        # 构造返回的上下文
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_spacs,
        }
        return render(request, 'detail.html', context)

    def get(self, request, sku_id):
        """提供商品详情页"""
        # 接收和校验参数
        try:
            # 查询sku
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            # return http.HttpResponseNotFound('sku_id 不存在')
            return render(request, '404.html')

        # 查询商品分类
        categories = get_categories()

        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 构造上下文
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs
        }

        return render(request, 'detail.html', context)


class HotGoodsView(View):
    """
    热销排行
    """

    def get(self, request, category_id):
        """
        响应json 数据
        {
            code	状态码
            errmsg	错误信息
            hot_skus[ ]	热销SKU列表
            id	SKU编号
            default_image_url	商品默认图片
            name	商品名称
            price	商品价格
        }
        :param request:
        :param category_id:
        :return:
        """
        try:
            suks = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]

        except Exception as e:
            logger.error(e)
            return http.HttpResponseNotFound('category_id 不存在')

        hot_skus = []
        for sku in suks:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price,
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})


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
