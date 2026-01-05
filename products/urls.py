from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    CartViewSet,
    CartItemViewSet,
    OrderViewSet,   # ✅ add
)

router = DefaultRouter()

router.register("categories", CategoryViewSet, basename="categories")
router.register("products", ProductViewSet, basename="products")

router.register("cart", CartViewSet, basename="cart")
router.register("cart/items", CartItemViewSet, basename="cart-items")

router.register("orders", OrderViewSet, basename="orders")  # ✅ add

urlpatterns = router.urls
