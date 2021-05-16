from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView

from users.serializers import UserModelSerializer
from .models import User
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


class UserCreateView(CreateAPIView):
    """用户创建"""
    serializer_class = UserModelSerializer