from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

from . import constants


def generate_token(openid):
    """
    签名openid
    :param openid:
    :return:
    """
    serializer = Serializer(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)
    data = {'openid': openid}
    token = serializer.dumps(data)
    return token.decode()


def check_access_token(access_token):
    """
    反解、反序列化access_token_openid
    :param access_token:
    :return:
    """
    try:
        serializer = Serializer(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)
        data = serializer.loads(access_token)
    except BadData:
        return None
    else:
        return data['openid']
