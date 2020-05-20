from rest_framework import serializers
from goods.models import GoodsVisitCount


class GoodsVisitSerializer(serializers.ModelSerializer):
    """分类商品浏览序列化器类"""
    # 关联对象嵌套序列化：将关联对象序列化为关联对象模型类__str__方法的返回值
    category = serializers.StringRelatedField(label='分类')

    class Meta:
        model = GoodsVisitCount
        fields = ('category', 'count')
