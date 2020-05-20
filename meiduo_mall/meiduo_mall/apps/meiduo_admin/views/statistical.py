from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import date, timedelta

from goods.models import GoodsVisitCount
from meiduo_admin.serialziers.GoodsSerializer import GoodsSerializer
from users.models import User


class UserCountView(APIView):
    """
    用户总量统计
    接口分析
    请求方式： GET /meiduo_admin/statistical/total_count/

    请求参数： 通过请求头传递jwt token数据。

    返回数据： JSON

    {
            "count": "总用户量",
            "date": "日期"
    }
    返回值	类型	是否必须	说明
    count	int	是	总用户量
    date	date	是	日期
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当天日期
        new_date = date.today()
        # 获取所有用户
        count = User.objects.all().count()
        return Response(
            {
                'count': count,
                'date': new_date
            }
        )


class UserDayCountView(APIView):
    """
    日增用户统计
    接口分析
    请求方式： GET /meiduo_admin/statistical/day_increment/

    请求参数： 通过请求头传递jwt token数据。

    返回数据： JSON

    {
            "count": "新增用户量",
            "date": "日期"
    }
    返回值	类型	是否必须	说明
    count	int	是	新增用户量
    date	date	是	日期
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # 获取当日注册用户数量 date_joined 记录创建账号时间
        count = User.objects.filter(date_joined__gte=now_date).count()
        return Response({'count': count, "date": now_date})


class UserActiveCountView(APIView):
    """
    日活跃用户统计
    接口分析
    请求方式：GET /meiduo_admin/statistical/day_active/

    请求参数： 通过请求头传递jwt token数据。

    返回数据： JSON

    {
            "count": "活跃用户量",
            "date": "日期"
    }
    返回值	类型	是否必须	说明
    count	int	是	活跃用户量
    date	date	是	日期
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        count = User.objects.filter(last_login__gte=now_date).count()
        return Response({
            "count": count,
            "date": now_date
        })


class UserOrderCountView(APIView):
    """
    日下单用户量统计
    接口分析
    请求方式：GET /meiduo_admin/statistical/day_orders/

    请求参数： 通过请求头传递jwt token数据。

    返回数据： JSON

    {
            "count": "下单用户量",
            "date": "日期"
    }
    返回值	类型	是否必须	说明
    count	int	是	下单用户量
    date	date	是	日期
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        # count = User.objects.filter(orders__create_time__gte=now_date).count()
        count = len(set(User.objects.filter(orders__create_time__gte=now_date)))
        return Response({
            "count": count,
            "date": now_date
        })


class UserMonthCountView(APIView):
    """
    日分类商品访问量月增用户统计
    接口分析
    请求方式：GET /meiduo_admin/statistical/month_increment/

    请求参数： 通过请求头传递jwt token数据。

    返回数据： JSON

     [
            {
                "count": "用户量",
                "date": "日期"
            },
            {
                "count": "用户量",
                "date": "日期"
            },
            ...
        ]
    返回值	类型	是否必须	说明
    count	int	是	新增用户量
    date	date	是	日期
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # 获取一个月开始时间
        start_date = now_date - timedelta(29)
        # 暂存每天保存的用户量
        date_list = []
        for i in range(30):
            # 循环便利日期
            index_date = start_date + timedelta(days=i)
            # 指定下一天日期
            cur_date = start_date + timedelta(days=i + 1)
            # 查询条件大于当前日期index_date 小于cur_date
            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=cur_date).count()
            date_list.append({
                'count': count,
                'date': index_date
            })
        return Response(date_list)


class GoodsDayView(APIView):
    """
    日分类商品访问量
    接口分析
    请求方式： GET /meiduo_admin/statistical/goods_day_views/

    请求参数： 通过请求头传递jwt token数据。

    返回数据： JSON

     [
            {
                "category": "分类名称",
                "count": "访问量"
            },
            {
                "category": "分类名称",
                "count": "访问量"
            },
            ...
        ]
    返回值	类型	是否必须	说明
    category	int	是	分类名称
    count	int	是	访问量
    """

    def get(self, request):
        # 获取当天日期
        now_date = date.today()
        # 获取当天访问的商品分类数量信息
        data = GoodsVisitCount.objects.filter(date=now_date)
        # 序列化返回分类数量
        ser = GoodsSerializer(data, many=True)

        return Response(ser.data)
