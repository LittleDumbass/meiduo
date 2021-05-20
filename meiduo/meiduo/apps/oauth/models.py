from django.db import models
from utils.models import BaseModel


class QQUser(BaseModel):
    """QQ用户"""
    user = models.ForeignKey('users.User')
    openid = models.CharField(max_length=64)

    class Meta:
        db_table = 'tb_auth_qq'