from operator import contains
from django.shortcuts import render
from django.db.models import Count, Sum
from rest_framework import viewsets
from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django.db.models import Q
from django.conf import settings

from order import serializers, models
from django.contrib.admin.models import LogEntry
from rest_framework.pagination import PageNumberPagination
from decimal import Decimal
import json
import datetime
import pytz


from product import models as productModel
from order import models as orderModel
from contact import models as contactModel
from accounting import models as accountingModel



# Create your views here.


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100000000


class CuponFilter(django_filters.FilterSet):
    class Meta:
        model = models.cupon
        fields = ['name']


class CuponViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.Cuponserializers
    queryset = models.cupon.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = CuponFilter


class IPNFilter(django_filters.FilterSet):
    class Meta:
        model = models.IPN
        fields = ['tran_id']
        
class IPNViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.IPNserializers
    queryset = models.IPN.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = IPNFilter

class InvoiceItemFilter(django_filters.FilterSet):
    
    start = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='lte')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.invoice_item
        fields = ['invoice__id','start', 'end', 'invoice__location__id', 'keyward']
    
    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice__invoice_number__contains=value) | Q(invoice__order_number__contains=value) | Q(invoice__contact__name__contains=value) | Q(product__barcode__contains=value) | Q(Details__contains=value) )



class InvoiceItemViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.InvoiceItemserializers
    queryset = models.invoice_item.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoiceItemFilter
    # permission_classes = (permissions.UpdateOwnProfile,)

    # def create(self, request):
    #     service = models.invoice.objects.get(id=invoice_item__invoice__id)
    #     service.save()
    #     return Response(serializer.data)
    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.InvoiceItemReadserializers
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.InvoiceItemReadserializers
        return super().retrieve(request, *args, **kwargs)


class SoldProductsViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.InvoiceItemserializers
    queryset = models.invoice_item.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoiceItemFilter
    
    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.InvoiceItemSOldReadserializers
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.InvoiceItemSOldReadserializers
        return super().retrieve(request, *args, **kwargs)


class MeasurementViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.Measurementserializers
    queryset = models.measurement.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('id', 'invoice__id', 'contact__id','is_basic')
    
    # def create(self, request, *args, **kwargs):
    #     is_basic = request.data.get("is_basic")
    #     contact = request.data.get("contact")
    #     invoice = request.data.get("invoice")
    #     product = request.data.get("invoice")
        
    #     if is_basic == "" or is_basic == None or is_basic == "None":
    #         invoice_object = models.invoice.objects.get(id=invoice)
    #         new_measurement, created = models.measurement.objects.get_or_create(
    #             invoice=invoice_object)
    #         serialized = serializers.Measurementserializers(
    #             instance=new_measurement, data=request.data)
    #         serialized.is_valid(raise_exception=True)
    #         serialized.save()
    #         return Response(serialized.data, status=status.HTTP_201_CREATED)
    #     else:
    #         contact_object = models.contact.objects.get(id=contact)
    #         new_measurement, created = models.measurement.objects.get_or_create(
    #             contact=contact_object, is_basic=is_basic)
    #         serialized = serializers.Measurementserializers(
    #             instance=new_measurement, data=request.data)
    #         serialized.is_valid(raise_exception=True)
    #         return Response(serialized.data, status=status.HTTP_201_CREATED)


class DeliveryTypeViewSet(viewsets.ModelViewSet):
    """Handel creating and updating users"""
    serializer_class = serializers.DeliveryypeSerializer
    queryset = models.DeliveryType.objects.all()
    authentication_classes = (TokenAuthentication,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('Type',)


class InvoiceFilter(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='lte')
    deliverystart = django_filters.IsoDateTimeFilter(
        field_name="delivery_date", lookup_expr='gte')
    deliveryend = django_filters.IsoDateTimeFilter(
        field_name="delivery_date", lookup_expr='lte')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    month = django_filters.NumberFilter(
        method='filter_by_month', lookup_expr='month')
    year = django_filters.NumberFilter(
        method='filter_by_year', lookup_expr='year')
    has_due = django_filters.BooleanFilter(
        method='filter_by_due', lookup_expr='icontains')
    refundable = django_filters.BooleanFilter(
        method='filter_by_refundable', lookup_expr='icontains')
    contains_item = django_filters.BooleanFilter(method='filter_by_item')

    class Meta:
        model = models.invoice
        fields = ['start', 'end',
                  'invoice_number', 'delivery_date', 'Payment_method','deliverystart','deliveryend',
                  'status', 'contact', 'location', 'account', 'keyward',
                  'month', 'year', 'contains_item', 'contact__ecommerce_id','has_due', 'Sales_person','refundable','is_refunded','is_mute','id']

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice_number__contains=value) | Q(order_number__contains=value) | Q(status__icontains=value) | Q(contact__name__icontains=value) | Q(contact__phone__icontains=value) | Q(contact__ecommerce_id__icontains=value) | Q(remarks__icontains=value))

    def filter_by_month(self, queryset, name, value):
        return queryset.filter(
            Q(issue_date__month=value) | Q(issue_date__month=value)
        )
        
    def filter_by_due(self, queryset, name, value):
        if value:
            return queryset.filter(due__gt=0)
    
    def filter_by_refundable(self, queryset, name, value):
        if value:
            return queryset.filter(advance_payment__gt=0)

    def filter_by_year(self, queryset, name, value):
        return queryset.filter(
            Q(issue_date__year=value) | Q(issue_date__year=value)
        )

    def filter_by_item(self, queryset, name, value):
        if value:
            return queryset.filter(invoice_item__isnull=False).distinct()
        else:
            return queryset.filter(invoice_item__isnull=True).distinct()


