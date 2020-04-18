import base64
import json
import logging
import pickle

from django import http
# Create your views here.
from django.shortcuts import render
from django.views.generic.base import View
from django_redis import get_redis_connection

from carts import constants
from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE

logger = logging.getLogger('django')


class CartsSimpleView(View):
    """
    简单购物车页面展示
    """

    def get(self, request):
        """
        请求参数
         空

        相应结果 Json
        code	状态码
        errmsg	错误信息
        cart_skus[ ]	简单购物车SKU列表
        id	购物车SKU编号
        name	购物车SKU名称
        count	购物车SKU数量
        default_image_url	购物车SKU图片
        :return: Json
        """

        user = request.user
        if user.is_authenticated:
            # 用户登陆
            redis_connection = get_redis_connection('carts')
            redis_cart = redis_connection.hgetall('carts_%s' % user.id)
            carts_selected = redis_connection.smembers('selected_%s' % user.id)
            # 统一 carts_dict 数据格式
            carts_dict = {}
            for sku_id, count in redis_cart.items():
                carts_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in carts_selected
                }
        else:
            # 用户未登录
            cookies_carts_str = request.COOKIES.get('carts')
            carts_dict = pickle.loads(base64.b64decode(cookies_carts_str.encode()))
            if not carts_dict:
                carts_dict = {}

        cart_skus = []
        sku_ids = carts_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': carts_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image.url,
            })
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'cart_skus': cart_skus})


