def jwt_response_payload_handler(token, user=None, request=None):
    """
    重新 jwt_response_payload_handler 方法 实现自定义返回
    :param token:
    :param user:
    :param request:
    :return:
    """
    return {
        'token': token,
        'username': user.username,
        'id': user.id
    }
