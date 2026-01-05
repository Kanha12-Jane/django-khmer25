import random
import string
from decimal import Decimal

from django.db import transaction
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Category, Product,
    Cart, CartItem,
    Order, OrderItem, PaymentProof
)
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer,
    CartSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    CheckoutSerializer,
    PaymentProofSerializer,
)

# ==========================
# CATEGORY
# ==========================
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["id", "name"]
    ordering = ["id"]

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True).order_by("id")


# ==========================
# PRODUCT
# ==========================
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related("category")

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug", "sku"]
    ordering_fields = ["id", "price", "created_at"]
    ordering = ["-id"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductSerializer

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("category")
        q = self.request.query_params

        if q.get("is_new") in ["true", "1", "yes"]:
            qs = qs.filter(is_new=True)

        if q.get("is_featured") in ["true", "1", "yes"]:
            qs = qs.filter(is_featured=True)

        if q.get("discounted") in ["true", "1", "yes"]:
            qs = qs.filter(discount_percent__gt=0)

        if q.get("category"):
            qs = qs.filter(category_id=q.get("category"))

        if q.get("parent_category"):
            qs = qs.filter(category__parent_id=q.get("parent_category"))

        return qs.order_by("-id")


# ==========================
# ✅ CART HELPERS
# ==========================
def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartViewSet(viewsets.ViewSet):
    """
    - GET  /api/cart/  => get my cart
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart = get_or_create_cart(request.user)
        return Response(CartSerializer(cart, context={"request": request}).data, status=200)


class CartItemViewSet(viewsets.ViewSet):
    """
    - POST   /api/cart/items/         body: {product_id, qty}
    - PATCH  /api/cart/items/<id>/    body: {qty}
    - DELETE /api/cart/items/<id>/
    """
    permission_classes = [IsAuthenticated]

    def create(self, request):
        cart = get_or_create_cart(request.user)

        product_id = request.data.get("product_id")
        qty = int(request.data.get("qty", 1))

        if not product_id:
            return Response({"detail": "product_id is required"}, status=400)
        if qty < 1:
            return Response({"detail": "qty must be >= 1"}, status=400)

        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            return Response({"detail": "Product not found"}, status=404)

        if product.stock < qty:
            return Response({"detail": "Not enough stock"}, status=400)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        item.qty = qty if created else (item.qty + qty)

        if product.stock < item.qty:
            return Response({"detail": "Not enough stock"}, status=400)

        item.save()
        cart.refresh_from_db()
        return Response(CartSerializer(cart, context={"request": request}).data, status=200)

    def partial_update(self, request, pk=None):
        cart = get_or_create_cart(request.user)

        item = CartItem.objects.filter(id=pk, cart=cart).select_related("product").first()
        if not item:
            return Response({"detail": "Item not found"}, status=404)

        qty = int(request.data.get("qty", item.qty))

        if qty < 1:
            item.delete()
        else:
            if item.product.stock < qty:
                return Response({"detail": "Not enough stock"}, status=400)
            item.qty = qty
            item.save()

        cart.refresh_from_db()
        return Response(CartSerializer(cart, context={"request": request}).data, status=200)

    def destroy(self, request, pk=None):
        cart = get_or_create_cart(request.user)

        item = CartItem.objects.filter(id=pk, cart=cart).first()
        if not item:
            return Response({"detail": "Item not found"}, status=404)

        item.delete()
        cart.refresh_from_db()
        return Response(CartSerializer(cart, context={"request": request}).data, status=200)


# ==========================
# ✅ ORDER HELPERS
# ==========================
def _gen_code(prefix="KH"):
    while True:
        s = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
        code = f"{prefix}{s}"
        if not Order.objects.filter(order_code=code).exists():
            return code


# ==========================
# ✅ ORDER API
# ==========================
class OrderViewSet(viewsets.ModelViewSet):
    """
    - GET  /api/orders/
    - GET  /api/orders/<id>/
    - POST /api/orders/checkout/
    - POST /api/orders/<id>/upload-proof/
    """
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["order_code", "phone"]
    ordering_fields = ["id", "created_at", "total", "status"]
    ordering = ["-id"]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items")
            .select_related("payment_proof")
            .order_by("-id")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        if self.action == "checkout":
            return CheckoutSerializer
        if self.action == "upload_proof":
            return PaymentProofSerializer
        return OrderDetailSerializer

    # GET /api/orders/
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        ser = OrderListSerializer(qs, many=True, context={"request": request})
        return Response(ser.data, status=200)

    # GET /api/orders/<id>/
    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        ser = OrderDetailSerializer(obj, context={"request": request})
        return Response(ser.data, status=200)

    # POST /api/orders/checkout/
    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        ser = CheckoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        phone = ser.validated_data["phone"].strip()
        address = ser.validated_data["address"].strip()
        note = (ser.validated_data.get("note") or "").strip()

        cart = get_or_create_cart(request.user)
        cart_items = cart.items.select_related("product").all()

        if not cart_items.exists():
            return Response({"detail": "Cart is empty"}, status=400)

        with transaction.atomic():
            # ✅ lock products to prevent stock race
            # re-fetch items with lock
            locked_items = (
                CartItem.objects
                .select_related("product")
                .select_for_update()
                .filter(cart=cart)
            )

            # stock check
            for it in locked_items:
                if it.product.stock < it.qty:
                    return Response(
                        {"detail": f"Not enough stock: {it.product.name}"},
                        status=400
                    )

            order = Order.objects.create(
                user=request.user,
                phone=phone,
                address=address,
                note=note,
                order_code=_gen_code(),
                status=Order.Status.PENDING_PAYMENT,
                total=Decimal("0"),
            )

            total = Decimal("0")
            for it in locked_items:
                p = it.product
                unit_price = Decimal(p.final_price)
                qty = int(it.qty)

                OrderItem.objects.create(
                    order=order,
                    product=p,
                    product_name=p.name,
                    unit_price=unit_price,
                    qty=qty,
                )
                total += unit_price * Decimal(qty)

                # ✅ reduce stock after creating order
                p.stock = max(0, p.stock - qty)
                p.save(update_fields=["stock"])

            order.total = total
            order.save(update_fields=["total"])

            # ✅ clear cart after checkout (recommended)
            locked_items.delete()

        # return detail serializer
        order.refresh_from_db()
        out = OrderDetailSerializer(order, context={"request": request}).data
        return Response(out, status=status.HTTP_201_CREATED)

    # POST /api/orders/<id>/upload-proof/
    @action(detail=True, methods=["post"], url_path="upload-proof")
    def upload_proof(self, request, pk=None):
        order = self.get_object()

        if hasattr(order, "payment_proof"):
            return Response({"detail": "proof already uploaded"}, status=400)

        image = request.FILES.get("image")
        note = request.data.get("note", "")

        if not image:
            return Response({"detail": "image is required"}, status=400)

        proof = PaymentProof.objects.create(
            order=order,
            image=image,
            note=note,
        )

        return Response(
            PaymentProofSerializer(proof, context={"request": request}).data,
            status=201
        )
