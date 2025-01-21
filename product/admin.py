from django.contrib import admin
from product import models

class AttributeTable(admin.ModelAdmin):
    list_display = ['id','name','slug','context'] 
    search_fields = ( 'name','slug','context','pk')

class AttributeTermTable(admin.ModelAdmin):
    list_display = ['id','name','slug','Attribute','context','url'] 
    search_fields = ( 'name','slug','context','pk','Attribute__name')

class CategoryTable(admin.ModelAdmin):
    list_display = ['id','Category_parent','name','slug','online_visible'] 
    search_fields = ( 'name','slug','pk','Category_parent__name')

class ProductDetailsTable(admin.ModelAdmin):
    list_display = ['id','title','Category','quantity', 'min_price','max_price','is_active','is_sellable','is_live'] 
    search_fields = ( 'title','Category__name','pk')

class ProductLocationTable(admin.ModelAdmin):
    list_display = ['id','barcode','ProductDetails','Warehouse','Color','Size','quantity','purchase_price','selling_price','data'] 
    search_fields = ( 'barcode','ProductDetails__title','Warehouse__name','Color__name','Size__name','pk')

class ProductImageTable(admin.ModelAdmin):
    list_display = ['id','ProductDetails','ProductLocation','Color','photo','is_active'] 
    search_fields = ( 'ProductDetails__title','Color__name','pk')
    
class TransferTable(admin.ModelAdmin):
    list_display = ['id','tansfer_number','source','destance','status','issue_date'] 
    search_fields = ( 'tansfer_number','source__name','destance__name','status','issue_date','pk') 

class transfer_itemTable(admin.ModelAdmin):
    list_display = ['id','transfer','product','quantity','is_received','is_returned','issue_date'] 
    search_fields = ( 'transfer__tansfer_number','product__ProductDetails__title','issue_date','pk')

class WarehouseTable(admin.ModelAdmin):
    list_display = ['id','name','address','contact','cash','petty_cash','is_outlet','is_office'] 
    search_fields = ( 'name','address','contact','pk')
    
# Register your models here.
admin.site.register(models.Attribute,AttributeTable)
admin.site.register(models.AttributeTerm, AttributeTermTable)
admin.site.register(models.Category,CategoryTable)
# admin.site.register(models.Brand)
admin.site.register(models.ProductDetails, ProductDetailsTable)
# admin.site.register(models.BulkProduct)
# admin.site.register(models.BulkProductList)
admin.site.register(models.Warehouse,WarehouseTable)
admin.site.register(models.ProductLocation,ProductLocationTable)
admin.site.register(models.ProductImage,ProductImageTable)
admin.site.register(models.transfer,TransferTable)
admin.site.register(models.transfer_item,transfer_itemTable)
