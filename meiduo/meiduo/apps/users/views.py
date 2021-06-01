from rest_framework import generics
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from users import constants
from users.serializers import UserModelSerializer, UserDetailSerializer, EmailSerializer, EmailActiveSerializer, \
    AddressSerializer, HistorySerializer
from utils import tjws
from .models import User, Address
from rest_framework.response import Response



class UsernameCountView(APIView):
    """统计用户名字数量"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()

        data = {
            "username": username,
            "count": count
        }
        return Response(data)


class MobileCountView(APIView):
    """统计电话号码数量"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        data = {
            "mobile": mobile,
            "count": count
        }
        return Response(data)


class UserCreateView(generics.CreateAPIView):
    """用户创建"""
    serializer_class = UserModelSerializer


class UserDetailView(generics.RetrieveAPIView):
    # 定义序列化器输出用户的信息内容
    serializer_class = UserDetailSerializer
    # 限制必须登录才能访问这个视图
    permission_classes = [IsAuthenticated]

    # 重写方法，根据登录的用户查询，不然默认根据PK主键查询用户
    def get_object(self):
        return self.request.user


class EmailView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user


class EmailActiveView(APIView):
    def get(self, requeset):
        data = requeset.query_params

        serializer = EmailActiveSerializer(data=data)

        if not serializer.is_valid():
            raise Response(serializer.errors)

        # 查询当前用户并保存
        user = User.objects.get(pk=serializer.validated_data.get('user_id'))
        user.email_active = True
        user.save()

        return Response({"message": "OK"})


class AddressViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.request.user.addresses.filter(is_delete=False)

    # 重写list
    def list(self, request, *args, **kwargs):
        data_dict = self.get_queryset()

        serializer = self.get_serializer(data_dict, many=True)

        return Response({
            "user_id": self.request.user.id,
            "default_address_id": self.request.user.default_address_id,
            "limit": constants.ADDRESS_LIMIT,
            "addresses": serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        address = self.get_object()

        address.is_delete = True

        return Response(status=204)

    # 修改标题===>****/pk/title/------put
    # 如果没有detail=False=====>*****/title/
    # ^ ^addresses/(?P<pk>[^/.]+)/title/$ [name='addresses-title']
    @action(methods=['put'], detail=True)
    def title(self, request, pk):
        # address = Address.objects.get(pk=pk)
        address = self.get_object()

        title = request.data['title']

        address.title = title

        address.save()

        return Response({"title": address.title})

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        user = request.user

        user.default_address_id = pk

        user.save()

        return Response({"message": "OK"})


class HistoryListView(generics.ListCreateAPIView):
    # 先创建浏览过商品的id列表
    permission_classes = [IsAuthenticated]

    serializer_class = HistorySerializer