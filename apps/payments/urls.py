from django.urls import path

from .views import VerifyPaymentView, WebhookView

urlpatterns = [
    path("verify/<str:reference>/", VerifyPaymentView.as_view(), name="verify-payment"),
    path("webhook/", WebhookView.as_view(), name="webhook"),
]
