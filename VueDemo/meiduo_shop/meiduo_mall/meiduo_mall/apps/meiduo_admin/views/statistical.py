from datetime import timedelta

from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import GoodsVisitCount
from meiduo_admin.serializers.statistical import GoodsVisitSerializer
from users.models import User


class UserTotalCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取网站总用户人数
        1. 获取网站总用户数量
        2. 返回应答
        """
        # 1.获取网站总用户数量
        now_date = timezone.now()
        count = User.objects.count()

        # 2.返回应答
        response_data = {
            # date: 只返回`年-月-日`
            'date': now_date.date(),
            'count': count
        }
        return Response(response_data)


class UserDayIncrementView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取日增用户数量
        1. 获取日增用户数量
        2. 返回应答
        """
        # 1.获取日增用户数量
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = User.objects.filter(date_joined__gte=now_date).count()

        # 2.返回应答
        response_data = {
            'date': now_date.date(),
            'count': count
        }
        return Response(response_data)


class UserDayActiveView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取日活用户量:
        1. 获取日活用户量
        2. 返回应答
        """

        # 1.获取日活用户量
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = User.objects.filter(last_login__gte=now_date).count()

        # 2. 返回应答
        response_data = {
            'date': now_date.date(),
            'count': count
        }

        return Response(response_data)


class UserMonthCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取当月每日新增用户数据:
        1. 获取当月每日新增用户数据
        2. 返回应答
        """
        # 1. 获取当月每日新增用户数据
        # 当前日期
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # 起始日期
        begin_date = now_date - timedelta(days=29)

        # 统计数据列表
        count_list = []

        for i in range(30):
            # 当天时间和下一天时间
            cur_date = begin_date + timedelta(days=i)
            next_date = cur_date + timedelta(days=1)

            # 统计当天新增用户数量
            count = User.objects.filter(date_joined__gte=cur_date, date_joined__lt=next_date).count()
            count_list.append({
                'date': cur_date.date(),
                'count': count
            })

        # 2. 返回应答
        return Response(count_list)


class GoodsDayView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取当日分类商品的访问量
        1. 查询获取当日分类商品访问量
        2. 将查询数据序列化并返回
        """
        # 1.查询获取当日分类商品访问量
        # 当前日期
        now_date = timezone.now().date()

        goods_visit = GoodsVisitCount.objects.filter(date=now_date)

        # 2.将查询数据序列化并返回
        serializer = GoodsVisitSerializer(goods_visit, many=True)

        return Response(serializer.data)

