from rest_framework.response import Response
from rest_framework.views import APIView

from oauth import constants
from oauth.models import QQUser
from oauth.serializers import QQUserAuthSerializer
from users.models import User
from utils.jwt_token import generate
from .qq_sdk import OAuthQQ
from utils import tjws


class QQUrlView(APIView):
    """获取QQ授权登录的url"""

    def get(self, request):
        """get请求返回url"""
        # 先获取请求参数的next作为state传入OAUTH, state是登录成功后跳转的界面
        state = request.query_params.get('next')
        # 创建QQsdk的对象
        oauth = OAuthQQ(state=state)
        # 获取url
        login_url = oauth.get_qq_login_url()
        # 返回
        return Response({"login_url": login_url})


class QQLoginView(APIView):
    """QQ登录视图"""
    def get(self, request):
        """先获取openid, 判断是否已经存在openid，存在就是授权登录过了，直接就可以返回状态保持了"""
        # 获取code
        code = request.query_params.get('code')
        # 获取access_token
        oauth = OAuthQQ()
        access_token = oauth.get_access_token(code)
        # 获取openid
        openid = oauth.get_openid(access_token)

        # 接下来就可以判断是否已经授权过了，就用这openid来判断的
        try:
            # 在qquser这边查询
            qquser = QQUser.objects.get(openid=openid)
        except:
            # 这里是不存在的情况。 返回access_token包含openid的，以便用这个openid来授权用户
            # 用itsdangerous里面的TimedJSONWebSignatureSerializer来加密这个openid
            access_token = tjws.dumps({"openid": openid}, constants.QQ_AUTH_TOKEN_EXPIRES)
            return Response({"access_token": access_token})

        else:
            # 这里是存在的情况, 直接返回状态保持就可以登录了
            return Response({
                "username": qquser.user.username,
                "user_id": qquser.user.id,
                "token": generate(qquser.user)
            })

    """
    如果之前没有openid授权过，就表示第一次授权咯，让用户填写手机号码和密码还有验证码，如果用手机可以查出一个用户就再校验密码，密码再正确就表示
    这个手机号码之前已经注册过了虽然不是用QQ授权登录注册的，如果验证密码失败那就表示这个手机号码被其他用户注册过了，现在这个用户填写的手机号码是
    不可以再被用来注册了，那如果用手机号码查不到这个用户就表示没有用户和这个手机号码对应，那就重新创建一个用户，保存，然后后面再把这个用户和QQ授权
    用户绑定关系，qquser.user = 这个用户， qquser.openid=这个QQ的openid，这样一个QQ就和一个用户对应了
    """
    def post(self, request):
        """绑定视图, 来到这里就表示这个QQ之前没有授权和一个用户绑定过"""

        # 获取数据
        data = request.data
        # 验证数据
        serializer = QQUserAuthSerializer(data=data)
        if not serializer.is_valid():
            return Response({"message": serializer.errors})
        # 保存用户， 序列化器返回的可能是创建出来的用户，也可能是原有的用户，如果手机已经注册过了就会返回注册过的用户信息
        qquser = serializer.save()

        # 返回响应
        return Response({
            "username": qquser.user.username,
            "id": qquser.user.id,
            "token": generate(qquser.user)
        })

