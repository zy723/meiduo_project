from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import User


class AdminAuthSerializer(ModelSerializer):
    """管理员序列化器类"""
    username = serializers.CharField(label='用户名')
    token = serializers.CharField(label='JWT Token', read_only=True)

    class Meta:
        model =User
        fields = ('id', 'username', 'password', 'token')

        extra_kwargs = {
            'password':{
                'write_only':True
            }
        }

    def validate(self, attrs):
        # 获取username和password
        username = attrs['username']
        password = attrs['password']

        # 进行用户名和密码校验
        try:
            user = User.objects.get(username=username, is_staff=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("用户名或是密码错误")

        else:
            # 校验密码
            if not user.check_password(password):
                raise serializers.ValidationError('用户名或是密码错误')

            # 给attrs中添加user属性,保存登录用户
            # TODO:了解attrs的使用
            attrs['user'] = user
        return attrs

    def create(self, validated_data):
        # 获取登录用户user
        user = validated_data['user']

        # 设置最新的登录时间
        user.last_login = timezone.now()
        user.save()

        # 服务器生成jwt token, 保存当前用户的身份信息
        from rest_framework_jwt.settings import api_settings

        # 组织payload数据的方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # 生成jwt token数据的方法
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 组织payload数据
        payload = jwt_payload_handler(user)
        # 生成jwt token
        token = jwt_encode_handler(payload)

        # 给用户增加属性,保存token
        user.token = token

        return user
