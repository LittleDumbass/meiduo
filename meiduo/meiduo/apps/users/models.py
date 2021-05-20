from django.contrib.auth.models import AbstractUser
from django.db import models

from users import constants
from utils import tjws
from utils.models import BaseModel


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False)
    default_address = models.OneToOneField('users.Address', related_name='user_addr', null=True, blank=True)

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_verify_email_token(self):
        # 用id加密
        data = {'user_id': self.id}
        # 加密
        token = tjws.dumps(data, constants.USER_EMAIL_TOKEN_EXPIRES)
        # 拼接 url
        return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token


class Address(BaseModel):
    user = models.ForeignKey(User, related_name='addresses')

    title = models.CharField(max_length=20)

    receiver = models.CharField(max_length=20)

    province = models.ForeignKey('areas.Area', related_name='province_addr')

    city = models.ForeignKey('areas.Area', related_name='city_addr')

    district = models.ForeignKey('areas.Area', related_name='district_addr')

    place = models.CharField(max_length=200)

    mobile = models.CharField(max_length=11)

    tel = models.CharField(max_length=20, null=True, blank=True)

    email = models.CharField(max_length=50, null=True, blank=True)

    is_delete = models.BooleanField(default=False)