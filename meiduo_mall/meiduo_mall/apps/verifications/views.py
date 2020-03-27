from django import http
from django.shortcuts import render

from django.views.generic.base import View
from django_redis import get_redis_connection

from meiduo_mall.utils import constants
from .libs.captcha.captcha import captcha


class ImageCodeView(View):
    """
    响应图片验证码
    """

    def get(self, request, uuid):
        # 生成验证码
        text, image = captcha.generate_captcha()

        # 保存图片验证码
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应图片验证码
        return http.HttpResponse(image, content_type='image/jpg')

    def post(self, request):
        pass
