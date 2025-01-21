from django.contrib import admin
from software_settings import models

# Register your models here.
admin.site.register(models.business_settings)
admin.site.register(models.module)
admin.site.register(models.sub_module)
