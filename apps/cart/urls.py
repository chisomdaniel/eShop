from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view

from .views import CartViewSet, CartItemViewSet

CartViewSet = extend_schema_view(
    list=extend_schema(tags=["Cart"]),
    destroy=extend_schema(tags=["Cart"])
)(CartViewSet)

CartItemViewSet = extend_schema_view(
    create=extend_schema(tags=["Cart"]),
    partial_update=extend_schema(tags=["Cart"]),
    destroy=extend_schema(tags=["Cart"])
)(CartItemViewSet)

# list and clear items in cart
cart_item_list = CartViewSet.as_view({
    "get": "list", "delete": "destroy"
})

# add item to cart
cart_item = CartItemViewSet.as_view({
    "post": "create"
})

# update and delete an item
cart_item_detail = CartItemViewSet.as_view({
    "put": "update", "delete": "destroy"
})

urlpatterns = [
    path("items/", cart_item_list, name="cart-list"),
    path("item/add/", cart_item, name="cart-item-add"),
    path("item/<uuid:pk>/", cart_item_detail, name="cart-item-detail"),
]
