from decimal import Decimal
from rest_framework import serializers

from .models import (
    Category, Product,
    Cart, CartItem,
    Order, OrderItem, PaymentProof
)

# ----------------------------
# Category Serializer (Nested)
# ----------------------------
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "image"]


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "image", "slug", "parent", "subcategories"]


# -----------------------------------------
# Small serializer for "Related Products"
# -----------------------------------------
class RelatedProductSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    price_text = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "image",
            "price", "discount_percent",
            "final_price", "price_text",
            "unit", "is_in_stock",
        ]

    def get_final_price(self, obj):
        return obj.final_price

    def get_price_text(self, obj):
        p = Decimal(obj.final_price)
        return f"{p:,.0f}៛ / {obj.unit}" if obj.unit else f"{p:,.0f}៛"


# -----------------------------------------
# Product Serializer (LIST)
# -----------------------------------------
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True
    )

    final_price = serializers.SerializerMethodField()
    price_text = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "sku", "image",
            "price", "discount_percent", "final_price", "price_text",
            "stock", "is_in_stock", "is_new", "is_featured", "is_active",
            "description", "unit", "created_at", "updated_at",
            "category", "category_id",
        ]

    def get_final_price(self, obj):
        return obj.final_price

    def get_price_text(self, obj):
        p = Decimal(obj.final_price)
        return f"{p:,.0f}៛ / {obj.unit}" if obj.unit else f"{p:,.0f}៛"


class ProductDetailSerializer(ProductSerializer):
    related_products = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ["related_products"]

    def get_related_products(self, obj):
        if not obj.category_id:
            return []
        qs = (
            Product.objects
            .filter(category_id=obj.category_id, is_active=True)
            .exclude(id=obj.id)
            .order_by("-created_at")[:10]
        )
        return RelatedProductSerializer(qs, many=True, context=self.context).data


# ==========================
# ✅ CART SERIALIZERS
# ==========================
class CartProductSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    price_text = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "image",
            "price", "discount_percent",
            "final_price", "price_text",
            "unit", "is_in_stock",
        ]

    def get_final_price(self, obj):
        return obj.final_price

    def get_price_text(self, obj):
        p = Decimal(obj.final_price)
        return f"{p:,.0f}៛ / {obj.unit}" if obj.unit else f"{p:,.0f}៛"


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.all(),
        write_only=True
    )
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "qty", "line_total"]

    def get_line_total(self, obj):
        return Decimal(obj.qty) * Decimal(obj.product.final_price)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    total_text = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total", "total_text"]

    def get_total(self, cart: Cart):
        total = Decimal("0")
        for it in cart.items.select_related("product").all():
            total += Decimal(it.qty) * Decimal(it.product.final_price)
        return total

    def get_total_text(self, cart: Cart):
        t = self.get_total(cart)
        return f"{Decimal(t):,.0f}៛"


# ==========================
# ✅ ORDER + PAYMENT PROOF
# ==========================

class OrderItemSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",          # product id
            "product_name",
            "product_image",
            "unit_price",
            "qty",
            "unit",
            "line_total",
        ]

    def get_product_image(self, obj):
        # safe: image url if exists
        try:
            if obj.product and obj.product.image:
                return obj.product.image.url
        except Exception:
            pass
        return None

    def get_unit(self, obj):
        try:
            return obj.product.unit
        except Exception:
            return None

    def get_line_total(self, obj):
        return Decimal(obj.unit_price) * Decimal(obj.qty)


class PaymentProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProof
        fields = ["id", "image", "note", "status", "created_at"]
        read_only_fields = ["status", "created_at"]


class OrderListSerializer(serializers.ModelSerializer):
    """✅ light serializer for order history list"""
    items_count = serializers.SerializerMethodField()
    total_text = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "order_code", "status",
            "total", "total_text",
            "created_at",
            "items_count",
        ]

    def get_items_count(self, obj: Order):
        return obj.items.count()

    def get_total_text(self, obj: Order):
        return f"{Decimal(obj.total):,.0f}៛"


class OrderDetailSerializer(serializers.ModelSerializer):
    """✅ detail serializer with items + proof"""
    items = OrderItemSerializer(many=True, read_only=True)
    payment_proof = PaymentProofSerializer(read_only=True)
    items_count = serializers.SerializerMethodField()
    total_text = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "order_code", "status",
            "phone", "address", "note",
            "total", "total_text", "created_at",
            "items_count",
            "items",
            "payment_proof",
        ]
        read_only_fields = [
            "order_code", "status", "total", "created_at",
            "items", "payment_proof",
        ]

    def get_items_count(self, obj: Order):
        return obj.items.count()

    def get_total_text(self, obj: Order):
        return f"{Decimal(obj.total):,.0f}៛"


class CheckoutSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    note = serializers.CharField(required=False, allow_blank=True, default="")
