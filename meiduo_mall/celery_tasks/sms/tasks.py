import time

from celery_tasks.main import celery_app
from celery_tasks.sms.yuntongxun import constants
from celery_tasks.sms.yuntongxun.ccp_sms import CCP

import logging

# 创建日志输出器
logger = logging.getLogger('ccp_send_sms_code')


@celery_app.task(bind=True, name='ccp_send_sms_code', retry_backoff=3)
# @celery_app.task(name='ccp_send_sms_code')
def ccp_send_sms_code(self, mobile, sms_code):
    """

    :return:
    """
    try:
        # send_ret = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
        #                                    constants.SEND_SMS_TEMPLATE_ID)
        # 模拟发送短信
        time.sleep(2)
        print("发送完毕", mobile, sms_code)
        send_ret = 0
    except Exception as e:
        logger.error(e)
        # 存在异常重试3次
        send_ret = -1
        raise self.retry(exc=e, max_retries=3)

    return send_ret
