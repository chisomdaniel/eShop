from rest_framework import serializers

class VerifyPaymentSerializer(serializers.Serializer):
    reference = serializers.CharField(required=True)
