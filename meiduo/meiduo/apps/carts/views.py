from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.response import Response

from carts import constants
from carts import serializers
from goods.models import SKU
from utils import myjson


class CartAddView(APIView):
    """添加购物车视图"""

    def perform_authentication(self, request):
        # 先重写这个，告诉视图不要一进来就验证用户对象
        pass

    def post(self, request):
        # 获取数据
        # 序列化器先反序列化校验一波
        serializer = serializers.CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取校验过的数据
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']

        # 创建对象是反序列化，用validated_data， 序列化才用data
        response = Response(serializer.validated_data)

        try:
            # 如果用户认证信息不存在则抛异常
            user = request.user
        except:
            user = None

        # 判断用户是否登录
        if user is None:
            # 如果没有登录就存在cookie

            # 先读cookie原有的数据
            cart_str = request.COOKIES.get('cart')

            # 添加新的商品要在原有的cookie上面添加，如果原来没有就弄一个{}再添加
            if cart_str is None:
                cart_dict = {}
            else:
                cart_dict = myjson.loads(cart_str)
            # 修改cookie
            cart_dict[sku_id] = {
                "count": count,
                "selected": True
            }

            # 写cookie
            # 字典转成字符串
            cart_str = myjson.dumps(cart_dict)
            # 写cookie
            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)
        else:
            # 如果登录就存进redis
            # 连接redis
            redis_cli = get_redis_connection('cart')
            # 拼接一下key
            key = 'cart_%d'%user.id
            keyselect = 'cart_select_%d'%user.id
            # 存redis
            redis_cli.hset(key, sku_id, count)
            redis_cli.sadd(keyselect, sku_id)

        # 返回序列化后的数据
        return response

    def get(self, request):
        # 查询数据
        try:
            user = request.user
        except:
            user = None

        if user is None:
            # 先获取cookie
            cart_str = request.COOKIES.get('cart')
            # 把cookie转成字典
            cart_dict = myjson.loads(cart_str)
            # 遍历cookie的keys
            skus = []
            for key, value in cart_dict.items():
                sku = SKU.objects.get(pk=key)
                sku.count = value['count']
                sku.selected = value['selected']
                skus.append(sku)

            serializer = serializers.CartSerializer(skus, many=True)
            return Response(serializer.data)

        else:
            # 存redis
            # 连接redis
            redis_cli = get_redis_connection('cart')
            key = 'cart_%d'%user.id
            keyselect = 'cart_select_%d'%user.id

            # 从hash中读取所有商品编号
            sku_ids = redis_cli.hkeys(key)



            # 从set中取出所有sku_id
            sku_ids_selected = redis_cli.smembers(keyselect)
            # 强转redis里面取出来的byte类型为int类型，不然sku.id不会和这个列表里面的值相等，因为类型就不一致
            sku_ids_selected = [int(skuid_selected) for skuid_selected in sku_ids_selected]


            # 查出哈希表里面全部sku的id
            skus = SKU.objects.filter(id__in=sku_ids)

            # 查出所有sku然后新增两个属性，然后再用序列化器序列化输出
            for sku in skus:
                sku.count = redis_cli.hget(key, sku.id)
                sku.selected = sku.id in sku_ids_selected

            serializer = serializers.CartSerializer(skus, many=True)
            return Response(serializer.data)

    def put(self, request):
        try:
            user = request.user
        except:
            user = None

        serializer = serializers.CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id= serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']

        response = Response(serializer.data)

        # 判断user是否存在
        if user is None:
            # 用cookie
            cart_str = request.COOKIES.get('cart')
            cart_dict = myjson.loads(cart_str)

            cart_dict[sku_id] = {
                "count": count,
                "selected": selected
            }

            cart_str = myjson.dumps(cart_dict)

            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)

        else:
            # 用redis
            # 连接redis
            redis_cli = get_redis_connection('cart')
            key = 'cart_%d'%user.id
            keyselect = 'cart_select_%d'%user.id

            redis_cli.hset(key, sku_id, count)

            if selected:
                redis_cli.sadd(keyselect, sku_id)
            else:
                redis_cli.srem(keyselect, sku_id)

        return response

    def delete(self, request):
        try:
            user = request.user
        except:
            user = None

        serializer = serializers.CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.validated_data['sku_id']

        response = Response(status=204)

        if user is None:
            cart_str = request.COOKIES.get('cart')
            cart_dict = myjson.loads(cart_str)

            if sku_id in cart_dict:
                del cart_dict[sku_id]

            # 写cookie
            cart_str = myjson.dumps(cart_dict)

            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)

        else:
            # 写redis
            # 连接redis
            redis_cli = get_redis_connection('cart')

            key = 'cart_%d'%user.id
            keyselect = 'cart_select_%d'%user.id

            redis_cli.hdel(key, sku_id)
            redis_cli.srem(keyselect, sku_id)


        return response


class CartSelectView(APIView):
    """购物车全选视图"""

    def perform_authentication(self, request):
        pass

    def put(self, request):
        try:
            user = request.user
        except:
            user = None

        # 获取，　校验数据，　并构建一个响应对象
        serializer = serializers.CartSelectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selected = serializer.validated_data['selected']

        response = Response(serializer.validated_data)

        # 未登录的情况
        if user is None:
            cart_str = request.COOKIES.get('cart')
            cart_dict = myjson.loads(cart_str)

            for key in cart_dict.keys():
                cart_dict[key]['selected'] = selected

            cart_str = myjson.dumps(cart_dict)

            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)
        # 登录的情况
        else:
            # 连接redis
            redis_cli = get_redis_connection('cart')
            key = 'cart_%d'%user.id
            keyselect = 'cart_select_%d'%user.id

            sku_ids = redis_cli.hkeys(key)

            if selected:
                redis_cli.sadd(keyselect, *sku_ids)
            else:
                redis_cli.srem(keyselect, *sku_ids)

        return response