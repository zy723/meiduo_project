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
