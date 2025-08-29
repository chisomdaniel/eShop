from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view

from .views import OrderViewSet

OrderViewSet = extend_schema_view(
    list=extend_schema(tags=["Orders"]),
    create=extend_schema(tags=["Orders"]),
    retrieve=extend_schema(tags=["Orders"]),
    destroy=extend_schema(tags=["Orders"]),
)(OrderViewSet)

order_list_create = OrderViewSet.as_view({
    "get": "list", "post": "create"
})

order_detail = OrderViewSet.as_view({
    "get": "retrieve"
})

urlpatterns = [
    path("", order_list_create, name="order-list"),
    path("<uuid:pk>/", order_detail, name="order-detail")
]
