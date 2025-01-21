from rest_framework import generics, viewsets
from product.models import Attribute, AttributeTerm, Category, ProductDetails
from .models import WorkOrder,Manufacture_Cost, ProductionLine_item, ProductionLine, Workstation, WorkOrderItem,QualityTest, ManufacturingRecord, WorkstationItems, ProductionLine_item
from .serializers import WorkOrderSerializer,ProductionLineitemSerializer,WorkOrderItemSerializer, WorkstationItemSerializer, Manufacture_CostSerializer, ProductionLineSerializer, WorkstationSerializer, QualityTestSerializer, ManufacturingRecordSerializer
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django.db.models import Q,Count
from rest_framework.response import Response


class WorkOrderFilter(django_filters.FilterSet):
    class Meta:
        model = WorkOrder
        fields = ['order_name','order_number','status']

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = WorkOrderFilter
    
    def create(self, request, *args, **kwargs):
        Variations = request.data["Variations"]
        order_name = request.data["order_name"]
        order_number = request.data["order_number"]
        Product = request.data["Product"]
        start_date = request.data["start_date"]
        end_date = request.data["end_date"]
        product_object = ProductDetails.objects.get(id=Product)
        neworder = WorkOrder.objects.create(order_name=order_name, order_number=order_number, 
                                            Product=product_object,start_date=start_date,end_date=end_date)
        for variation in Variations:
            # print(variation.quantity_needed)
            workorderitem = WorkOrderItem.objects.create(Workorder=neworder, quantity_needed=variation["quantity_needed"])
            if variation["Attributes"] != "" or variation["Attributes"] != None:
                # print(type(Attributes))
                Attributes_list = []
                if isinstance(variation["Attributes"], list):
                    Attributes_list = variation["Attributes"]
                elif isinstance(variation["Attributes"], str):
                    Attributes_list = Attributes.split(",")
                for attribute in Attributes_list:
                    workorderitem.Attributes.add(attribute)

            workorderitem.save()
        
        return Response({"status": "success"})

class WorkOrderItemFilter(django_filters.FilterSet):
    class Meta:
        model = WorkOrderItem
        fields = ['Workorder__id',]

class WorkOrderitemViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderItem.objects.all()
    serializer_class = WorkOrderItemSerializer
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = WorkOrderItemFilter


class Manufacture_CostFilter(django_filters.FilterSet):
    
    class Meta:
        model = Manufacture_Cost
        fields = ['ProductionLine__id','ProductionLine_item__id']


class Manufacture_CostViewSet(viewsets.ModelViewSet):
    queryset = Manufacture_Cost.objects.all()
    serializer_class = Manufacture_CostSerializer
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = Manufacture_CostFilter


class ProductionLineViewSet(viewsets.ModelViewSet):
    queryset = ProductionLine.objects.all()
    serializer_class = ProductionLineSerializer
    
class ProductionLineitemFilter(django_filters.FilterSet):

    # start = django_filters.IsoDateTimeFilter(
    #     field_name="start_date", lookup_expr='gte')
    # end = django_filters.IsoDateTimeFilter(
    #     field_name="end_date", lookup_expr='lte')
    # keyward = django_filters.CharFilter(
    #     method='filter_by_keyward', lookup_expr='icontains')
    
    class Meta:
        model = ProductionLine_item
        fields = ['ProductionLine__id','Workorder__id', 'status',
                #   'start', 'end',
                  ]
    # def filter_by_keyward(self, queryset, name, value):
    #     return queryset.filter(Q(invoice__invoice_number__contains=value) | Q(invoice__order_number__contains=value) | Q(invoice__contact__name__contains=value) | Q(product__barcode__contains=value) | Q(Details__contains=value))


class ProductionLineitemViewSet(viewsets.ModelViewSet):
    queryset = ProductionLine_item.objects.all()
    serializer_class = ProductionLineitemSerializer
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductionLineitemFilter


class ProductionLineitemPieViewSet(viewsets.ModelViewSet):
    # queryset = ProductionLine_item.objects.all().order_by('status')
    queryset = ProductionLine_item.objects.annotate(count=Count('status')).order_by('count')
    serializer_class = ProductionLineitemSerializer
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductionLineitemFilter


class WorkstationViewSet(viewsets.ModelViewSet):
    queryset = Workstation.objects.all()
    serializer_class = WorkstationSerializer

class WorkstationItemViewSet(viewsets.ModelViewSet):
    queryset = WorkstationItems.objects.all()
    serializer_class = WorkstationItemSerializer

class QualityTestViewSet(viewsets.ModelViewSet):
    queryset = QualityTest.objects.all()
    serializer_class = QualityTestSerializer


class ManufacturingRecordViewSet(viewsets.ModelViewSet):
    queryset = ManufacturingRecord.objects.all()
    serializer_class = ManufacturingRecordSerializer

