from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view

from .views import ReviewViewSet

ReviewViewSet = extend_schema_view(
    list=extend_schema(tags=["Reviews"]),
    create=extend_schema(tags=["Reviews"]),
    retrieve=extend_schema(tags=["Reviews"]),
    partial_update=extend_schema(tags=["Reviews"]),
    destroy=extend_schema(tags=["Reviews"]),
)(ReviewViewSet)

review_list = ReviewViewSet.as_view({
    "get": "list", "post": "create"
})
review_detail = ReviewViewSet.as_view({
    "get": "retrieve", "patch": "partial_update", "delete": "destroy"
})

urlpatterns = [
    path("", review_list, name="review-list"),
    path("<uuid:pk>/", review_detail, name="review-detail")
]