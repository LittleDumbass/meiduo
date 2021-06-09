import base64
import pickle


def dumps(mydict):
    """字典转字符串"""

    # 将字典转字节b'\x**\x**..'
    byte_hex = pickle.dumps(mydict)

    # 加密b'a-zA-Z0-9='
    byte_str64 = base64.b64encode(byte_hex)

    # 转字符串
    return byte_str64.decode()


def loads(mystr):
    """字符串转字典"""

    # 字符串转64的加密字节
    byte_str64 = mystr.encode()

    # 64的字节解密
    byte_hex = base64.b64decode(byte_str64)

    # 转字典
    return pickle.loads(byte_hex)
