import re

from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework import serializers

from oauth import constants
from oauth.models import QQUser
from users.models import User
from utils import tjws


class QQUserAuthSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    sms_code = serializers.CharField()
    password = serializers.CharField()
    access_token = serializers.CharField()

    def validate(self, attrs):
        # 验证手机号码
        mobile = attrs.get('mobile')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            raise serializers.ValidationError("手机号码格式不正确")

        # 验证短信验证码
        redis_cli = get_redis_connection('sms_code')
        sms_code_redis = redis_cli.get('sms_code_' + mobile)
        sms_code_request = attrs.get('sms_code')
        if not sms_code_redis:
            raise serializers.ValidationError("短信验证码已过期")
        redis_cli.delete('sms_code_' + mobile)
        if int(sms_code_redis) != int(sms_code_request):
            raise serializers.ValidationError("短信验证码不正确")

        # 验证access_token
        access_token = attrs.get('access_token')
        data_dict = tjws.loads(access_token, constants.QQ_AUTH_TOKEN_EXPIRES)

        # 这个access_token是会过期的，这里需要判断一下
        if data_dict is None:
            raise serializers.ValidationError("access_token已经过期了")

        openid = data_dict.get('openid')

        # 校验完之后存到attrs里面返回，下面注册的时候需要用到来和一个用户绑定在一起
        attrs["openid"] = openid

        return attrs

    def create(self, validated_data):
        # validated_data是一个字典
        openid = validated_data.get('openid')
        mobile = validated_data.get('mobile')
        password = validated_data.get('password')

        try:
            user = User.objects.get(mobile=mobile)
        except:
            # 这里是手机号码没有对应用户的情况, 创建一个新的用户对象并保存进数据库
            user = User()
            user.username = mobile
            user.mobile = mobile
            user.set_password(password)
            user.save()
        else:
            # 这里是手机号码对了一个用户的情况， 校验一下那个密码和对应的手机号码的用户密码有没有一致
            if not user.check_password(password):
                raise serializers.ValidationError("当前手机号码已经被注册")

        qquser = QQUser()
        qquser.user = user
        qquser.openid =openid
        qquser.save()

        # 校验完后返回一个QQ授权的用户
        return qquser





