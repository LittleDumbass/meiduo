#!/usr/bin/env python
# 在当前环境中查找python的目录

# !/home/python/.virtualenvs/meiduo/bin/python
# 指定当前文件执行时，使用的解释器

# 设置环境变量
import sys
import os
import django

sys.path.insert(0, '../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo.settings.dev")
django.setup()