class InvoiceVATFilter(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter(
        field_name="Vat_issued_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="Vat_issued_date", lookup_expr='lte')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    month = django_filters.NumberFilter(
        method='filter_by_month', lookup_expr='month')
    year = django_filters.NumberFilter(
        method='filter_by_year', lookup_expr='year')
    contains_item = django_filters.BooleanFilter(method='filter_by_item')

    class Meta:
        model = models.invoice
        fields = ['start', 'end',
                  'invoice_number', 'delivery_date', 'Payment_method',
                  'status', 'contact', 'location', 'account', 'keyward',
                  'month', 'year', 'contains_item', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice_number__contains=value) | Q(order_number__contains=value) | Q(status__contains=value))

    def filter_by_month(self, queryset, name, value):
        return queryset.filter(
            Q(Vat_issued_date__month=value) | Q(Vat_issued_date__month=value)
        )

    def filter_by_year(self, queryset, name, value):
        return queryset.filter(
            Q(Vat_issued_date__year=value) | Q(Vat_issued_date__year=value)
        )

    def filter_by_item(self, queryset, name, value):
        if value:
            return queryset.filter(invoice_item__isnull=False).distinct()
        else:
            return queryset.filter(invoice_item__isnull=True).distinct()


class InvoiceFilterByDeliveryDate(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter(
        field_name="delivery_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="delivery_date", lookup_expr='lte')

    class Meta:
        model = models.invoice
        fields = ['start', 'end',
                  'invoice_number', 'delivery_date', 'Payment_method', 'status', 'contact', 'location', 'account', 'DeliveryType']


class ServiceFilter(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='lte')
    deliverystart = django_filters.IsoDateTimeFilter(
        field_name="invoice__delivery_date", lookup_expr='gte')
    deliveryend = django_filters.IsoDateTimeFilter(
        field_name="invoice__delivery_date", lookup_expr='lte')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.services
        fields = ['start', 'end',  'invoice__id', 'keyward', 'employe__id', 'realter','status','deliverystart','deliveryend']

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice__invoice_number__contains=value) | Q(details__contains=value) | Q(invoice__contact__name__contains=value) | Q(invoice__order_number__contains=value) | Q(invoice__remarks__contains=value))


class InvoiceViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Invoiceserializers
    queryset = models.invoice.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoiceFilter
    # permission_classes = (permissions.UpdateOwnProfile,)

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.InvoiceReadserializers
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.InvoiceReadserializers
        return super().retrieve(request, *args, **kwargs)


class InvoiceViewSetP(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Invoiceserializers
    queryset = models.invoice.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoiceFilter
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.InvoiceReadserializers
        response = super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())

        response.data['total_discount'] = queryset.aggregate(Sum('discount'))[
            'discount__sum']
        response.data['total_sales'] = queryset.aggregate(Sum('bill'))[
            'bill__sum']
        response.data['total_payment'] = queryset.aggregate(Sum('payment'))[
            'payment__sum']
        response.data['total_due'] = queryset.aggregate(Sum('due'))['due__sum']
        response.data['total_tax'] = queryset.aggregate(Sum('tax'))['tax__sum']
        response.data['total_costing'] = queryset.aggregate(Sum('costing'))[
            'costing__sum']

        response.data['current_page_discount'] = sum(
            [Decimal(data.get('discount', 0)) for data in response.data['results']])
        response.data['current_page_sales'] = sum(
            [Decimal(data.get('bill', 0)) for data in response.data['results']])
        response.data['current_page_payment'] = sum(
            [Decimal(data.get('payment', 0)) for data in response.data['results']])
        response.data['current_page_due'] = sum(
            [Decimal(data.get('due', 0)) for data in response.data['results']])
        response.data['current_page_tax'] = sum(
            [Decimal(data.get('tax', 0)) for data in response.data['results']])
        response.data['current_page_costing'] = sum(
            [Decimal(data.get('costing', 0)) for data in response.data['results']])

        return response

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.InvoiceReadserializers
        return super().retrieve(request, *args, **kwargs)

