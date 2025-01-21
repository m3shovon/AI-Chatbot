from django.contrib import admin
from contact import models

class contacttabel(admin.ModelAdmin):
    list_display = ['id','name','email','phone','Type','role','account_balance']
    
    search_fields = ( 'email','name','pk','phone','Type','role__name',)

class UserProfileTable(admin.ModelAdmin):
    list_display = ['name','email', 'user_role','branch']    
    search_fields = ['name', 'email']
    
class EmployeeProfileTable(admin.ModelAdmin):
    list_display = ['employee','phone', 'address',]
    search_fields = ['employee__name']

class Role_permissionTable(admin.ModelAdmin):
    list_display = ['id','user_role','module', 'sub_module','is_read','is_location']
    search_fields = ['pk','module__name','sub_module__name']

class UserRoleTable(admin.ModelAdmin):
    list_display = ['id','name','department',]
    search_fields = ['pk','name','department__name']

# Register your models here.
admin.site.register(models.Department)
admin.site.register(models.userRole,UserRoleTable)
admin.site.register(models.UserProfile,UserProfileTable)
admin.site.register(models.EmployeeProfile,EmployeeProfileTable)
admin.site.register(models.EmployeeDocument)
admin.site.register(models.contact,contacttabel)
admin.site.register(models.ContactType)
admin.site.register(models.role_permission, Role_permissionTable)
