import random
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework import serializers
from . import constants
from celery_tasks.sms.tasks import send_sms_code


class SMSCodeView(APIView):
    def get(self, request, mobile):

        """发送短信验证码"""
        # 连接redis
        redis_cli = get_redis_connection('sms_code')
        # 检查60s之内是否发过短信
        if redis_cli.get('sms_flag_' + mobile):
            raise serializers.ValidationError("发送验证码过于频繁")
        # 生成随机验证码
        sms_code = random.randint(100000, 999999)
        print(sms_code)
        # 保存短信验证码内容和时间标志
        # redis_cli.setex('SMS_CODE_'+mobile, constants.SMS_CODE_EXPIRES, sms_code)
        # redis_cli.setex('SMS_FLAG_'+mobile, constants.SMS_FLAG_EXPIRES, 1)

        redis_pipeline = redis_cli.pipeline()
        redis_pipeline.setex('sms_code_'+mobile, constants.SMS_CODE_EXPIRES, sms_code)
        redis_pipeline.setex('sms_flag_'+mobile, constants.SMS_FLAG_EXPIRES, 1)
        redis_pipeline.execute()

        # 发送短信
        # CCP.sendTemplateSMS(mobile, sms_code, constants.SMS_CODE_EXPIRES/60, 1)
        # send_sms_code.delay(mobile, sms_code, constants.SMS_CODE_EXPIRES/60, 1)
        # 响应
        return Response({"message": "OK"})