class AllOnlineOrderFilter(django_filters.FilterSet):
    class Meta:
        model = models.online_order
        fields = ['invoice_number',]

class AllOnlineOrderViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.AllOnlineOrderserializers
    queryset = models.online_order.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = AllOnlineOrderFilter
    
    def create(self, request, *args, **kwargs):
        selectedDeliveryMethod = request.data["selectedDeliveryMethod"] 
        shipping_method = request.data["shipping_method"]
        bill = request.data["bill"]
        due = request.data["due"]
        delivery_charge = request.data["delivery_charge"] 
        tax = request.data["tax"] 
        discount = request.data["discount"] 
        discountlimit = request.data["discountlimit"]
        cupon = request.data["cupon"]
        quantity = request.data["quantity"] 
        Type = request.data["Type"] 
        ecommerce_id = request.data["ecommerce_id"]
        data = request.data["data"] 
        name = request.data["name"]
        contact = request.data["contact"] 
        location = request.data["location"]
        account = request.data["account"]
        delivery_date = request.data["delivery_date"] 
        invoice_number = request.data["invoice_number"] 
        products = request.data["products"]
        costing = 0
        
        address1 = ""
        if request.data.get("address1"):
            address1 = request.data["address1"]
            shipping_address = str(address1)
        address2 = ""
        if request.data.get("address2"):
            address2 = request.data["address2"]
            shipping_address += " " + str(address2)
        thana = ""
        if request.data.get("thana"):
            thana = request.data["thana"]
            shipping_address += ", " + str(thana)
        district = ""
        if request.data.get("district"):
            district = request.data["district"]
            shipping_address += ", " + str(district)
        country = ""
        if request.data.get("country"):
            country = request.data["country"]
            shipping_address += ", " + str(country)
        postalCode =""
        if request.data.get("postalCode"):
            postalCode = request.data["postalCode"]
            shipping_address += " " + str(postalCode)
        
        s_phone = ""
        if request.data.get("s_phone"):
            s_phone = request.data["s_phone"] 
        data = {
            "selectedDeliveryMethod": selectedDeliveryMethod,
            "shipping_method": shipping_method,
            "bill": bill,
            "due": due,
            "delivery_charge": delivery_charge,
            "tax": tax,
            "discount": discount,
            "discountlimit": discountlimit,
            "cupon": cupon,
            "quantity": quantity,
            "Type": Type,
            "ecommerce_id": ecommerce_id,
            "data": data,
            "name": name,
            "contact": contact,
            "location": location,
            "account": account,
            "delivery_date": delivery_date,
            "invoice_number": invoice_number,
            "products": products,
            "address1": address1,
            "address2": address2,
            "thana": thana,
            "district": district,
            "country": country,
            "postalCode": postalCode,
            "shipping_address": shipping_address,
            "s_phone": s_phone,
        }
        onlineorder = models.online_order.objects.create(data=data, confirm=False, invoice_number=invoice_number)
        return Response({"status": "success", "id": onlineorder.id})


class InvoiceClientViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.ClientInvoiceSerializers
    queryset = models.invoice.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoiceFilter

    def get(self, request, pk):
        "return data"
        queryset = models.invoice.objects.filter(id=pk)
        result = serializers.ClientInvoiceSerializers(
            queryset, context={'request': self.request, 'view': self})
        return Response(result.data)


class InvoiceVatViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.InvoiceVatSerializers
    queryset = models.invoice.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoiceVATFilter
    # pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())

        # response.data['total_quantity'] = queryset.aggregate(Sum('quantity'))[
        #     'quantity__sum']
        # response.data['total_bill'] = queryset.aggregate(Sum('bill'))[
        #     'bill__sum']
        # # response.data['total_due'] = queryset.aggregate(Sum('due'))['due__sum']
        # response.data['total_discount'] = queryset.aggregate(Sum('discount'))[
        #     'discount__sum']
        # response.data['total_tax'] = queryset.aggregate(Sum('tax'))['tax__sum']
        # response.data['total_costing'] = queryset.aggregate(Sum('costing'))[
        #     'costing__sum']
        # response.data['total_profit'] = queryset.aggregate(Sum('profit'))[
        #     'profit__sum']
        # response.data['total_payment'] = queryset.aggregate(Sum('payment'))[
        #     'payment__sum']
        # response.data['total_advance_payment'] = queryset.aggregate(
        #     Sum('advance_payment'))['advance_payment__sum']

        return response

    def create(self, request):
        response = {'message': 'Create function is not offered in this path.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        response = {'message': 'Update function is not offered in this path.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None):
        response = {'message': 'Update function is not offered in this path.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        response = {'message': 'Delete function is not offered in this path.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

class SalesPersonViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.SalesPersonSerializers
    queryset = models.invoice.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoiceFilter


class InvoiceExcelViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.InvoiceVatSerializers
    queryset = models.invoice.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoiceFilter

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())
        return response

