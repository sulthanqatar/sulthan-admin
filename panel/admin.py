from django.contrib import admin

from panel.models import (
    AuditTrail,
    B2BRegistration,
    Banner,
    Coupon,
    Customer,
    InternalUser,
    Order,
    OrderLine,
    Product,
    ProductCategory,
    ProductImage,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "price", "stock", "is_active", "stock_updated_at")
    list_filter = ("category", "is_active")
    search_fields = ("sku", "name")
    inlines = [ProductImageInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "email")


@admin.register(InternalUser)
class InternalUserAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "role", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("name", "email")


@admin.register(B2BRegistration)
class B2BRegistrationAdmin(admin.ModelAdmin):
    list_display = ("company", "contact_name", "email", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("company", "email")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "customer", "status", "created_at")
    list_filter = ("status",)
    inlines = [OrderLineInline]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "updated_at")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "is_active", "expires_on")
    search_fields = ("code",)


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "target")
    search_fields = ("actor", "action", "target")
