from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from .models import Product, ProductImage
from .serializers import ProductSerializer, ProductImageSerializer


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(status=Product.ProductStatus.active)
    permission_classes = [IsAuthenticated, IsAdminUser]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_permissions(self):
        """return view permissions.
        All users can view Products,
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
        return super().get_queryset()


# TODO: catch permission denied exception and log it
