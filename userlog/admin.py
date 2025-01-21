from django.contrib import admin
from userlog import models

# Register your models here.

class UserlogFilter(admin.ModelAdmin):

    list_display = ['object_id','user','action' ,'content_type', 'timestamp']
    search_fields = ('user__email', 'timestamp', 'object_id', 'content_type__model', 'action')

admin.site.register(models.UserLog,UserlogFilter)

