from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone


# ==========================
# CATEGORY
# ==========================
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category_khmer25/", blank=True, null=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="subcategories"
    )

    def __str__(self):
        return self.name


# ==========================
# PRODUCT
# ==========================
class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    image = models.ImageField(upload_to="products_khmer25/", blank=True, null=True)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.PositiveSmallIntegerField(default=0)

    stock = models.PositiveIntegerField(default=0)
    is_in_stock = models.BooleanField(default=True)

    is_new = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def final_price(self) -> Decimal:
        """
        return discounted price as Decimal
        """
        price = Decimal(self.price)
        if self.discount_percent and self.discount_percent > 0:
            disc = (price * Decimal(self.discount_percent)) / Decimal("100")
            return price - disc
        return price

    def save(self, *args, **kwargs):
        self.is_in_stock = self.stock > 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ==========================
# CART (Djoser user)
# ==========================
class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({getattr(self.user, 'username', self.user_id)})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="cart_items")
    qty = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="uniq_cart_product")
        ]

    def __str__(self):
        return f"{self.product.name} x{self.qty}"


# ==========================
# ORDER + PAYMENT PROOF
# ==========================
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "PENDING_PAYMENT", "Pending Payment"
        PAID = "PAID", "Paid"
        PROCESSING = "PROCESSING", "Processing"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        REJECTED = "REJECTED", "Rejected"
        CANCELED = "CANCELED", "Canceled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    # shipping
    phone = models.CharField(max_length=20)
    address = models.TextField()
    note = models.TextField(blank=True, default="")

    # total in KHR (keep Decimal like your cart total)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))

    # easy for admin find
    order_code = models.CharField(max_length=30, unique=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.order_code} - {self.user_id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")

    # snapshot for history
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # final_price at checkout time
    qty = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_name} x{self.qty}"


class PaymentProof(models.Model):
    class VerifyStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment_proof")
    image = models.ImageField(upload_to="payment_proofs_khmer25/")
    note = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=20, choices=VerifyStatus.choices, default=VerifyStatus.PENDING)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Proof {self.order.order_code} - {self.status}"
