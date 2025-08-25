from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import MethodNotAllowed

from apps.products.serializers import MinimalProductSerializer
from apps.discounts.models import Discounts
from apps.products.models import Product

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """order item serializers"""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    applied_discount = serializers.SlugRelatedField(
        slug_field="code", queryset=Discounts.objects.all(), allow_null=True
    )
    order = serializers.SlugRelatedField(
        slug_field="order_number", read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "quantity", #
            "product", #
            "applied_discount", #
            "order",
            "subtotal",
            "discounted_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "order", "subtotal", "discounted_amount", "created_at", "updated_at"
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=OrderItem.objects.all(),
                fields=["order", "product"],
                message="Product already added to order."
            )
        ]
    
    def validate_product(self, product):
        if product.status == Product.ProductStatus.archived:
            raise serializers.ValidationError({
                "product": "Product unavailable (Archived)"
            })
        if product.status == Product.ProductStatus.draft:
            raise serializers.ValidationError({
                "product": "Can not order a product in draft"
            })
        if product.stock_quantity == 0 and not product.allow_backorder:
            raise serializers.ValidationError({
                "product": "This product is out of stock"
            })
    
    def validate(self, validated_data):
        request = self.context.get("request", None)
        product: Product = validated_data.get("product", None)
        quantity = validated_data.get("quantity", None)
        if not request:
            raise serializers.ValidationError("The request context must be passed to the Order Item serializer")
        if request.method in ["PUT", "PATCH"]:
            raise MethodNotAllowed(406, detail="Cannot update an order item once created. Cancel and create another.")

        user = request.user
        moq = product.min_order_quantity
        if product and (quantity < moq):
            raise serializers.ValidationError({
                "quantity": f"Min order quantity (MOQ) for this product is {moq}"
            })
        if quantity and product and quantity > product.stock_quantity:
            raise serializers.ValidationError({
                "quantity": "Not enough stock to fufil order"
            })
        elif not quantity:
            validated_data["quantity"] = product.min_order_quantity
        return validated_data


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer"""
    items = OrderItemSerializer(many=True)
    applied_discount = serializers.SlugRelatedField(
        slug_field="code", queryset=Discounts.objects.all(), allow_null=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "items", #
            "notes", #
            "applied_discount", #
            "order_number",
            "status",
            "customer", #
            "subtotal",
            "discounts",
            "delivery_fee",
            "other_fees",
            "total_amount",
            "payment_status",
            "delivery_status",
            "delivery_address_line1",
            "delivery_address_line2",
            "delivery_address_closest_busstop",
            "delivery_address_city",
            "delivery_address_state",
            "delivery_address_country",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "order_number",
            "status", # status can only be updated by store owner
            "customer",
            "subtotal",
            "discounts",
            "delivery_fee",
            "other_fees",
            "total_amount",
            "payment_status",
            "delivery_status",
            "created_at",
            "updated_at",
        ]

    def validate(self, validated_data):
        request = self.context.get("request", None)
        if not request:
            raise serializers.ValidationError("The request context must be passed to the Order serializer")
        if request.method in ["PUT", "PATCH"]:
            raise MethodNotAllowed(request.method, detail="Cannot update an order once created. Cancel and create another.")

    def create(self, validated_data):
        """create an order. an order must have at least one order item"""
        request = self.context.get("request", None)
        order_items = validated_data.pop("items")
        validated_data["customer"] = request.user

        order = super().create(validated_data)
        for item in order_items:
            OrderItem.objects.create(order=order, **item)

        return order


# TODO: factor in the "store currency" when placing order
# TODO: reduce stock by order quantity when creating orders
# TODO: increase purchase count after a successful order payment
# TODO: test what happens when no item is provided or when an empty dict of items is provided
# TODO: return a count of items in the user's cart and order

# TODO: test discount code validity in items and order
# TODO: test checkout flow and see update. Done
# TODO: use their primary delivery address by default. they can update it
