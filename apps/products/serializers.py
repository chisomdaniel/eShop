import os
import uuid
from PIL import Image
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Product, Category, Tag, ProductImage


# TODO: add serializers to create Categories and Tags


class ProductImageUploadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True, write_only=True)

    class Meta:
        fields = ["image"]
    
    def create(self, validated_data):
        # TODO: change implementation to upload to cloud storage here
        image = validated_data.pop("image", None)
        try:
            if image:
                ext = os.path.splitext(image.name)[1]
                image_name = f"product-{str(uuid.uuid4().hex)}.{ext}"
                file_location = os.path.join(
                    "images",
                    "product_images",
                    image_name
                )
                img = Image.open(validated_data.get("image"))
                img.save(file_location)
                # use Reverse to get the link with the image name
                validated_data["image_url"] = file_location
                return validated_data
        except Exception as e:
            raise ValidationError("Error while uploding product image, please try again")
            # TODO: LOG
    
    def to_representation(self, instance: dict[str, str]):
        """Instance can be a dict as returned from the `create` method in create operation,
        or a ProductImage instance in read operation"""
        return instance


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "alt_text", "position"]
        # read_only_fields = ["image_url"]


# TODO: display rating aggregate on product on the product view
# TODO: put a boolean `in_cart` and `quantity in cart` to show if a product is in a user's cart and the quantity

class ProductSerializer(serializers.ModelSerializer):
    """The product serializer"""
    categories = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Category.objects.all()
    )
    tags = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Tag.objects.all(), allow_null=True
    )
    images = ProductImageSerializer(many=True, required=False)

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
    
    def create(self, validated_data):
        """Create a product. Take the image data from the input and
        create each image in db, linking each image to the product"""
        images = validated_data.pop("images", None)
        product = super().create(validated_data)
        if images:
            for image_dict in images:
                ProductImage.objects.create(product=product, **image_dict)
        return product
    
    def update(self, instance, validated_data):
        """
        Update a product info and also allow for adding more images.
        Existing images cannot be edited/updated with this serializer. Use
        Image serializer to update existing images.
        """
        images = validated_data.pop("images", None) # add image to a product
        product = super().update(instance, validated_data)
        if images:
            for image_dict in images:
                ProductImage.objects.create(product=product, **image_dict)
        return product


class MinimalProductSerializer(serializers.ModelSerializer):
    """Minimal product serializer for cartItem and orderItem view"""
    image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "image",
            "in_stock",
            "min_order_quantity",
            "status"
        ]
        read_only_fields = fields.copy()

    def get_image(self, obj: Product):
        """return the first image for cart/order item display"""
        image: ProductImage = obj.images.first()
        return image.image_url if image else None
    
    def get_in_stock(self, obj: Product):
        return True if obj.stock_quantity > 0 else False

