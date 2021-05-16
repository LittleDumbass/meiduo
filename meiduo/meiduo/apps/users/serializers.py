from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from users.models import User


class UserModelSerializer(serializers.Serializer):
    """用户序列化器"""
    id = serializers.IntegerField(read_only=True)
    token = serializers.CharField(read_only=True)
    username = serializers.CharField(
        min_length=5,
        max_length=20,
        error_messages={
            'min_length': '用户名包含5-20个字符',
            'max_length': '用户名包含5-20个字符',
        }
    )
    mobile = serializers.CharField()
    password = serializers.CharField(
        min_length=8,
        max_length=20,
        error_messages={
            'min_length': '密码包含5-20个字符',
            'max_length': '密码包含5-20个字符',
        },
        write_only=True
    )
    password2 = serializers.CharField(
        min_length=8,
        max_length=20,
        error_messages={
            'min_length': '密码包含5-20个字符',
            'max_length': '密码包含5-20个字符',
        },
        write_only=True
    )
    sms_code = serializers.IntegerField(write_only=True)
    allow = serializers.BooleanField(write_only=True)

    # 验证用户名
    def validate_username(self, value):
        count = User.objects.filter(username=value).count()
        if count > 0:
            raise serializers.ValidationError("用户名已经注册")
        return value

    # 验证手机号码
    def validate_mobile(self, value):
        count = User.objects.filter(mobile=value).count()
        if count > 0:
            raise serializers.ValidationError("手机号码已经注册")
        return value

    # 验证勾选协议是否
    def validate_allow(self,value):
        if value is None:
            raise serializers.ValidationError("请先阅读协议并同意")
        return value

    # 验证密码和短信验证码
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("两次输入密码不一致")

        redis_cli = get_redis_connection('sms_code')
        mobile = attrs.get('mobile')
        key = 'sms_code_' + mobile
        sms_code_redis = redis_cli.get(key)
        sms_code_request = attrs.get('sms_code')
        if int(sms_code_redis) != int(sms_code_request):
            raise serializers.ValidationError("验证码输入错误")

        return attrs

    # create创建和保存新建的用户
    def create(self, validated_data):
        user = User()
        user.username = validated_data.get('username')
        user.mobile = validated_data.get('mobile')
        user.set_password(validated_data.get('password'))
        user.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token

        return user

