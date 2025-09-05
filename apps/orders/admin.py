from django.contrib import admin

from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "status", "total_quantity", "customer", "payment_status", "total_amount", "created_at")

admin.site.register(OrderItem)
