from django.shortcuts import render

from celery_tasks.main import app
from django.template import loader
from django.conf import settings
import os

from utils.goods_category import get_goods_category
from goods.models import SKU


@app.task(name='generate_static_sku_detail_html')
def generate_static_sku_detail_html(sku_id):
    """
    生成静态商品详情页面
    :param sku_id: 商品sku id
    """
    # 商品分类菜单
    categories = get_goods_category()

    # 获取当前sku的信息
    sku = SKU.objects.get(id=sku_id)
    sku.images = sku.skuimage_set.all()

    # 面包屑导航信息中的频道    手机》手机通讯》手机   只查一级分类就可以了
    goods = sku.goods
    goods.channel = goods.category1.goodschannel_set.all()[0]
    print(goods.channel)

    # 构建当前商品的规格键
    # sku_key = [规格1参数id， 规格2参数id， 规格3参数id, ...]
    # 所有规格加上参数id的列表
    sku_specs = sku.skuspecification_set.order_by('spec_id')  # 这个表里面存的是具体规格选项的id
    # <QuerySet [<SKUSpecification: 16: 华为 HUAWEI P10: 颜色 - 曜石黑>, <SKUSpecification: 16: 华为 HUAWEI P10: 版本 - 128GB>]>
    sku_key = []  # 这里面放的是当前SKU每个规格的选项参数的id
    for spec in sku_specs:  # 遍历每一个规格
        sku_key.append(spec.option.id)  # option_id

    # 获取当前商品的所有SKU
    skus = goods.sku_set.all()

    # 构建不同规格参数（选项）的sku字典
    # spec_sku_map = {
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     ...
    # }
    spec_sku_map = {}  # 构建一个sku对应其所有规格参数id的列表
    # 取出当前商品的每一个sku
    for s in skus:
        # 获取sku的规格参数
        s_specs = s.skuspecification_set.order_by('spec_id')
        # 用于形成规格参数-sku字典的键
        key = []
        for spec in s_specs:
            key.append(spec.option.id)
        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

    # 获取当前商品的规格信息     获取到的是对象，可以点出属性的那种
    # specs = [
    #    {
    #        'name': '屏幕尺寸',
    #        'options': [
    #            {1'value': '13.3寸', 'sku_id': xxx},
    #            {2'value': '15.6寸', 'sku_id': xxx}
    #        ]
    #    },
    #    {
    #        'name': '颜色',
    #        'options': [
    #            {1'value': '银色', 'sku_id': xxx},
    #            {2'value': '黑色', 'sku_id': xxx}
    #        ]
    #    },
    #    ...
    # ]
    # 所有规格信息，只是规格，例如颜色，内存，尺寸这种
    specs = goods.goodsspecification_set.order_by('id')  # 现在可以有两个规格，也可以有三个规格
    # 若当前sku的规格信息不完整，则不再继续
    # 就是判断一下这个商品里面的所有规格是否和sku的规格参数的数量是否相同，
    if len(sku_key) < len(specs):
        return
    # 遍历当前商品的每一个规格                      原理是给当前商品的每个sku的所有规格上面的所有选项加上对应的sku_id属性
    for index, spec in enumerate(specs):
        # 复制当前sku的规格键
        key = sku_key[:]  # [规格选项的id,规格选项的id,...]
        # 该规格的选项

        # 查询每一个规格所有的选项  只是一个列表
        options = spec.specificationoption_set.all()
        # 遍历每一个规格选项
        for option in options:  # 给每一个规格选项加[sku_id,sku_id,sku_id...]，如果没有sku那就加不了，那前端就是else了，就不能点也不会高亮

            # 在规格参数sku字典中查找符合当前规格的sku
            # 每变换一个规格的一个选项都表示换了一个具体的sku，不是一开始我们查到的那个了   这样就好理解了
            key[index] = option.id  # 就是每更换一个选项就查询有没有符合的sku，如果有就给这个选项加一个sku_id
            # 如果这个key可以取到，代表有一个存在的sku，赋值给这个选项的sku_id属性就可以了
            option.sku_id = spec_sku_map.get(tuple(key))

        # 这里给每一个规格加上所有选项
        spec.options = options

    # 渲染模板，生成静态html文件
    context = {
        'categories': categories,
        'goods': goods,
        'specs': specs,
        'sku': sku
    }

    # template = loader.get_template('detail.html')
    response = render(None, 'detail.html', context=context)
    # html_text = template.render(context)
    html_str = response.content.decode()
    file_path = os.path.join(settings.GENERATE_STATIC_HTML_PATH, 'goods/' + str(sku_id) + '.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_str)

    print('OK')
