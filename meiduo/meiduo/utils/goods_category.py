from collections import OrderedDict

from goods.models import GoodsChannel


def get_goods_category():
    # 1.查询分类数据
    # 1.1查询分类数据
    '''
    {
        组编号（同频道）:{
            一级分类channels：[]
            二级分类sub_cats：[]
        }
    }
    如：
    {
        1:{
            channels:[
                {手机},{相机},{数码}
            ],
            sub_cats:[二级分类]
        },
        2:{
            channels:[
                {电脑},{办公},{家用电器}
            ],
            sub_cats:[二级分类]
        },
        ....
    }
    '''
    categories = OrderedDict()

    channels = GoodsChannel.objects.order_by('group_id', 'sequence')

    for channel in channels:
        # 添加频道分组
        if channel.group_id not in categories:
            categories[channel.group_id] = {'channels': [], 'sub_cats': []}

        # 添加一级分类  categories[channel.group_id]这个可以让同组的进到一个频道
        categories[channel.group_id]['channels'].append({
            'id': channel.id,
            'name': channel.category.name,
            'url': channel.url
        })

        # 一个一级分类的全部二级分类
        sub_cats = channel.category.goodscategory_set.all()

        # 添加二级分类之前先给每一个二级分类添加对应的三级分类
        for sub in sub_cats:
            sub.sub_cats = sub.goodscategory_set.all()
            # 这里才是添加二级分类和与之对应的所有三级分类
            categories[channel.group_id]['sub_cats'].append(sub)
    # print(categories)

    # 记得返回一个categories字典，不然函数没有返回值了
    return categories