from django.contrib import admin
from manufacturing.models import WorkOrder,WorkOrderItem, Manufacture_Cost,WorkstationItems, ProductionLine, ProductionLine_item,  Workstation, WorkstationStatus, QualityTestStatus, QualityTest, ManufacturingRecord
# Register your models here.


# class WorkOrderTable(admin.ModelAdmin):
#     list_display = ['id', 'draft_cost_sheet', 'order_name', 'order_number',
#                     'start_date', 'end_date', 'quantity_needed', 'total_cost']
#     search_fields = ('order_name', 'order_number', 'id')


# class Manufacture_CostTable(admin.ModelAdmin):
#     list_display = ['Workstation', 'material_name', 'unit_name',
#                     'quantity_in_stock', 'cost_per_unit', 'total_cost']
#     search_fields = ('Workstation', 'material_name')


# class ProductionLineTable(admin.ModelAdmin):
#     list_display = ['order', 'line_name', 'location']
#     search_fields = ('order', 'line_name', 'location')


# class WorkstationTable(admin.ModelAdmin):
#     list_display = ['id', 'workstation_name', 'line', 'order']
#     search_fields = ('id', 'workstation_name', 'line', 'order')


# class QualityTestTable(admin.ModelAdmin):
#     list_display = ['test_type', 'test_date', 'pass_fail_status']
#     search_fields = ('test_type', 'test_date', 'pass_fail_status')


# admin.site.register(WorkOrder)
# admin.site.register(WorkOrderItem)

# admin.site.register(Manufacture_Cost)
# admin.site.register(ProductionLine)
# admin.site.register(ProductionLine_item)

# admin.site.register(Workstation)
# admin.site.register(WorkstationItems)
# admin.site.register(QualityTestStatus)
# admin.site.register(QualityTest)
# admin.site.register(ManufacturingRecord)
