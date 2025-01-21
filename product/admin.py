from django.contrib import admin
from product import models

# class AttributeTermInline(admin.TabularInline):
#     model = models.ProductLocation.Attributes.through  # ManyToMany intermediary table
#     extra = 1  # Number of extra forms displayed


class AttributeTermTable(admin.ModelAdmin):
    list_display = ['id','Attribute','name']
    
    search_fields = ( 'Attribute__name','name','pk')

class ProductDetailsTable(admin.ModelAdmin):
    list_display = ['id','title','product_code','discount','Sub_Category','quantity']
    
    search_fields = ( 'title','product_code','pk')

class ProductLocationTable(admin.ModelAdmin):
    # inlines = [AttributeTermInline]
    list_display = ['id','get_attributes','ProductDetails', 'Warehouse','purchase_price','selling_price', 'quantity', 'barcode']
    filter_horizontal = ('Attributes',)
    
    search_fields = ( 'ProductDetails__product_code','ProductDetails__title','barcode','pk') 

    def get_attributes(self, obj):
        return ", ".join([attr.name for attr in obj.Attributes.all()])
    
    get_attributes.short_description = 'Attributes'   

class BarcodePrintListTable(admin.ModelAdmin):
    list_display = ['id','challan_number','list_quantity', 'issue_date']
    
class ProductLocationEntryTable(admin.ModelAdmin):
    list_display = ['id','ProductLocation','quantity','remarks','created', ]  
    search_fields = ( 'ProductLocation__ProductDetails__title','quantity')

class TransferTable(admin.ModelAdmin):
    list_display = ('id', 'tansfer_number', 'source', 'destance', 'status', 'issue_date')

    def get_transfer_number(self, obj):
        return obj.transfer.tansfer_number if obj.transfer else None

    get_transfer_number.short_description = 'Transfer Number'

class TransferItemTable(admin.ModelAdmin):
    list_display = ('id', 'get_transfer_number', 'product', 'quantity', 'is_received', 'is_returned','issue_date')
    search_fields = ( 'transfer__tansfer_number','product__ProductDetails__product_code','product__ProductDetails__title','product__barcode','pk')

    def get_transfer_number(self, obj):
        return obj.transfer.tansfer_number if obj.transfer else None

    get_transfer_number.short_description = 'Transfer Number'

# Register your models here.
admin.site.register(models.Attribute)
admin.site.register(models.AttributeTerm, AttributeTermTable)
admin.site.register(models.Category)
admin.site.register(models.ProductDetails, ProductDetailsTable)
admin.site.register(models.Warehouse)
admin.site.register(models.ProductLocation,ProductLocationTable)
admin.site.register(models.ProductLocationEntry, ProductLocationEntryTable)
admin.site.register(models.ProductImage)
admin.site.register(models.transfer,TransferTable)
admin.site.register(models.transfer_item,TransferItemTable)
admin.site.register(models.BarcodePrintList,BarcodePrintListTable)


