from rest_framework import serializers

from goods.models import SKU


class CartAddSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField()
    count = serializers.IntegerField(min_value=1)
    selected = serializers.BooleanField(required=False, default=True)

    def validate_sku_id(self, value):
        # 用过滤查询方法看能不能查到这个sku
        count = SKU.objects.filter(pk=value).count()

        if count <= 0:
            raise serializers.ValidationError("不存在该商品")
        return value


class CartSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(min_value=1)
    selected = serializers.BooleanField()

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'count', 'selected', 'default_image_url']


class CartDeleteSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField()

    def validate_sku_id(self, value):
        count = SKU.objects.filter(pk=value).count()

        if count <= 0:
            raise serializers.ValidationError("商品不存在")
        return value


class CartSelectSerializer(serializers.Serializer):
    selected = serializers.BooleanField()
