import json
import logging
from decimal import Decimal

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render
# Create your views here.
from django.utils import timezone
from django.views.generic.base import View
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from orders import constants
from orders.models import OrderInfo, OrderGoods
from users.models import Address

logger = logging.getLogger('django')


class UserOrderInfoView(LoginRequiredMixin, View):
    """
    我的订单
    """

    def get(self, request, page_num):
        user = request.user
        # 查询订单信息
        orders = user.orderinfo_set.all().order_by('-create_time')
        # 遍历所有订单
        for order in orders:
            # 绑定订单状态
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1]
            # 绑定支付方式
            # order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1]
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1]
            order.sku_list = []
            # 查询订单商品
            order_goods = order.skus.all()
            # 遍历订单商品
            for order_good in order_goods:
                sku = order_good.sku
                sku.count = order_good.count
                sku.amount = sku.price * sku.count
                order.sku_list.append(sku)

        try:
            page_num = int(page_num)
            paginator = Paginator(orders, constants.ORDERS_LIST_LIMIT)
            page_orders = paginator.page(page_num)
            total_page = paginator.num_pages

        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '参数 page_num 有误或订单不存在'})

        context = {
            'page_orders': page_orders,
            'total_page': total_page,
            'page_num': page_num,
        }
        return render(request, 'user_center_order.html', context=context)


class OrderSuccessView(LoginRequiredMixin, View):
    """
    订单成功
    """

    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        return render(request, 'order_success.html', context)


class OrderCommitView(LoginRequiredMixin, View):
    """
    提交订单接口
    """

    def post(self, request):
        """保存订单基本信息和订单商品信息"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
            # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('参数address_id错误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')
        # 明显的开启一次事务
        with transaction.atomic():
            # 在数据库操作之前需要指定保存点（保存数据库最初的状态）
            save_id = transaction.savepoint()
            # 暴力回滚
            try:
                # 获取登录用户
                user = request.user
                # 获取订单编号：时间+user_id == '20190526165742000000001'
                order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
                # 保存订单基本信息（一）
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0.00),
                    freight=Decimal(10.00),
                    pay_method=pay_method,
                    # status = 'UNPAID' if pay_method=='ALIPAY' else 'UNSEND'
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )
                # 保存订单商品信息（多）
                # 查询redis购物车中被勾选的商品
                redis_conn = get_redis_connection('carts')
                # 所有的购物车数据，包含了勾选和未勾选 ：{b'1': b'1', b'2': b'2'}
                redis_cart = redis_conn.hgetall('carts_%s' % user.id)
                # 被勾选的商品的sku_id：[b'1']
                redis_selected = redis_conn.smembers('selected_%s' % user.id)
                # 构造购物车中被勾选的商品的数据 {b'1': b'1'}
                new_cart_dict = {}
                for sku_id in redis_selected:
                    new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])
                # 获取被勾选的商品的sku_id
                sku_ids = new_cart_dict.keys()
                for sku_id in sku_ids:
                    # 每个商品都有多次下单的机会，直到库存不足
                    while True:
                        # 读取购物车商品信息
                        sku = SKU.objects.get(id=sku_id)  # 查询商品和库存信息时，不能出现缓存，所以没用filter(id__in=sku_ids)
                        # 获取原始的库存和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales
                        # 获取要提交订单的商品的数量
                        sku_count = new_cart_dict[sku.id]
                        # 判断商品数量是否大于库存，如果大于，响应"库存不足"
                        if sku_count > origin_stock:
                            # 库存不足，回滚
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
                        # 模拟网络延迟
                        # import time
                        # time.sleep(7)
                        # SKU 减库存，加销量
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)
                        # 如果在更新数据时，原始数据变化了，返回0；表示有资源抢夺
                        if result == 0:
                            # 库存 10，要买1，但是在下单时，有资源抢夺，被买走1，剩下9个，如果库存依然满足，继续下单，直到库存不足为止
                            # return http.JsonResponse('下单失败')
                            continue
                        # SPU 加销量
                        sku.spu.sales += sku_count
                        sku.spu.save()
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )
                        # 累加订单商品的数量和总价到订单基本信息表
                        order.total_count += sku_count
                        order.total_amount += sku_count * sku.price
                        # 下单成功，记得break
                        break
                # 再加最后的运费
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})
            # 数据库操作成功，明显的提交一次事务
            transaction.savepoint_commit(save_id)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'order_id': order_id})


class OrderSettlementView(LoginRequiredMixin, View):
    def get(self, request):
        """
        获取订单信息
        :param request:
        :return:
        """
        user = request.user
        # 获取用户地址
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except Address.DoesNotExist:
            logger.error(Address.DoesNotExist.__str__())
            addresses = None

        # 获取sku信息
        redis_connection = get_redis_connection('carts')
        redis_cart = redis_connection.hgetall("carts_%s" % user.id)
        carts_selected = redis_connection.smembers('selected_%s' % user.id)
        cart = {}
        for sku_id in carts_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        total_count = 0
        total_amount = Decimal(0.00)

        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]
            sku.amount = sku.count * sku.price
            total_count += sku.count
            total_amount += sku.count * sku.price
        freight = Decimal(constants.FREIGHT)
        context = {
            'addresses': addresses,  # 地址
            'skus': skus,  # 商品信息
            'total_count': total_count,  # 总数量
            'total_amount': total_amount,  # 总价格
            'freight': freight,  # 邮费
            'payment_amount': total_amount + freight,
        }

        return render(request, 'place_order.html', context)
