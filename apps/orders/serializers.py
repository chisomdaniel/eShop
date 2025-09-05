from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import MethodNotAllowed
from django.db import transaction

from apps.products.serializers import MinimalProductSerializer
from apps.discounts.models import Discounts
from apps.products.models import Product
from common.services.payment_service import initialize_payment

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """order item serializers"""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    applied_discount = serializers.SlugRelatedField(
        slug_field="code", queryset=Discounts.objects.all(), required=False
    )
    order = serializers.SlugRelatedField(
        slug_field="order_number", read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "quantity",
            "product",
            "applied_discount",
            "order",
            "subtotal",
            "discounted_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "order", "subtotal", "discounted_amount", "created_at", "updated_at"
        ]
    
    def validate_product(self, product):
        if product.status == Product.ProductStatus.archived:
            raise serializers.ValidationError("Product unavailable (Archived)")
        if product.status == Product.ProductStatus.draft:
            raise serializers.ValidationError("Can not order a product in draft")
        if product.stock_quantity == 0 and not product.allow_backorder:
            raise serializers.ValidationError("This product is out of stock")
        return product
    
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
        slug_field="code", queryset=Discounts.objects.all(), required=False
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "total_quantity",
            "items",
            "notes",
            "applied_discount",
            "order_number",
            "status",
            "customer",
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
            "status",
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
        if not validated_data.get("items"):
            raise serializers.ValidationError({
                "items": "Order must contain at least one item"
            })
        request = self.context.get("request", None)
        if not request:
            raise serializers.ValidationError("The request context must be passed to the Order serializer")
        if request.method in ["PUT", "PATCH"]:
            raise MethodNotAllowed(request.method, detail="Cannot update an order once created. Cancel and create another.")
        validated_data["customer"] = request.user
        return validated_data

    @transaction.atomic()
    def create(self, validated_data):
        """create an order"""
        order_items = validated_data.pop("items")

        order = Order.objects.create(**validated_data)
        added_products = {}
        total_quantity = 0
        for item in order_items:
            """ensure product is unique in Order"""
            if added_products.get(item["product"].id, None):
                raise serializers.ValidationError("You cannot add the same product twice. Increase the quantity instead")
            OrderItem.objects.create(order=order, **item)
            total_quantity += item["quantity"]
            added_products[item["product"].id] = True
            """reduce the stock quantity from the existing stock
            and increase product purchase count"""
            product: Product = item["product"]
            product.stock_quantity -= item["quantity"]
            product.purchase_count += item["quantity"]
            product.save(update_fields=["stock_quantity", "purchase_count"])

        order.total_quantity = total_quantity
        order.save(update_fields=["total_quantity"])
        return order
