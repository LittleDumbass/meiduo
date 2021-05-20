from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings


def dumps(data, expires):
    """加密"""
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires)

    result = serializer.dumps(data).decode()

    return result


def loads(data, expires):
    """解密"""
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires)

    try:
        data_dict = serializer.loads(data)
        return data_dict
    except:
        # 这个token有可能会过期的，
        return None