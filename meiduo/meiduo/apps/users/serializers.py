from django.core.mail import send_mail
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from celery_tasks.email.tasks import send_verify_email
from goods.models import SKU
from users import constants

from users.models import User, Address
from utils import tjws


class UserModelSerializer(serializers.Serializer):
    """用户序列化器"""
    id = serializers.IntegerField(read_only=True)
    token = serializers.CharField(read_only=True)
    default_address = serializers.IntegerField(read_only=True)
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
    def validate_allow(self, value):
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

        # 不需要保存在服务器的
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'email_active']


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

    def update(self, instance, validated_data):
        # 接收参数
        email = validated_data.get('email')
        # 修改
        instance.email = email

        # 保存之前需要发邮箱验证,用celery里面的方法发
        send_verify_email.delay(email, instance.generate_verify_email_token())

        # 保存
        instance.save()

        return instance


class AddressSerializer(serializers.ModelSerializer):
    province_id = serializers.IntegerField()
    city_id = serializers.IntegerField()
    district_id = serializers.IntegerField()

    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Address
        exclude = ['is_delete', 'create_time', 'update_time', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        address = super().create(validated_data)
        return address


class EmailActiveSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=200)

    def validate(self, attrs):
        token = attrs['token']

        data_dict = tjws.loads(token, constants.USER_EMAIL_TOKEN_EXPIRES)

        if data_dict is None:
            raise serializers.ValidationError('激活链接已经过期')

        attrs['user_id'] = data_dict['user_id']

        return attrs


class HistorySerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)

    def validate_sku_id(self, value):
        try:
            SKU.objects.get(pk=value)
        except:
            raise serializers.ValidationError("该商品不存在")

        return value

    def create(self, validated_data):
        sku_id = validated_data.get('sku_id')

        # 根据当前登录用户的id为键存一个列表
        # 连接redis
        redis_cli = get_redis_connection('history')

        key = 'history_%d' % self.context['request'].user.id
        # 1.先删除同样的商品id
        redis_cli.lrem(key, 0, sku_id)

        # 2.把商品id从左边存进去
        redis_cli.lpush(key, sku_id)

        # 3.如果数量大于5个那就删除最右边的那个
        if redis_cli.llen(key) > constants.BROWSE_HISTORY_LIMIT:
            redis_cli.rpop(key)

        return {'sku_id': sku_id}