class OurObject:
    def __init__(self, /, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    
class OnlineOrderViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Invoiceserializers
    queryset = models.invoice.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    # filter_backends = [DjangoFilterBackend]
    # filter_class = InvoiceFilter
    
    def create(self, request, *args, **kwargs):
        selectedDeliveryMethod = request.data["selectedDeliveryMethod"] 
        shipping_method = request.data["shipping_method"]
        bill = request.data["bill"]
        due = request.data["due"]
        delivery_charge = request.data["delivery_charge"] 
        tax = request.data["tax"] 
        discount = request.data["discount"] 
        discountlimit = request.data["discountlimit"]
        cupon = request.data["cupon"]
        quantity = request.data["quantity"] 
        Type = request.data["Type"] 
        ecommerce_id = request.data["ecommerce_id"]
        data = request.data["data"] 
        name = request.data["name"]
        contact = request.data["contact"] 
        location = request.data["location"]
        account = request.data["account"]
        delivery_date = request.data["delivery_date"] 
        invoice_number = request.data["invoice_number"] 
        products = request.data["products"]
        costing = 0
        
        address1 = ""
        if request.data.get("address1"):
            address1 = request.data["address1"]
            shipping_address = str(address1)
        address2 = ""
        if request.data.get("address2"):
            address2 = request.data["address2"]
            shipping_address += " " + str(address2)
        thana = ""
        if request.data.get("thana"):
            thana = request.data["thana"]
            shipping_address += ", " + str(thana)
        district = ""
        if request.data.get("district"):
            district = request.data["district"]
            shipping_address += ", " + str(district)
        country = ""
        if request.data.get("country"):
            country = request.data["country"]
            shipping_address += ", " + str(country)
        postalCode =""
        if request.data.get("postalCode"):
            postalCode = request.data["postalCode"]
            shipping_address += " " + str(postalCode)
        
        s_phone = ""
        if request.data.get("s_phone"):
            s_phone = request.data["s_phone"] 
        
        
        redFlag = 0
        cuonFlag = 0
        message = "Successfully updated"
        for product in request.data["products"]:
            item = productModel.ProductLocation.objects.get(id=product["id"])
            costing += float(product["quantity"]) * float(item.purchase_price)
            if product["quantity"] > item.quantity:
               redFlag = 1
               message = str(item.ProductDetails.title) + " is not available"
        
        current_datetime = str(datetime.datetime.now()) + "+00:00"
        dt = datetime.datetime.fromisoformat(current_datetime)
        
        if cupon:
            currentCupon = orderModel.cupon.objects.get(pk=cupon)
            if currentCupon.start <= dt <= currentCupon.end  and currentCupon.status == "Active":
                if currentCupon.limit_type == "limited":
                    currentCupon.limit = currentCupon.limit - 1
                    # currentCupon.save()
            else:
                cuonFlag = 1
                message = "Cupon is not valid"
            
        
        if redFlag == 0 and cuonFlag == 0:
            contactobj = contactModel.contact.objects.get(pk=contact)
            locationobj = productModel.Warehouse.objects.get(pk=location)
            accountobj = accountingModel.account.objects.get(pk=account)
            
            # if there is any cupon
            if cupon:
                currentCupon = orderModel.cupon.objects.get(pk=cupon)

                neworder = orderModel.invoice.objects.create(shipping_method=shipping_method,bill=bill, due=due,costing=costing, delivery_charge=delivery_charge,tax=tax,
                                                         discount=discount,discountlimit=discountlimit,cupon=currentCupon,quantity=quantity,
                                                         data=data,contact=contactobj,location=locationobj,account=accountobj,
                                                         delivery_date=delivery_date,invoice_number=invoice_number,address1=address1,
                                                         address2=address2,country=country,district=district,postalCode=postalCode,
                                                         thana=thana,s_phone=s_phone, shipping_address=shipping_address)
                
                for product in request.data["products"]:
                    item = productModel.ProductLocation.objects.get(id=product["id"])
                    orderModel.invoice_item.objects.create(invoice=neworder,product=item,price=product["price"], quantity=product["quantity"],purchase_price=item.purchase_price)
                    # new_quantity = item.quantity - product["quantity"]
                    # item.quantity = new_quantity
                    # item.save()
                if cupon:
                    currentCupon.save()
                
                return Response({"status": "success", "message": message, "id": neworder.id})
            
            else:
                neworder = orderModel.invoice.objects.create(shipping_method=shipping_method,bill=bill,due=due,costing=costing,delivery_charge=delivery_charge,tax=tax,
                                                         discount=discount,discountlimit=discountlimit,quantity=quantity,
                                                         data=data,contact=contactobj,location=locationobj,account=accountobj,
                                                         delivery_date=delivery_date,invoice_number=invoice_number,address1=address1,
                                                         address2=address2,country=country,district=district,postalCode=postalCode,
                                                         thana=thana,s_phone=s_phone,shipping_address=shipping_address)
                for product in request.data["products"]:
                    item = productModel.ProductLocation.objects.get(id=product["id"])
                    orderModel.invoice_item.objects.create(invoice=neworder,product=item,price=product["price"], quantity=product["quantity"],purchase_price=item.purchase_price)
                    # new_quantity = item.quantity - product["quantity"]
                    # item.quantity = new_quantity
                    # item.save()
                if cupon:
                    currentCupon.save()
                
                return Response({"status": "success", "message": message, "id": neworder.id})
            
        else:
            return Response({"status": "failed", "message": message})
            
        # return Response({"status": "success", "message": message, "data": neworder})


class OnlineOrderValidityViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Invoiceserializers
    queryset = models.invoice.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    # filter_backends = [DjangoFilterBackend]
    # filter_class = InvoiceFilter
    
    def create(self, request, *args, **kwargs):
        
        selectedDeliveryMethod = request.data["selectedDeliveryMethod"] 
        shipping_method = request.data["shipping_method"]
        bill = request.data["bill"]
        due = request.data["due"]
        delivery_charge = request.data["delivery_charge"] 
        tax = request.data["tax"] 
        discount = request.data["discount"] 
        discountlimit = request.data["discountlimit"]
        cupon = request.data["cupon"]
        quantity = request.data["quantity"] 
        costing = 0
        
        
        redFlag = 0
        cuonFlag = 0
        message = "Successfully updated"
        for product in request.data["products"]:
            item = productModel.ProductLocation.objects.get(id=product["id"])
            costing += float(product["quantity"]) * float(item.purchase_price)
            if product["quantity"] > item.quantity:
               redFlag = 1
               message = str(item.ProductDetails.title) + " is not available"
        
        current_datetime = str(datetime.datetime.now()) + "+00:00"
        dt = datetime.datetime.fromisoformat(current_datetime)
        
        if cupon:
            currentCupon = orderModel.cupon.objects.get(pk=cupon)
            if currentCupon.start <= dt <= currentCupon.end  and currentCupon.status == "Active":
                if currentCupon.limit_type == "limited":
                    currentCupon.limit = currentCupon.limit - 1
            else:
                cuonFlag = 1
                message = "Cupon is not valid"
            
        
        if redFlag == 0 and cuonFlag == 0:
            return Response({"status": "success", "message": message})
            
        else:
            return Response({"status": "failed", "message": message})
            
        # return Response({"status": "success", "message": message, "data": neworder})




class InvoiceByDeliveryDateViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.InvoiceReadserializers
    queryset = models.invoice.objects.all().order_by('-delivery_date')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoiceFilterByDeliveryDate
    pagination_class = StandardResultsSetPagination

    # def list(self, request, *args, **kwargs):
    #     self.serializer_class = serializers.InvoiceReadserializers
    #     return super().list(request, *args, **kwargs)

    # def retrieve(self, request, *args, **kwargs):
    #     self.serializer_class = serializers.InvoiceReadserializers
    #     return super().retrieve(request, *args, **kwargs)


class ServicesViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Servicesserializers
    queryset = models.services.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = ServiceFilter
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('invoice__id',)
    # permission_classes = (permissions.UpdateOwnProfile,)

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.ServicesReadserializers
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.ServicesReadserializers
        return super().retrieve(request, *args, **kwargs)


class ServicesPViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Servicesserializers
    queryset = models.services.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = ServiceFilter
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.ServicesReadserializers
        response = super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())
        response.data['total_quantity'] = queryset.aggregate(Sum('quantity'))[
            'quantity__sum']
        response.data['total_price'] = queryset.aggregate(Sum('price'))[
            'price__sum']
        response.data['total_cost'] = queryset.aggregate(Sum('cost'))[
            'cost__sum']

        return response

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.ServicesReadserializers
        return super().retrieve(request, *args, **kwargs)


