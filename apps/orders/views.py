from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from common.utils.responses import customize_response, success_response
from common.services.payment_service import initialize_payment
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        """the user can only see their Orders"""
        return self.queryset.filter(customer=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return customize_response(response, "Orders retrieved successfully.")

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return customize_response(response, "Order retrieved successfully.")

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        if (order.total_amount <= 0):
            """for orders with 0 fees and 0 prices"""
            return success_response(
                {"order_id": order.id},
                "NoPaymentRequired: Order created successfully",
                status_code=status.HTTP_201_CREATED)

        # create payment after creating order
        payment_data = {
            "email": order.customer.email,
            "amount": order.total_amount,
            "order_id": order.id
        }
        payment_res = initialize_payment(payment_data)
        res_data = {
            "order_id": order.id,
            "payment_data": payment_res["data"]
        }

        headers = self.get_success_headers(serializer.data)
        response = Response(res_data, status=status.HTTP_201_CREATED, headers=headers)
        return customize_response(response, "Order created successfully.")

