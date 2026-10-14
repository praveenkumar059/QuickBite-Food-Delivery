from django.contrib import admin
from .models import FoodItem, Order, OrderItem
@admin.register(FoodItem)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'available']
    list_filter = ['category', 'available']
    search_fields = ['name', 'description']
class ItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['food', 'food_name', 'unit_price', 'quantity']
    can_delete = False
    def has_add_permission(self, request, obj=None):
        return False
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'phone', 'address']
    readonly_fields = ['user', 'address', 'phone', 'total', 'created_at', 'checkout_token']
    inlines = [ItemInline]
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.site_header = 'QuickBite Administration'