class ServicesCostingFilter(django_filters.FilterSet):

    class Meta:
        model = models.services_costing
        fields = ['services__id', ]


class ServicesCostingViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Services_costingserializers
    queryset = models.services_costing.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = ServicesCostingFilter
    # permission_classes = (permissions.UpdateOwnProfile,)

    def create(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        service_id = request.data.get("services")
        sum = models.services_costing.objects.filter(services=service_id,
                                                     cost__isnull=False).aggregate(Sum('cost'))
        service = models.services.objects.get(id=service_id)
        service.cost = sum['cost__sum']
        service.save()
        # print(sum)
        # print(sum['cost__sum'])
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        service_costing = models.services_costing.objects.get(id=pk)
        service_id = service_costing.services.id
        service_costing.delete()
        sum = models.services_costing.objects.filter(services=service_id,
                                                     cost__isnull=False).aggregate(Sum('cost'))
        service = models.services.objects.get(id=service_id)
        if sum['cost__sum']:
            service.cost = sum['cost__sum']
        else:
            service.cost = 0
        service.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.Services_costingReadserializers
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.Services_costingReadserializers
        return super().retrieve(request, *args, **kwargs)


class reportVIewByDate(APIView):
    "get variation of a specific product"

    def get(self, request, date1, date2):
        "return data"
        if date1:
            queryset = models.invoice.objects.raw(
                'SELECT *, SUM(bill) AS sum, COUNT(bill) AS count FROM order_invoice WHERE created_at BETWEEN %s AND %s GROUP BY issue_date', [date1, date2])
        else:
            queryset = models.invoice.objects.raw(
                'SELECT *, SUM(bill) AS sum, COUNT(bill) AS count FROM order_invoice GROUP BY issue_date')
        result = serializers.InvoiceReportserializers(queryset, many=True)
        return Response(result.data)


# class DeliveryreportVIew(APIView):
#     "get Delivery of a specific product"

#     def get(self, request, date1, date2):
#         "return data"
#         if date1:
#             queryset = models.invoice.objects.raw(
#                 'SELECT * FROM order_invoice WHERE delivery_date BETWEEN %s AND %s', [date1, date2])
#         result = serializers.Invoiceserializers(queryset, many=True)
#         return Response(result.data)


# class ServicereportVIew(APIView):
#     "get service of a specific product"

#     def get(self, request, date1, date2):
#         "return data"
#         if date1:
#             queryset = models.services.objects.raw(
#                 'SELECT * FROM order_services WHERE created_at BETWEEN %s AND %s', [date1, date2])
#         result = serializers.Servicesserializers(queryset, many=True)
#         return Response(result.data)

class PurchaseItemFilter(django_filters.FilterSet):

    class Meta:
        model = models.purchase_item
        fields = ['purchase__id', ]


class PurchaseItemViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.PurchaseItemserializers
    queryset = models.purchase_item.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = PurchaseItemFilter
    # permission_classes = (permissions.UpdateOwnProfile,)

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.PurchaseItemsReaderializers
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.PurchaseItemsReaderializers
        return super().retrieve(request, *args, **kwargs)


class PurchaseFilter(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='lte')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.purchase
        fields = ['start', 'end',
                  'purchase_number', 'contact__id', 'location__id', 'keyward', 'is_received', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(purchase_number__contains=value) | Q(contact__name__contains=value))


class PurchaseViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Purchaseserializers
    queryset = models.purchase.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = [DjangoFilterBackend]
    filter_class = PurchaseFilter

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.PurchaseseReadrializers
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.PurchaseseReadrializers
        return super().retrieve(request, *args, **kwargs)


class PurchaseViewSetP(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Purchaseserializers
    queryset = models.purchase.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = [DjangoFilterBackend]
    filter_class = PurchaseFilter
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.PurchaseseReadrializers
        response = super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())

        response.data['total_discount'] = queryset.aggregate(Sum('discount'))[
            'discount__sum']
        response.data['total_bill'] = queryset.aggregate(Sum('bill'))[
            'bill__sum']
        response.data['total_payment'] = queryset.aggregate(Sum('payment'))[
            'payment__sum']
        response.data['total_due'] = queryset.aggregate(Sum('due'))['due__sum']
        response.data['total_costing'] = queryset.aggregate(Sum('costing'))[
            'costing__sum']
        response.data['total_quantity'] = queryset.aggregate(Sum('quantity'))[
            'quantity__sum']

        response.data['current_page_discount'] = sum(
            [Decimal(data.get('discount', 0)) for data in response.data['results']])
        response.data['current_page_bill'] = sum(
            [Decimal(data.get('bill', 0)) for data in response.data['results']])
        response.data['current_page_payment'] = sum(
            [Decimal(data.get('payment', 0)) for data in response.data['results']])
        response.data['current_page_due'] = sum(
            [Decimal(data.get('due', 0)) for data in response.data['results']])
        response.data['current_page_costing'] = sum(
            [Decimal(data.get('costing', 0)) for data in response.data['results']])
        response.data['current_page_quantity'] = sum(
            [Decimal(data.get('quantity', 0)) for data in response.data['results']])

        return response

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.PurchaseseReadrializers
        return super().retrieve(request, *args, **kwargs)


class WordrobeFilter(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='lte')
    keyword = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.wordrobe
        fields = ['start', 'end','keyword',]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(wordrobe_number__contains=value) | Q(contact__name__contains=value) | Q(contact__phone__contains=value))

class WordrobeViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Wordrobeserializers
    queryset = models.wordrobe.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = WordrobeFilter
    # permission_classes = (permissions.UpdateOwnProfile,)

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.WordrobeReadserializers
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.WordrobeReadserializers
        return super().retrieve(request, *args, **kwargs)

class WordrobePViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.WordrobeReadserializers
    queryset = models.wordrobe.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = WordrobeFilter
    pagination_class = StandardResultsSetPagination

class WordrobeItemFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.wordrobe_item
        fields = ['is_returned', 'keyward', 'wordrobe__id']

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(product__ProductDetails__title__contains=value) | Q(product__barcode__contains=value))


class WordrobeItemViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.WordrobeItemserializers
    queryset = models.wordrobe_item.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = WordrobeItemFilter
    # permission_classes = (permissions.UpdateOwnProfile,)

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.WordrobeItemReadserializers
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.WordrobeItemReadserializers
        return super().retrieve(request, *args, **kwargs)


class WordrobeItemPViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.WordrobeItemserializers
    queryset = models.wordrobe_item.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = WordrobeItemFilter
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.WordrobeItemReadserializers
        response = super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())

        response.data['total_quantity'] = queryset.aggregate(Sum('quantity'))[
            'quantity__sum']
        response.data['total_price'] = queryset.aggregate(Sum('price'))[
            'price__sum']

        response.data['current_page_quantity'] = sum(
            [Decimal(data.get('quantity', 0)) for data in response.data['results']])
        response.data['current_page_price'] = sum(
            [Decimal(data.get('price', 0)) for data in response.data['results']])

        return response

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.WordrobeItemReadserializers
        return super().retrieve(request, *args, **kwargs)


class InvoiceCheckViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Invoiceserializers
    queryset = models.invoice.objects.all().order_by('-id')
    permission_classes = (IsAuthenticatedOrReadOnly,)
    

    def list(self, request, *args, **kwargs):
        invoices = models.invoice.objects.all().order_by('-id')
        Errors = []
        
        for invoice in invoices:
            journals = accountingModel.journal.objects.filter(invoice = invoice)
            debit = 0;
            credit = 0;
            Type = "";
            Salesrevenue = 0;
            accountsReceivable = 0;
            advancefromcustomer = 0;
            for journal in journals:
                if journal.chartofaccount.normally_Debit == "Debit":
                    if journal.increase:
                        debit += journal.amount
                    else:
                        debit -= journal.amount
                else:
                    if journal.increase:
                        credit += journal.amount
                    else:
                        credit -= journal.amount
                
                if str(journal.chartofaccount.account_code) == str(settings.ACCOUNTS_RECEIVABLE):
                    if journal.increase:
                        accountsReceivable += journal.amount
                    else:
                        accountsReceivable -= journal.amount
                        
                if str(journal.chartofaccount.account_code) == str(settings.SALES_REVENUE):
                    if journal.increase:
                        Salesrevenue += journal.amount
                    else:
                        Salesrevenue -= journal.amount
                        
                if str(journal.chartofaccount.account_code) == str(settings.ADVANCE_FROM_CUSTOMERS):
                    if journal.increase:
                        advancefromcustomer += journal.amount
                    else:
                        advancefromcustomer -= journal.amount
                        
            if debit != credit:
                Type += "Trail balance | "
            if accountsReceivable != invoice.due:
                Type += "Accounts Receivable | "
            # if Salesrevenue != invoice.bill:
            #     Type += "Sales revenue | "
            if advancefromcustomer != invoice.advance_payment:
                Type += "Advacne From Customer | "
            if Type != "":
                Errors.append({"invoice number" : invoice.invoice_number ,
                               "Bill": invoice.bill,
                               "Sales revenue": Salesrevenue,
                               "Payment":  invoice.payment,
                               "Advance Payment": invoice.advance_payment,
                               "Due": invoice.due,
                               "Accounts Receivable": accountsReceivable,
                               "Debit" : debit,
                               "Credit" : credit,
                               "status": Type})
        return Response({"message": "Success", "mismatch" : Errors})

class InvoiceCheckautoremoveViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Invoiceserializers
    queryset = models.invoice.objects.all().order_by('-id')
    permission_classes = (IsAuthenticatedOrReadOnly,)
    

    def list(self, request, *args, **kwargs):
        start = datetime.now().date() 
        end = datetime.now() - timedelta(days=365)
        end = end.date() 
        invoices = models.invoice.objects.all().order_by('-id')
        for invoice in invoices:
            journals = accountingModel.journal.objects.filter(invoice = invoice)
            debit = 0;
            credit = 0;
            Type = "";
            Salesrevenue = 0;
            accountsReceivable = 0;
            advancefromcustomer = 0;
            for journal in journals:
                if journal.chartofaccount.normally_Debit == "Debit":
                    if journal.increase:
                        debit += journal.amount
                    else:
                        debit -= journal.amount
                else:
                    if journal.increase:
                        credit += journal.amount
                    else:
                        credit -= journal.amount
                
                if str(journal.chartofaccount.account_code) == str(settings.ACCOUNTS_RECEIVABLE):
                    if journal.increase:
                        accountsReceivable += journal.amount
                    else:
                        accountsReceivable -= journal.amount
                        
                if str(journal.chartofaccount.account_code) == str(settings.SALES_REVENUE):
                    if journal.increase:
                        Salesrevenue += journal.amount
                    else:
                        Salesrevenue -= journal.amount
                        
                if str(journal.chartofaccount.account_code) == str(settings.ADVANCE_FROM_CUSTOMERS):
                    if journal.increase:
                        advancefromcustomer += journal.amount
                    else:
                        advancefromcustomer -= journal.amount
                        
            if debit != credit:
                Type += "Trail balance | "
            if accountsReceivable != invoice.due:
                Type += "Accounts Receivable | "
            # if Salesrevenue != invoice.bill:
            #     Type += "Sales revenue | "
            if advancefromcustomer != invoice.advance_payment:
                Type += "Advacne From Customer | "
            if Type != "":
                Errors.append({"invoice number" : invoice.invoice_number ,
                               "Bill": invoice.bill,
                               "Sales revenue": Salesrevenue,
                               "Payment":  invoice.payment,
                               "Advance Payment": invoice.advance_payment,
                               "Due": invoice.due,
                               "Accounts Receivable": accountsReceivable,
                               "Debit" : debit,
                               "Credit" : credit,
                               "status": Type})
        return Response({"message": "Success", "mismatch" : Errors})

class RefundFilter(django_filters.FilterSet):
    
    start = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='lte')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.Refund
        fields = ['invoice__id','start', 'end', 'invoice__location__id', 'keyward']
    
    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice__invoice_number__contains=value) | Q(invoice__order_number__contains=value) | Q(invoice__contact__name__contains=value) | Q(deatils__contains=value) | Q(reason__contains=value)  )

    
class RefundViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.Refundserializers
    queryset = models.Refund.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = RefundFilter
    pagination_class = StandardResultsSetPagination
    
    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.Refundserializers
        response = super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())

        response.data['total_amount'] = queryset.aggregate(Sum('amount'))[
            'amount__sum']
        response.data['current_page_amount'] = sum(
            [Decimal(data.get('amount', 0)) for data in response.data['results']])
        return response

class RefundItemViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.RefundItemserializers
    queryset = models.Refund_item.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    # filter_class = InvoiceItemFilter