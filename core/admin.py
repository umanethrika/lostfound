from django.contrib import admin
from .models import CustomUser, Category, Item, MatchNotification
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# ----------------------------
# Custom User Admin
# ----------------------------
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ("name", "roll_number", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("name", "email", "roll_number")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "roll_number", "name", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "roll_number", "name", "password1", "password2", "is_staff", "is_active")}
        ),
    )

# ----------------------------
# Item Admin
# ----------------------------
class ItemAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "category", "location", "user", "created_at")
    list_filter = ("kind", "category", "location", "created_at")
    search_fields = ("title", "description", "contact_info")

# ----------------------------
# Category Admin
# ----------------------------
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

# ----------------------------
# Match Notification Admin
# ----------------------------
class MatchNotificationAdmin(admin.ModelAdmin):
    list_display = ("lost_item", "found_item", "notified", "created_at")
    list_filter = ("notified", "created_at")
    search_fields = ("lost_item__title", "found_item__title")

# ----------------------------
# Register all models
# ----------------------------
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(MatchNotification, MatchNotificationAdmin)
