from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from common.utils.responses import customize_response
from apps.accounts.permissions import IsCartOwner
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.all()
    permission_classes = [IsCartOwner]
    http_method_names = ["post", "patch", "delete"]

    def get_queryset(self):
        """return only the user's cart item"""
        # Cart.objects.get_or_create(user=self.request.user)
        return self.queryset.filter(cart__user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return customize_response(response, "Item added successfully.")

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return customize_response(response, "Item updated successfully.")
    
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return customize_response(response, "Item deleted successfully.")


class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    permission_classes = [IsCartOwner]
    http_method_names = ["get", "delete"]

    def get_queryset(self):
        """return the user's cart"""
        cart, _ = self.queryset.get_or_create(user=self.request.user)
        return [cart]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if response.data is not None:
            response.data = response.data[0] # get the first cart which is the user's cart
        return customize_response(response, "Cart retrieved successfully.")

    def destroy(self, request, *args, **kwargs):
        """delete all the items in the cart (by deleting the cart)"""
        try:
            instance = self.queryset.get(user=self.request.user)
            instance.items.all().delete()
        except Cart.DoesNotExist:
            pass
        response = Response(data={}, status=status.HTTP_204_NO_CONTENT)
        return customize_response(response, "Cart cleared successfully.")

