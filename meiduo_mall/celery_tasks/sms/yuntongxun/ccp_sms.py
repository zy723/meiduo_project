# -*- coding: UTF-8 -*-

from .CCPRestSDK import REST

# 主帐号
accountSid = '8aaf070862181ad5016236f3bcc811d5'

# 主帐号Token
accountToken = '4e831592bd464663b0de944df13f16ef'

# 应用Id
appId = '8aaf070868747811016883f12ef3062c'

# 请求地址，格式如下，不需要写http://
# serverIP = 'app.cloopen.com'  # 生产环境
serverIP = 'sandboxapp.cloopen.com'  # 测试环境

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id

# def sendTemplateSMS(to, datas, tempId):
#     # 初始化REST SDK
#     rest = REST(serverIP, serverPort, softVersion)
#     rest.setAccount(accountSid, accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     for k, v in result.iteritems():
#
#         if k == 'templateSMS':
#             for k, s in v.iteritems():
#                 print('%s:%s' % (k, s))
#
#         else:
#             print('%s:%s' % (k, v))

# sendTemplateSMS(手机号码,内容数据,模板Id)


class CCP(object):
    def __new__(cls, *args, **kwargs):
        """
        定义单例的初始化方法
        :param args:
        :param kwargs:
        :return:
        """
        # 判断单例是否存在, _instance属性存储的额就是单例
        if not hasattr(cls, '_instance'):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)

            # 初始化单例
            cls._instance.rest = REST(serverIP, serverPort, softVersion)
            cls._instance.rest.setAccount(accountSid, accountToken)
            cls._instance.rest.setAppId(appId)

        # 返回单例
        return cls._instance

    def send_template_sms(self, to, datas, tempId):
        """
        发送短信验证码单例方法
        :param to: 手机号
        :param datas: 内容数据
        :param tempId: 模板ID
        :return: 成功：0 失败：-1
        """
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        print(result)
        if result.get('statusCode') == '000000':
            return 0
        else:
            return -1


if __name__ == '__main__':
    CCP().send_template_sms('17600992168', ['123456', 5], 1)
