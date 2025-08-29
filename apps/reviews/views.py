from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly

from common.utils.responses import customize_response
from apps.accounts.permissions import IsOwnerOrReadonly

from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadonly]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        product_id = self.request.query_params.get("product_id", None)
        if product_id:
            # TODO: validate the product ID is a valid uuid
            return self.queryset.filter(product_id=product_id)
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return customize_response(response, "Reviews retrieved successfully.")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return customize_response(response, "Review created successfully.")

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return customize_response(response, "Review retrieved successfully.")

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return customize_response(response, "Review updated successfully.")

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return customize_response(response, "Review deleted successfully.")
