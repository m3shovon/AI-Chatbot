from django.contrib import admin
from accounting import models
from product.models import Brand


class BrandBasedAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Example: Hide this module for a specific Brand
        restricted_brand_name = "ELORA"
        if Brand.objects.filter(name=restricted_brand_name).exists():
            return False  # Hide module
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        restricted_brand_name = "ELORA"
        if Brand.objects.filter(name=restricted_brand_name).exists():
            return False  # Hide view
        return super().has_view_permission(request)

class CheckAdmin(BrandBasedAdmin):
    pass

class chartofaccountstabel(BrandBasedAdmin):
    list_display = ['id','account_name','account_code','group','sub_group','Financial_statement','normally_Debit','amount','status']
    
    search_fields = ( 'account_name','account_code','pk','group__account_name','sub_group__account_name','Financial_statement')
    
class accounttabel(admin.ModelAdmin):
    list_display = ['id','accountparent','name','account_no','type','cash','txnCharge','is_active',]
    
    search_fields = ( 'accountparent__name','name','pk','account_no','type',)

class journaltabel(BrandBasedAdmin):
    list_display = ['id','chartofaccount','details','increase','amount','outlet','created']
    
    search_fields = ( 'details','chartofaccount__account_name','pk',)

class vouchertabel(BrandBasedAdmin):
    list_display = ['id','voucher_number','employee','amount','location','referance','created']
    
    search_fields = ( 'voucher_number','pk',)    

class paymentvoucheritemtabel(BrandBasedAdmin):
    list_display = ['id','paymentvoucher','chartofaccount','narration','increase','amount','created']
    
    search_fields = ( 'chartofaccount__account_name','pk','narration','paymentvoucher__voucher_number') 
    

class receivevoucheritemtabel(BrandBasedAdmin):
    list_display = ['id','receivevoucher','chartofaccount','narration','increase','amount','created']
    
    search_fields = ( 'chartofaccount__account_name','pk','narration','receivevoucher__voucher_number')


class journalvoucheritemtabel(BrandBasedAdmin):
    list_display = ['id','journalvoucher','chartofaccount','narration','increase','amount','created']
    
    search_fields = ( 'chartofaccount__account_name','pk','narration','journalvoucher__voucher_number')


class pettycash_transfertabel(BrandBasedAdmin):
    list_display = ['id','location','account','cash_amount','pett_cash_amount','collect_cash','add_cash','created','modified']
    
    search_fields = ( 'location__name','pk','cash_amount','pett_cash_amount','created')

class pettycashtabel(BrandBasedAdmin):
    list_display = ['id','location','employee','narration','amount','increase','created',]
    
    search_fields = ( 'location__name','pk','amount','narration','created')
    
from django.contrib import admin
from accounting import models

# Register your models here.
admin.site.register(models.account,accounttabel)
admin.site.register(models.accountStatusByDate, CheckAdmin)
admin.site.register(models.accountStatus, CheckAdmin)
admin.site.register(models.chartofaccount,chartofaccountstabel)
admin.site.register(models.journal, journaltabel)
admin.site.register(models.paymentvoucher, vouchertabel)
admin.site.register(models.paymentvoucheritems, paymentvoucheritemtabel)
admin.site.register(models.receivevoucher,vouchertabel)
admin.site.register(models.receivevoucheritems,receivevoucheritemtabel)
admin.site.register(models.journalvoucher,vouchertabel)
admin.site.register(models.journalvoucheritems,journalvoucheritemtabel)
admin.site.register(models.contravoucher,vouchertabel)
admin.site.register(models.pettycash, pettycashtabel)
admin.site.register(models.pettycash_transfer, pettycash_transfertabel)
