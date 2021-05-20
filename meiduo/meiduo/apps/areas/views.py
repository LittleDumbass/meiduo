from rest_framework.response import Response
from rest_framework import generics
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.models import Area
from areas.serializers import AreaListSerializer, AreaRetrieveSerializer


# class AreaListView(generics.ListAPIView):
#     # 这个是查多个，查出很多省
#     queryset = Area.objects.filter(parent__isnull=True)
#     serializer_class = AreaListSerializer
#
#
# class AreaRetrieveView(generics.RetrieveAPIView):
#     # 这个是查一个，查到一个省之后，用关系属性展示其他的市
#     # 查到一个市之后展示其他的区
#     queryset = Area.objects.all()
#     serializer_class = AreaRetrieveSerializer


class AreaViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    # 视图集提供的方法和路由，给各个方法指定查询集和序列化器就好了，这两个东西也可以看情况重写
    def get_queryset(self):
        # 在视图集中，我们可以通过action对象属性来获取当前请求视图集时的action动作是哪个。
        if self.action == 'list':
            return Area.objects.filter(parent__isnull=True)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        # 在视图集中，我们可以通过action对象属性来获取当前请求视图集时的action动作是哪个。
        if self.action == 'list':
            return AreaListSerializer
        else:
            return AreaRetrieveSerializer