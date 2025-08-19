import os
import uuid
from PIL import Image
from rest_framework import serializers

from .models import Product, Category, Tag, ProductImage


class MinimalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        field = ["name"]


class MinimalTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        field = ["name"]


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)

    class Meta:
        model = ProductImage
        field = ["image", "image_url", "alt_text", "position"]
    
    def create(self, validated_data):
        image = validated_data.pop("image", None)
        if image:
            ext = os.path.splitext(image.name)[1]
            file_location = os.path.join(
                "product_images",
                f"product-{str(uuid.uuid4().hex)[:7]}.{ext}"
            )
            img = Image.open(validated_data.get("image"))
            img.save(file_location)
        super().create(**validated_data)


class ProductSerialzer(serializers.ModelSerializer):
    """The product serializer"""
    categories = MinimalCategorySerializer(many=True)
    tags = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Tag.objects.all()
    )
    image = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock_quantity",
            "min_order_quantity",
            "status",
            "type",
            "categories",
            "tags",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at", "updated_at"
        ]

    

# Test what happens when you put a negative stock number
