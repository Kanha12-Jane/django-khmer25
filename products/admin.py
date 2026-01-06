from django.contrib import admin
from unfold.admin import ModelAdmin  # ✅ Unfold ModelAdmin
from django.db import transaction
from django.utils.html import format_html

from .models import (
    Category, Product,
    Cart, CartItem,
    Order, OrderItem, PaymentProof
)

# ==========================
# CATEGORY
# ==========================
@admin.register(Category)
class CategoryAdmin(ModelAdmin):  # ✅ changed
    list_display = ("id", "name", "parent")
    list_filter = ("parent",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("parent__id", "id")


# ==========================
# PRODUCT
# ==========================
@admin.register(Product)
class ProductAdmin(ModelAdmin):  # ✅ changed
    list_display = (
        "id", "image_preview", "name", "category",
        "price", "discount_percent", "stock",
        "is_in_stock", "is_new", "is_featured", "is_active", "created_at",
    )
    list_filter = ("category", "is_new", "is_featured", "is_active", "is_in_stock")
    search_fields = ("name", "slug", "sku")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview", "created_at", "updated_at", "is_in_stock")
    list_editable = ("price", "stock", "is_new", "is_featured", "is_active")
    ordering = ("-created_at",)

    fieldsets = (
        ("Basic Info", {"fields": ("name", "slug", "sku", "category")}),
        ("Image", {"fields": ("image", "image_preview")}),
        ("Pricing", {"fields": ("price", "discount_percent")}),
        ("Stock & Status", {"fields": ("stock", "is_in_stock", "is_new", "is_featured", "is_active")}),
        ("Description", {"fields": ("description", "unit")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="80" style="border-radius:8px;border:1px solid #eee;" />'
                "</a>",
                obj.image.url,
            )
        return "-"
    image_preview.short_description = "Image"


# ==========================
# CART (optional show)
# ==========================
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    autocomplete_fields = ("product",)
    fields = ("product", "qty")


@admin.register(Cart)
class CartAdmin(ModelAdmin):  # ✅ changed
    list_display = ("id", "user", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
    inlines = [CartItemInline]
    ordering = ("-updated_at",)


# ==========================
# ORDER + PAYMENT PROOF
# ==========================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product_name", "unit_price", "qty")
    readonly_fields = ("product_name", "unit_price", "qty")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(ModelAdmin):  # ✅ changed
    list_display = ("id", "order_code", "user", "status", "total", "phone", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_code", "user__username", "user__email", "phone")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]

    readonly_fields = ("order_code", "created_at", "total")
    fieldsets = (
        ("Order", {"fields": ("order_code", "user", "status", "total", "created_at")}),
        ("Shipping", {"fields": ("phone", "address", "note")}),
    )


@admin.register(PaymentProof)
class PaymentProofAdmin(ModelAdmin):  # ✅ changed
    list_display = ("id", "order_code", "user", "status", "created_at", "image_preview")
    list_filter = ("status", "created_at")
    search_fields = ("order__order_code", "order__user__username", "order__user__email")
    ordering = ("-created_at",)

    readonly_fields = ("created_at", "image_preview", "order", "status")
    fieldsets = (
        ("Order", {"fields": ("order",)}),
        ("Proof", {"fields": ("image", "image_preview", "note")}),
        ("Verify", {"fields": ("status", "created_at")}),
    )

    actions = ["approve_proof", "reject_proof"]

    def order_code(self, obj):
        return obj.order.order_code
    order_code.short_description = "Order Code"

    def user(self, obj):
        return obj.order.user
    user.short_description = "User"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="120" style="border-radius:10px;border:1px solid #eee;" />'
                "</a>",
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Screenshot"

    @admin.action(description="✅ Approve selected proofs (Proof=APPROVED, Order=PAID)")
    def approve_proof(self, request, queryset):
        updated = 0
        with transaction.atomic():
            for proof in queryset.select_related("order").select_for_update():
                proof.status = PaymentProof.VerifyStatus.APPROVED
                proof.save(update_fields=["status"])
                proof.order.status = Order.Status.PAID
                proof.order.save(update_fields=["status"])
                updated += 1
        self.message_user(request, f"Approved {updated} proof(s).")

    @admin.action(description="❌ Reject selected proofs (Proof=REJECTED, Order=REJECTED)")
    def reject_proof(self, request, queryset):
        updated = 0
        with transaction.atomic():
            for proof in queryset.select_related("order").select_for_update():
                proof.status = PaymentProof.VerifyStatus.REJECTED
                proof.save(update_fields=["status"])
                proof.order.status = Order.Status.REJECTED
                proof.order.save(update_fields=["status"])
                updated += 1
        self.message_user(request, f"Rejected {updated} proof(s).")
