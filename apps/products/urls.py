from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view

from .views import ProductViewSet

ProductViewSet = extend_schema_view(
    list=extend_schema(tags=["Products"]),
    create=extend_schema(tags=["Products"]),
    retrieve=extend_schema(tags=["Products"]),
    partial_update=extend_schema(tags=["Products"]),
    destroy=extend_schema(tags=["Products"]),
)(ProductViewSet)

product_list = ProductViewSet.as_view({
    "get": "list", "post": "create"
})
product_detail = ProductViewSet.as_view({
    "get": "retrieve", "patch": "partial_update", "delete": "destroy"
})

urlpatterns = [
    path("", product_list, name="product-list"),
    path("<uuid:pk>/", product_detail, name="product-detail")
]
