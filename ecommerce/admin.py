from django.contrib import admin
from ecommerce import models
from product.models import Brand
# Register your models here.

class BrandBasedAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Example: Hide this module for a specific Brand
        restricted_brand_name = "ELOR"
        if Brand.objects.filter(name=restricted_brand_name).exists():
            return False  # Hide module
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        restricted_brand_name = "ELOR"
        if Brand.objects.filter(name=restricted_brand_name).exists():
            return False  # Hide view
        return super().has_view_permission(request)

class CheckAdmin(BrandBasedAdmin):
    pass


admin.site.register(models.page, CheckAdmin)
admin.site.register(models.image, CheckAdmin)
admin.site.register(models.feature, CheckAdmin)
admin.site.register(models.feature_item, CheckAdmin)