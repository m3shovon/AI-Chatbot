from django.contrib import admin
from order import models
from product.models import ProductLocation

class invoicetabel(admin.ModelAdmin):
    list_display = ['id','invoice_number','order_number','contact','location','Sales_person','bill','payment','due','issue_date']
    
    search_fields = ( 'invoice_number','order_number','pk')

# class measurementtabel(admin.ModelAdmin):
#     list_display = ['id','invoice']
#     search_fields = ( 'invoice__invoice_number',)
    
    # search_fields = ('pk')
class invoice_itemTable(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'product', 'quantity']
    search_fields = [ 'invoice__invoice_number'] 

class invoice_item_copyTable(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'product', 'quantity', 'created_at', 'is_exchanged']
    search_fields = [ 'invoice__invoice_number'] 

class invoice_paymentTable(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'bill', 'discount', 'account', 'issue_date']
    search_fields = [ 'invoice__invoice_number']

# class servicesTable(admin.ModelAdmin):
#     list_display = ['invoice']
#     search_fields = ['invoice__invoice_number']

class couponTable(admin.ModelAdmin):
    list_display = ['name' ,'amount', 'status']
    search_fields = ['name']

# Register your models here.
admin.site.register(models.cupon, couponTable)
admin.site.register(models.refund)
admin.site.register(models.invoice, invoicetabel)
admin.site.register(models.invoice_payment, invoice_paymentTable)
admin.site.register(models.invoice_item, invoice_itemTable)
# admin.site.register(models.measurement,measurementtabel)
# admin.site.register(models.services, servicesTable)
# admin.site.register(models.services_costing)
# admin.site.register(models.purchase)
# admin.site.register(models.purchase_item)
admin.site.register(models.wordrobe)
admin.site.register(models.wordrobe_item)
# admin.site.register(models.DraftOrder)
# admin.site.register(models.DraftImage)
# admin.site.register(models.DraftCostSheet)
