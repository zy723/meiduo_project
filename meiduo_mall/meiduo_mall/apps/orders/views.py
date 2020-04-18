import logging
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
# Create your views here.
from django.views.generic.base import View
from django_redis import get_redis_connection

from goods.models import SKU
from orders import constants
from users.models import Address

logger = logging.getLogger('django')


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
