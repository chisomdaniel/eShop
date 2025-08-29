from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from common.utils.responses import customize_response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer


# TODO: filter order by status
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

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return customize_response(response, "Order created successfully.")

# you cannot delete an order. if you cancel the payment will
# be cancelled forcing the order to be marked as CANCELLED.
