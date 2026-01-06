from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from .models import Profile

User = get_user_model()


# ==========================
# PROFILE INLINE (safe)
# ==========================
class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    can_delete = False
    show_change_link = True
    exclude = ()  # show all fields safely


# ==========================
# USER ADMIN (Unfold + Avatar in row)
# ==========================
from django.utils.html import format_html

class CustomUserAdmin(ModelAdmin, DjangoUserAdmin):
    # ...
    list_display = (
        "id",
        "avatar_thumb",
        "username",
        "email",
        "is_staff",
        "is_active",
        "date_joined",
    )

    def avatar_thumb(self, obj):
        profile = getattr(obj, "profile", None)
        if not profile:
            return "—"

        for field in ("avatar", "image", "photo", "profile_image"):
            f = getattr(profile, field, None)
            if f and hasattr(f, "url"):
                return format_html(
                    '<img src="{}" '
                    'style="width:56px;height:56px;'
                    'border-radius:50%;'
                    'object-fit:cover;'
                    'border:2px solid #e5e7eb;'
                    'box-shadow:0 1px 4px rgba(0,0,0,.08);" />',
                    f.url,
                )
        return "—"

    avatar_thumb.short_description = "Profile"



# ==========================
# REGISTER (only once)
# ==========================
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
