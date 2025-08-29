from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model


from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    review_by = serializers.SerializerMethodField()
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            "comment",
            "created_at",
            "updated_at",
            "review_by",
            "user",
            "product",
        ]
        read_only_fields = ["review_by", "created_at", "updated_at", "user"]
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=["product", "user"],
                message="You have already reviewed this product"
            )
        ]

    def validate(self, validated_data):
        """ensure only one review per user per product"""
        request = self.context["request"]
        if request.method in ["PUT", "PATCH"]:
            if "product" in validated_data:
                raise serializers.ValidationError({
                    "product": "You can not update the product"
                })
        return validated_data
    
    def get_review_by(self, obj):
        return obj.user.full_name


# TODO test what happens if an invalid product ID is used to create a review

