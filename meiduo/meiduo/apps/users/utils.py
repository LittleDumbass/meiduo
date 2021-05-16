import re
from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):

    return {
        'token': token,
        'username': user.username,
        'user_od': user.id
    }


class MyModel(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断是手机号码还是用户名
        try:
            # 查询
            if re.match(r'1[3-9]\d{9}', username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)
        except:
            return None
        # 校验密码
        if user.check_password(password):
            # 返回user
            return user
        else:
            return None


