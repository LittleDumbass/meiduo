from django_redis import get_redis_connection
from utils import myjson


def merge_cookie_to_redis(request,user_id,response):
    """
    合并cookie购物车信息到redis             以cookie里面的数据为准
    :param request: 请求对象，用来获取cookie
    :param user_id: 用来连接redis
    :param response: 用来返回删除cookie的操作
    :return:
    """
    # 获取cookie的数据
    cart_str = request.COOKIES.get('cart_%d'%user_id)

    # 字符串转成字典
    cart_dict = myjson.loads(cart_str)

    # 连接redis
    cart_key = 'cart_%d'%user_id
    cart_selected_key = 'cart_select_%d'%user_id

    redis_cli = get_redis_connection('cart')

    # 获取管道
    redis_pl = redis_cli.pipeline()

    # 遍历cookie的数据然后添加到redis中    只修改redis中和cookie一致的商品，如果redis有其他商品而cookie没有，则不会有影响
    for sku_id, sku_dict in cart_dict.items():
        # 先存id和数量，以cookie为准，就是如果已经存在这个商品，它的数量会是现在这个，如果不存在就创建新的sku_id:count进去
        redis_pl.hset(cart_key, sku_id, sku_dict['count'])
        # 看这个cookie的是否选中，选中就把redis改为选中，否则就不选中，
        if sku_dict['selected']:
            redis_pl.sadd(cart_selected_key, sku_id)
        else:
            redis_pl.srem(cart_selected_key, sku_id)

    # 执行管道命令
    redis_pl.execute()
    # 删除cookie并返回包含这个操作的响应对象
    response.set_cookie('cart', '', max_age=0)

    # 返回这个response
    return response