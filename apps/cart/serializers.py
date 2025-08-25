from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.products.serializers import MinimalProductSerializer
from apps.products.models import Product

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """cart Item serializier"""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = [
            "id",
            "quantity",
            "product",
            "subtotal",
            "discounted_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "subtotal", "discounted_amount", "created_at", "updated_at"
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=CartItem.objects.all(),
                fields=["cart", "product"],
                message="Product already added to cart."
            )
        ]
    
    def get_fields(self):
        """make the product field read only on update"""
        fields = super().get_fields()
        request = self.context.get("request")
        if request and request.method in ["PUT", "PATCH"]:
            if "product" in fields:
                fields["product"].read_only = True
        return fields

    def validate_product(self, product):
        if product.status == Product.ProductStatus.archived:
            raise serializers.ValidationError({
                "product": "Product unavailable (Archived)"
            })
        if product.status == Product.ProductStatus.draft:
            raise serializers.ValidationError({
                "product": "Can't add a product in draft to cart"
            })
        if product.stock_quantity == 0 and not product.allow_backorder:
            raise serializers.ValidationError({
                "product": "This product is out of stock"
            })

    def validate(self, validated_data):
        request = self.context.get("request")
        user = request.user
        product: Product = validated_data.get("product", None)
        quantity = validated_data.get("quantity", None)
        if request.method == "POST":
            moq = product.min_order_quantity
            if product and (quantity < moq):
                raise serializers.ValidationError({
                    "quantity": f"Min order quantity (MOQ) for this product is {moq}"
                })
            validated_data["cart"], _ = Cart.objects.get_or_create(user=user)
            if not quantity:
                validated_data["quantity"] = product.min_order_quantity
        if product and quantity and quantity and product and quantity < product.stock_quantity:
            raise serializers.ValidationError({
                "quantity": "Not enough stock to fufil order"
            })
        return validated_data

    def update(self, instance, validated_data):
        """only the quantity is available for update"""
        quantity = validated_data.get("quantity", 0)
        self.validate_product(instance.product)
        return super().update(instance, validated_data)

    def to_representation(self, instance: CartItem):
        """a product should be represented in it's minimal
        view in the response"""
        data = super().to_representation(instance)
        data["product"] = MinimalProductSerializer(instance.product).data
        return data


class CartSerializer(serializers.ModelSerializer):
    """Cart serializer. Read only"""
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "subtotal",
            "discounts",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["subtotal", "discounts", "total_amount", "created_at", "updated_at"]
