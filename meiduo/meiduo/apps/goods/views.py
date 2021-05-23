from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from goods.models import SKU
from goods.serializers import SKUSerializer
from utils.pagination import SKUListPagination
from drf_haystack.viewsets import HaystackViewSet
from .serializers import SKUIndexSerializer


class SKUListView(ListAPIView):
    def get_queryset(self):
        return SKU.objects.filter(category_id=self.kwargs['category_id'])

    serializer_class = SKUSerializer

    # 分页
    # 在公用包里面定义一个分页类
    pagination_class = SKUListPagination

    # 排序
    filter_backends = [OrderingFilter]
    order_fields = ['create_time', 'price', 'sales']


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer

    # 分页
    pagination_class = SKUListPagination