class CartsSelectAllView(View):
    """
    全选购物车
    """

    def put(self, request):
        """
        参数名	类型	是否必传	说明
        selected	bool	是	是否全选

        返回参数
        字段	说明
        code	状态码
        errmsg	错误信息

        :param request:
        :return: Json
        """
        # 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)
        if selected:
            if not isinstance(selected, bool):
                return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'selected 有误'})

        user = request.user
        if user.is_authenticated:
            # 已经登录
            redis_connection = get_redis_connection('carts')
            cart = redis_connection.hgetall('carts_%s' % user.id)
            sku_id_list = cart.keys()
            pipeline = redis_connection.pipeline()

            if selected:
                pipeline.sadd('selected_%s' % user.id, *sku_id_list)
                ret_str = '全选购物车成功'
            else:
                pipeline.srem('selected_%s' % user.id, *sku_id_list)
                ret_str = '全选购物车已经取消'
            pipeline.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': ret_str})
        else:
            # 未登录
            # 用户已登录，操作cookie购物车
            cart = request.COOKIES.get('carts')
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                for sku_id in cart:
                    cart[sku_id]['selected'] = selected
                cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                response.set_cookie('carts', cookie_cart, max_age=constants.CARTS_COOKIE_EXPIRES)

            return response


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

        user = request.user
        # 获取购物车中的数据
        if user.is_authenticated:
            # 用户登录从redis中读取数据
            redis_connection = get_redis_connection('carts')
            redis_carts = redis_connection.hgetall('carts_%s' % user.id)
            carts_selected = redis_connection.smembers('selected_%s' % user.id)
            carts_dict = {}
            for sku_id, count in redis_carts.items():
                carts_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in carts_selected
                }
        else:
            # 从cookie中获取购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                carts_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                carts_dict = {}

        # 构造渲染数据
        sku_ids = carts_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        carts_skus = []

        for sku in skus:
            carts_skus.append(
                {
                    'id': sku.id,
                    'name': sku.name,
                    'count': carts_dict.get(sku.id).get('count'),
                    'selected': str(carts_dict.get(sku.id).get('selected')),
                    'default_image_url': sku.default_image.url,
                    'price': str(sku.price),
                    'amount': str(sku.price * carts_dict.get(sku.id).get('count'))
                }

            )
        context = {
            'cart_skus': carts_skus,
        }
        return render(request, 'cart.html', context)

    def post(self, request):
        """
        添加购物车 登录用户保存数据到redis、未登录保存在cookie
        :param request:
        :return:
        """
        # 接收参数

        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 校验参数是否齐全
        if not all([sku_id, count, selected]):
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '传入参数不能为空'})

        # 判断sku_id 是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            logger.error(SKU.DoesNotExist.__str__())
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'sku_id 不存在'})

        # 判断 count 是否为数字
        try:
            count = int(count)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'count有误'})
        # 判断selected是否为bool

        if selected:
            if not isinstance(selected, bool):
                return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'selected 有误'})

        user = request.user
        if user.is_authenticated:
            # 已登录操作 数据存储到redis
            redis_conn = get_redis_connection('carts')
            pipeline = redis_conn.pipeline()
            # 新增购物车数据
            pipeline.hincrby('carts_%s' % user.id, sku_id, count)
            # 新增选中状态
            if selected:
                pipeline.sadd('selected_%s' % user.id, sku_id)

            pipeline.execute()
            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})

        else:
            # 未登录操作
            carts_str = request.COOKIES.get('carts')
            # 如果数据存在 做解密操作
            if carts_str:
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
            else:
                carts_dict = {}
            # 判断商品是否已经存在 存在做累计操作 反之直接赋值
            if sku_id in carts_dict:
                # 商品做累计
                origin_count = carts_dict[sku_id]['count']
                count += origin_count

            carts_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }
            # 将数据再次打包加密
            carts_str_enc = base64.b64encode(pickle.dumps(carts_dict)).decode()

            # 响应结果
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            response.set_cookie('carts', carts_str_enc, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response

    def put(self, request):
        """
        修改购物数据

        传入参数
        参数名	类型	是否必传	说明
        sku_id	int	是	商品SKU编号
        count	int	是	商品数量
        selected	bool	否	是否勾选

        响应 json

        字段	说明
        sku_id	商品SKU编号
        count	商品数量
        selected	是否勾选

        :param request:
        :return:
        """

        # 接收参数
        json_dcit = json.loads(request.body.decode())
        sku_id = json_dcit.get('sku_id')
        count = json_dcit.get('count')
        selected = json_dcit.get('selected')
        # 校验参数
        if not all([sku_id, count, selected]):
            return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '传入参数不能为空'})

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            logger.error(SKU.DoesNotExist.__str__())
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '参数sku_id 不存在'})
        try:
            count = int(count)
        except:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '参数count 有误'})

        if selected:
            if not isinstance(selected, bool):
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'selected 有误'})

        # 保存数据

        if request.user.is_authenticated:
            # 用户登录 从redis中获取数据
            redis_connection = get_redis_connection('carts')
            pipeline = redis_connection.pipeline()
            pipeline.hset('carts_%s' % request.user.id, sku_id, count)
            # 判断是否被选中
            if selected:
                pipeline.sadd('selected_%s' % request.user.id, sku_id)
            else:
                pipeline.srem('selected_%s' % request.user.id, sku_id)
            # 构造数据
            # 构造响应数据
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count
            }
            # 响应json数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})

        else:
            # 用户未登录
            carts_str = request.COOKIES.get('carts')
            # 解析数据
            if carts_str:
                carts_dict = pickle.loads(base64.b64decode(carts_str))
            else:
                carts_dict = {}
            # 修改数据
            carts_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 加密数据
            carts_str = base64.b64encode(pickle.dumps(carts_dict)).decode()

            # 构造响应数据
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count
            }
            # 响应json数据
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            response.set_cookie('carts', carts_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response

    def delete(self, request):
        """
        删除商品信息
        :param request:
        :return:
        """
        # 接收参数
        json_dcit = json.loads(request.body.decode())
        sku_id = json_dcit.get('sku_id')

        # 校验参数
        if not all([sku_id]):
            return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '传入参数不能为空'})

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            logger.error(SKU.DoesNotExist.__str__())
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '参数sku_id 不存在'})
        # 保存数据
        user = request.user
        if user.is_authenticated:
            redis_connection = get_redis_connection('carts')
            pipeline = redis_connection.pipeline()
            pipeline.hdel('carts_%s' % user.id, sku_id)
            pipeline.srem('selected_%s' % user.id, sku_id)
            pipeline.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
        else:
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                carts_dict = pickle.loads(base64.b64decode(carts_str))
            else:
                carts_dict = {}
            if sku_id in carts_dict:
                del carts_dict[sku_id]
                carts_str = base64.b64encode(pickle.dumps(carts_dict)).decode()

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
            response.set_cookie('carts', carts_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response
