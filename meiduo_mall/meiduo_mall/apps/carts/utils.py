import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    """
    登录后合并cookie购物车数据到Redis
    :param request:
    :param user:
    :param rqsponse:
    :return:
    """
    cookie_cart_str = request.COOKIES.get('carts')

    if not cookie_cart_str:
        return response

    cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart_str.encode()))
    new_cart_dict = {}
    new_cart_selected_add = []
    new_cart_selected_remove = []
    # 同步购物车中的数据
    for sku_id, cookie_dict in cookie_cart_dict.items():
        new_cart_dict[sku_id] = cookie_dict['count']
        if cookie_dict['selected']:
            new_cart_selected_add.append(sku_id)
        else:
            new_cart_selected_remove.append(sku_id)

    # 将数据写入到Redis中

    redis_connection = get_redis_connection('carts')
    pipeline = redis_connection.pipeline()
    pipeline.hmset('carts_%s' % user.id, new_cart_dict)
    # 同步勾选状态到Redis中
    if new_cart_selected_add:
        pipeline.sadd('selected_%s' % user.id, *new_cart_selected_add)
    if new_cart_selected_remove:
        pipeline.srem('selected_%s' % user.id, *new_cart_selected_remove)
    pipeline.execute()

    # 清除cookie
    response.delete_cookie('carts')
    return response
