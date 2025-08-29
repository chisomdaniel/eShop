from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from common.utils.responses import customize_response
from .models import Product, ProductImage
from .serializers import ProductSerializer, ProductImageSerializer


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(status=Product.ProductStatus.active)
    permission_classes = [IsAuthenticated, IsAdminUser]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_permissions(self):
        """return view permissions.
        All users can view Products (IsAuthenticatedOrReadonly),
        Only admins can create, update or delete a product.
        """
        action_permission = {
            "list": [AllowAny],
            "retrieve": [AllowAny],
        }
        self.permission_classes = action_permission.get(
            self.action, self.permission_classes
        )
        return super().get_permissions()

    def get_queryset(self):
        """return queryset. filter queryset to include only 
        active product for normal users. Admins get full product list
        including products in draft and archive"""
        if IsAdminUser().has_permission(self.request, None):
            self.queryset = Product.objects.all()
        return self.queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return customize_response(response, "Products retrieved successfully.")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return customize_response(response, "Product created successfully.")

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return customize_response(response, "Product retrieved successfully.")

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return customize_response(response, "Product updated successfully.")

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return customize_response(response, "Product deleted successfully.")
