import os
from collections import OrderedDict

from django.conf import settings
from django.shortcuts import render

from contents.models import ContentCategory
from goods.models import GoodsChannel
from utils.goods_category import get_goods_category


def generate_static_index_html():

    # 封装了获取商品分类的函数在utils那边
    categories = get_goods_category()

    # 2.广告数据
    # 所有广告
    contents = {}

    # 所有广告分类
    content_categories = ContentCategory.objects.all()

    # 遍历所有广告分类
    for category in content_categories:
        # 以每个分类的key作为键，分类下所有的广告内容作为值添加到广告的列表
        contents[category.key] = category.content_set.filter(status=True).order_by('sequence')

    # 生成index.html
    response = render(None, 'index.html', {'categories': categories, 'contents': contents})
    html_str = response.content.decode()

    # 写文件
    filename = os.path.join(settings.GENERATE_STATIC_HTML_PATH, 'index.html')  # 生成文件的路径和名称
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_str)

    print('OK')