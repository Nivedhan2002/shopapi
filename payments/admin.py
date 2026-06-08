from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "status", "transaction_id", "amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("transaction_id", "order__user__email")
