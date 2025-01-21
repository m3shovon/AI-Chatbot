from rest_framework import serializers
from .models import WorkOrder, Manufacture_Cost, ProductionLine, WorkOrderItem, Workstation, QualityTest, ManufacturingRecord, WorkstationItems,ProductionLine_item
from product.models import ProductDetails
from product.serializers import CategorySingleProductSerilizer

class WorkOrderSerializer(serializers.ModelSerializer):
    # WorkOrderItem = WorkOrderItem.WorkOrderItemSerializer(read_only=True)
    class Meta:
        model = WorkOrder
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        workorderitems = WorkOrderItem.objects.filter(Workorder=instance.id)
        if instance.Product:
            product = ProductDetails.objects.filter(id=instance.Product.id)
            # print(product)
            for i in product:
                response["Product"] = CategorySingleProductSerilizer(i).data
        else:
            response["Product"] = ""
        varationarray = []
        for item in workorderitems:
            varationarray.append(
                    WorkOrderItemSerializer(item).data)
        response["Variations"] = varationarray
        # print(workorderitems)
        
        return response

class WorkOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderItem
        fields = '__all__'
        
    def to_representation(self, instance):
        response = super().to_representation(instance)
        res = ""
        count = 0
        if response["Attributes"]:
            for attribute in instance.Attributes.all():
                if attribute.name.isdigit():
                    response[attribute.Attribute.name.lower()] = int(
                        attribute.name)
                    response[attribute.Attribute.name] = int(attribute.id)
                else:
                    response[attribute.Attribute.name.lower()] = attribute.name
                    response[attribute.Attribute.name] = attribute.id
                if count == 0:
                    res += str(attribute.name)
                else:
                    res += " / " + str(attribute.name)
                count += 1
        response["description"] = instance.Workorder.order_name + " " + res
        
        return response
        
class Manufacture_CostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacture_Cost
        fields = '__all__'

class ProductionLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionLine
        fields = '__all__'
    
   

class ProductionLineitemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionLine_item
        fields = '__all__'
        
    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.Workorder:
            response["workorder_name"] = instance.Workorder.order_name
        if instance.ProductionLine:
            response["line_name"] = instance.ProductionLine.line_name
        if instance.WorkOrderItem:
            workorderitemobj = WorkOrderItem.objects.get(id=instance.WorkOrderItem.id)
            response["workorder_item"] = WorkOrderItemSerializer(workorderitemobj).data
            
        
        return response
    
class WorkstationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workstation
        fields = '__all__'
        
class WorkstationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkstationItems
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.Workstation:
            response["workstation_name"] = instance.Workstation.workstation_name
        
        line_items_array = []
        if instance.ProductionLine:
            response["line_name"] = instance.ProductionLine.line_name
            
            line_items = ProductionLine_item.objects.filter(
                ProductionLine=instance.ProductionLine)
            for i in line_items:
                line_items_array.append(
                    ProductionLineitemSerializer(i).data)
        response["line_items"] = line_items_array
            
        
        return response

    
    

class QualityTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityTest
        fields = '__all__'

class ManufacturingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManufacturingRecord
        fields = '__all__'
