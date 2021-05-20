from rest_framework.response import Response
from rest_framework import serializers

from areas.models import Area


class AreaListSerializer(serializers.ModelSerializer):
    # 展示很多省
    class Meta:
        model = Area
        fields = ['id', 'name']


class AreaRetrieveSerializer(serializers.ModelSerializer):
    # 展示一个省和下面的市  和市下面的区
    subs = AreaListSerializer(many=True, read_only=True)
    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']
