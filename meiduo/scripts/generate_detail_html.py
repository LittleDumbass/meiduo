#!/usr/bin/env python
# 在当前环境中查找python的目录  相当于which python 命令

# !/home/python/.virtualenvs/meiduo/bin/python
# 指定当前文件执行时，使用的解释器

# 设置环境变量
import sys
import os
import django


sys.path.insert(0, '../')  # 添加Python导包路径
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo.settings.dev")  # 使用django的环境变量配置
django.setup()  # 引入django

from celery_tasks.html.tasks import generate_static_sku_detail_html
from goods.models import SKU


if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        generate_static_sku_detail_html(sku.id)