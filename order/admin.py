from django.contrib import admin
from order import models
from product.models import ProductLocation

class invoicetabel(admin.ModelAdmin):
    list_display = ['id','invoice_number','order_number','contact','location','Sales_person','bill','payment','due','issue_date'] 
    search_fields = ( 'invoice_number','order_number','pk')

class measurementtabel(admin.ModelAdmin):
    list_display = ['id','invoice']
    search_fields = ( 'invoice__invoice_number',)
    
    # search_fields = ('pk')
class invoice_itemTable(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'product', 'quantity']
    search_fields = [ 'invoice__invoice_number'] 

class servicesTable(admin.ModelAdmin):
    list_display = ['invoice']
    search_fields = ['invoice__invoice_number']

class couponTable(admin.ModelAdmin):
    list_display = ['name' ,'amount', 'status']
    search_fields = ['name']

class ipnTable(admin.ModelAdmin):
    list_display = ['tran_id' ,'card_type','amount', 'status']
    # search_fields = ['name']
    
class Wordrobe_itemTable(admin.ModelAdmin):
    list_display = ['id','wordrobe','Details','quantity','price','is_returned','issue_date','created_at'] 
    search_fields = ( 'wordrobe__wordrobe_number','Details','created_at','issue_date','pk')

class WordrobeTable(admin.ModelAdmin):
    list_display = ['id','wordrobe_number','contact','location','company_name','delivery_date','is_returned','status','created_at'] 
    search_fields = ( 'wordrobe_number','contact__name','contact__email','contact__phone','location__name','created_at','issue_date','pk')
    
# Register your models here.
admin.site.register(models.cupon, couponTable)
admin.site.register(models.Refund)
admin.site.register(models.Refund_item)
admin.site.register(models.online_order)
admin.site.register(models.invoice, invoicetabel)
admin.site.register(models.invoice_item, invoice_itemTable)
admin.site.register(models.measurement,measurementtabel)
admin.site.register(models.services, servicesTable)
admin.site.register(models.services_costing)
admin.site.register(models.purchase)
admin.site.register(models.purchase_item)
admin.site.register(models.wordrobe, WordrobeTable)
admin.site.register(models.wordrobe_item,Wordrobe_itemTable)
admin.site.register(models.IPN, ipnTable)
