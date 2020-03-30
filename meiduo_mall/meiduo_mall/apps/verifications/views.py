import logging
import random

from django import http

from django.views.generic.base import View
from django_redis import get_redis_connection

from celery_tasks.sms.tasks import ccp_send_sms_code
from .libs.yuntongxun.ccp_sms import CCP
from meiduo_mall.utils import constants
from meiduo_mall.utils.response_code import RETCODE
from .libs.captcha.captcha import captcha

# 创建日志输出器
logger = logging.getLogger('django')


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


class SMSCodeView(View):
    """
    手机验证码发送
    """

    def get(self, request, mobile):
        """

        :param request:
        :param mobile: 手机号
        :return:
        """
        # 接收获取参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 校验参数
        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})

        # 连接到redis 获取验证码对象
        redis_conn = get_redis_connection('verify_code')
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            # 图形验证码不存在或者过期
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})
        # 删除已经验证过的验证码, 避免重复使用
        try:
            redis_conn.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)
        # 对比图片验证码
        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码有误'})
        # 生成6位数字短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        # 保存验证码到redis中
        # 创建redis对象
        p1 = redis_conn.pipeline()
        p1.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        p1.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        p1.execute()

        # 发送验证码
        # send_sms_code.delay(mobile, sms_code)
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
        #                         constants.SEND_SMS_TEMPLATE_ID)

        # 异步发送验证码

        ccp_send_sms_code.delay(mobile, sms_code)

        print(sms_code)
        # 相应发送结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})

    def post(self, request):
        pass
