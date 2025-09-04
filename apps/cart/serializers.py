from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.products.serializers import MinimalProductSerializer
from apps.products.models import Product

from .models import Cart, CartItem


def check_product_exists(validated_data):
    """checks if product already exist in the user's
    cart. Returns the item and quantity"""
    product = validated_data.get("product")
    cart = validated_data.get("cart")
    item = cart.items.filter(product_id=product).first()
    if item:
        """update the data so the create method easily verify
        without accessing the db again"""
        validated_data.update({"exists": True, "item": item})
        return item, item.quantity
    return None, None


class CartItemSerializer(serializers.ModelSerializer):
    """cart Item serializier"""

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
            raise serializers.ValidationError("Product unavailable (Archived)")
        if product.status == Product.ProductStatus.draft:
            raise serializers.ValidationError("Can not order a product in draft")
        if product.stock_quantity == 0 and not product.allow_backorder:
            raise serializers.ValidationError("This product is out of stock")
        return product

    def validate(self, validated_data):
        request = self.context.get("request")
        user = request.user
        validated_data["cart"], _ = Cart.objects.get_or_create(user=user)

        product: Product = validated_data.get("product")
        if not product and request.method in ["PUT", "PATCH"]:
            validated_data["product"] = getattr(self.instance, "product", None)
            product = validated_data["product"]

        quantity = validated_data.get("quantity", None)
        """if quantity is not provided it defaults to the MOQ.
        If item exist, the previous quantity is increased by 1 or
        updated to the new quantity provided in the request if available
        """
        item, item_quantity = check_product_exists(validated_data)
        if item_quantity and not quantity:
            quantity = item_quantity + 1

        moq = product.min_order_quantity
        if not quantity and not item:
            quantity = moq
        if product and (quantity < moq):
            raise serializers.ValidationError({
                "quantity": f"Min order quantity (MOQ) for this product is {moq}"
            })
        if product and quantity and quantity and product and quantity > product.stock_quantity:
            raise serializers.ValidationError({
                "quantity": "Not enough stock to fufil order"
            })

        validated_data["quantity"] = quantity
        return validated_data

    def create(self, validated_data):
        """check if the product already exist in the user's cart and just update it"""
        if validated_data.get("exists"):
            """this is already added in the validate method if item exist"""
            item = validated_data.pop("item")
            return self.update(item, validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """only the quantity is available for update"""
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
            "no_of_items",
            "items",
            "subtotal",
            "discounts",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["subtotal", "discounts", "total_amount", "created_at", "updated_at"]
