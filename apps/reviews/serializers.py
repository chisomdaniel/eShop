from rest_framework import serializers
from django.contrib.auth import get_user_model


from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="first_name", queryset=get_user_model().objects.all()
    )
    
    class Meta:
        model = Review
        field = [
            "id",
            "rating",
            "comment",
            "created_at",
            "user",
            "product",
        ]
        read_only_fields = ["created_at", "user"]
    
    def validate_rating(self, value):
        """Validate the rating data"""
        if value < 1 and value > 5:
            raise serializers.ValidationError("Rating must be within 1 to 5")
        return value
    
    def validate(self, validated_data):
        """ensure only one review per user per product"""
        request = self.context["request"]
        if request.method == "POST":
            user = request.user
            product_id = validated_data.pop("product")
            if Review.objects.filter(product=product_id, user=user).exists():
                raise serializers.ValidationError("You have already reviewed this product")
        elif request.method in ["PUT", "PATCH"]:
            if "product" in validated_data:
                raise serializers.ValidationError({
                    "product": "You can not update the product"
                })        
        return validated_data

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["user"] = request.user
        return super().create(**validated_data)

