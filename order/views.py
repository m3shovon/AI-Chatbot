from keyword import kwlist
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
from order import serializers, models
from django.contrib.admin.models import LogEntry
from rest_framework.pagination import PageNumberPagination
from decimal import Decimal
import json
import datetime
import pytz
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404


from product import models as productModel
from order import models as orderModel
from contact import models as contactModel
from accounting import models as accountingModel

# Create your views here.


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000000


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


class InvoiceItemFilter(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='lte')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.invoice_item
        fields = ['invoice__id', 'start', 'end', 'invoice__invoice_number',
                  'invoice__location__id', 'keyward','invoice__is_public']

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice__invoice_number__contains=value) | Q(invoice__order_number__contains=value) | Q(invoice__contact__name__contains=value) | Q(product__barcode__contains=value) | Q(Details__contains=value))



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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        invoice_item_copy = models.invoice_item_copy.objects.filter(
            invoice=instance.invoice,
            product=instance.product,
            Details=instance.Details,
            quantity=instance.quantity,
            price=instance.price,
            purchase_price=instance.purchase_price
        ).first()
        if invoice_item_copy:
            invoice_item_copy.is_exchanged = True
            invoice_item_copy.save()
        self.perform_destroy(instance)
        return Response({"message": "Invoice item deleted and corresponding copy marked as exchanged."}, status=204)



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
    filterset_fields = ('id', 'invoice__id', 'contact__id', 'is_basic')

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
                  'month', 'year', 'contains_item', 'is_public' ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice_number__contains=value) | Q(order_number__contains=value) | Q(status__icontains=value) | Q(remarks__icontains=value) | Q(contact__phone__icontains=value))
 
    def filter_by_month(self, queryset, name, value):
        return queryset.filter(
            Q(issue_date__month=value) | Q(issue_date__month=value)
        )

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
                  'month', 'year', 'contains_item','is_public' ]

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
                  'invoice_number', 'delivery_date', 'Payment_method', 'status', 'contact', 'location', 'account', 'DeliveryType','is_public']


class ServiceFilter(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='lte')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.services
        fields = ['start', 'end',  'invoice__id', 'keyward', 'employe__id','invoice__is_public',]

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
        response.data['total_additional_discount'] = queryset.aggregate(Sum('additional_discount'))[
            'additional_discount__sum']
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
        response.data['current_page_additional_discount'] = sum(
            [Decimal(data.get('additional_discount', 0)) for data in response.data['results']])
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

        redFlag = 0
        cuonFlag = 0
        message = "Successfully updated"
        for product in request.data["products"]:
            item = productModel.ProductLocation.objects.get(id=product["id"])
            if product["quantity"] > item.quantity:
                redFlag = 1
                message = str(item.ProductDetails.title) + " is not available"

        current_datetime = str(datetime.datetime.now()) + "+00:00"
        dt = datetime.datetime.fromisoformat(current_datetime)

        if cupon:
            currentCupon = orderModel.cupon.objects.get(pk=cupon)
            if currentCupon.start <= dt <= currentCupon.end and currentCupon.status == "Active":
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
            if cupon:
                currentCupon = orderModel.cupon.objects.get(pk=cupon)

                neworder = orderModel.invoice.objects.create(shipping_method=shipping_method, bill=bill, delivery_charge=delivery_charge, tax=tax,
                                                             discount=discount, discountlimit=discountlimit, cupon=currentCupon, quantity=quantity,
                                                             data=data, contact=contactobj, location=locationobj, account=accountobj,
                                                             delivery_date=delivery_date, invoice_number=invoice_number)

                for product in request.data["products"]:
                    item = productModel.ProductLocation.objects.get(
                        id=product["id"])
                    orderModel.invoice_item.objects.create(
                        invoice=neworder, product=item, price=product["price"], quantity=product["quantity"], purchase_price=item.purchase_price)
                    new_quantity = item.quantity - product["quantity"]
                    item.quantity = new_quantity
                    item.save()
                if cupon:
                    currentCupon.save()

                return Response({"status": "success", "message": message, "id": neworder.id})

            else:
                neworder = orderModel.invoice.objects.create(shipping_method=shipping_method, bill=bill, delivery_charge=delivery_charge, tax=tax,
                                                             discount=discount, discountlimit=discountlimit, quantity=quantity,
                                                             data=data, contact=contactobj, location=locationobj, account=accountobj,
                                                             delivery_date=delivery_date, invoice_number=invoice_number)
                for product in request.data["products"]:
                    item = productModel.ProductLocation.objects.get(
                        id=product["id"])
                    orderModel.invoice_item.objects.create(
                        invoice=neworder, product=item, price=product["price"], quantity=product["quantity"], purchase_price=item.purchase_price)
                    new_quantity = item.quantity - product["quantity"]
                    item.quantity = new_quantity
                    item.save()
                if cupon:
                    currentCupon.save()

                return Response({"status": "success", "message": message, "id": neworder.id})

        else:
            return Response({"status": "failed", "message": message})

        # return Response({"status": "success", "message": message, "data": neworder})

class InvoicePaymentFilter(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='lte')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.invoice_payment
        fields = ['invoice__id', 'start', 'end',
                  'invoice__location__id', 'keyward','invoice__is_public']

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice__invoice_number__contains=value) | Q(invoice__order_number__contains=value) | Q(invoice__contact__name__contains=value) )


class InvoicePayementViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice payment"""
    serializer_class = serializers.InvoicePaymentserializers
    queryset = models.invoice_payment.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoicePaymentFilter
    pagination_class = StandardResultsSetPagination

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


class WordrobeViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Wordrobeserializers
    queryset = models.wordrobe.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.UpdateOwnProfile,)

    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.WordrobeReadserializers
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.WordrobeReadserializers
        return super().retrieve(request, *args, **kwargs)


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

# class InvoiceVatHide(viewsets.ModelViewSet):
#     queryset

# Draft Order Views
class DraftImageViewSet(viewsets.ModelViewSet):
    queryset = models.DraftImage.objects.all().order_by('-id')
    serializer_class = serializers.DraftImageSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    pagination_class = StandardResultsSetPagination

    def get_serializer_context(self):
        context = super(DraftImageViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context    


class DraftOrderViewSet(viewsets.ModelViewSet):
    queryset = models.DraftOrder.objects.all()
    serializer_class = serializers.DraftOrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    pagination_class = StandardResultsSetPagination

    # def create(self, request, pk=None, *args, **kwargs):
    #     draft_cost = get_object_or_404(models.DraftCostSheet, id=pk)
    #     cost_sheet_items = request.data.get("cost_sheet_items")
    #     draft_order, _ = models.DraftOrder.objects.get_or_create(draft_cost=draft_cost, cost_sheet_items=cost_sheet_items)
    #     serialized = serializers.DraftOrderSerializer(instance=draft_order, data=request.data)
    #     serialized.is_valid(raise_exception=True)
    #     serialized.save(draft_cost=draft_cost, cost_sheet_items=cost_sheet_items)
    #     return Response(serialized.data, status=status.HTTP_201_CREATED)
    
    # def update(self, request, pk=None, *args, **kwargs):
    #     draft_cost = get_object_or_404(models.DraftCostSheet, id=pk)
    #     cost_sheet_items = request.data.get("cost_sheet_items")
    #     draft_order, _ = models.DraftOrder.objects.get_or_create(draft_cost=draft_cost, cost_sheet_items=cost_sheet_items)
    #     serialized = serializers.DraftOrderSerializer(instance=draft_order, data=request.data)
    #     serialized.is_valid(raise_exception=True)
    #     serialized.save(draft_cost=draft_cost, cost_sheet_items=cost_sheet_items)
    #     return Response(serialized.data, status=status.HTTP_200_OK)

def get_serializer_context(self):
    context = super(DraftOrderViewSet, self).get_serializer_context()
    context.update({"request": self.request})
    return context


class DraftCostSheetViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    queryset = models.DraftCostSheet.objects.all()
    serializer_class = serializers.DraftCostSheetSerializer
    filter_backends = [DjangoFilterBackend]

    # def create(self, request):
    #     serializer = self.serializer_class(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def update(self, request, pk=None, *args, **kwargs):
    #     draft_cost = get_object_or_404(models.DraftCostSheet, id=pk)
    #     serialized = serializers.DraftCostSheetSerializer(
    #         instance=draft_cost, data=request.data)
    #     if serialized.is_valid():
    #         draft_cost = serialized.save()
    #         return Response(serialized.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


def get_serializer_context(self):
    context = super(DraftCostSheetViewSet, self).get_serializer_context()
    context.update({"request": self.request})
    return context


class DraftCostSheetNestedViewSet(viewsets.ModelViewSet):
    queryset = models.DraftCostSheet.objects.all()
    serializer_class = serializers.DraftCostSheetNestedSerializer

    # def retrieve(self, request, pk, **kwargs):
    #     cost_sheet = self.get_object(pk, **kwargs)
    #     serializer = self.serializer_class(cost_sheet, data=request.data)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # def list(self, request):
    #     cost_sheets = self.queryset.all()
    #     serializer = self.serializer_class(cost_sheets, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # def destroy(self, request, pk):
    #     cost_sheet = self.get_object(pk)
    #     cost_sheet.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


# class DraftCostSheetViewSet(viewsets.ModelViewSet):
#     queryset = models.DraftCostSheet.objects.all()
#     serializer_class = serializers.DraftCostSheetSerializer
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = [AllowAny]
#     filter_backends = [DjangoFilterBackend]
#     pagination_class = StandardResultsSetPagination

#     def create(self, request, *args, **kwargs):
#         orders = request.data.get("orders")
#         orders = get_object_or_404(models.DraftOrder, id=orders)

#         image = request.data.get("image")
#         image = get_object_or_404(models.DraftImage, id=image)

#         serialized = serializers.DraftCostSheetSerializer(data=request.data)
#         if serialized.is_valid():
#             draft_cost = serialized.save(orders=orders, image=image)
#             return Response(serialized.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

#     def update(self, request, pk=None, *args, **kwargs):
#         draft_cost = get_object_or_404(models.DraftCostSheet, id=pk)
#         orders = request.data.get("orders")
#         orders = get_object_or_404(models.Employee, id=orders)
#         image = request.data.get("image")
#         image = get_object_or_404(models.LeaveType, id=image)

#         serialized = serializers.DraftCostSheetSerializer(
#             instance=draft_cost, data=request.data)
#         if serialized.is_valid():
#             draft_cost = serialized.save(
#                 orders=orders, image=image)
#             return Response(serialized.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceItemCopyFilter(django_filters.FilterSet):
    start = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="issue_date", lookup_expr='lte')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    class Meta:
        model = models.invoice_item_copy
        fields = ['invoice__id', 'start', 'end', 'invoice__invoice_number',
                  'invoice__location__id', 'keyward','invoice__is_public']
    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice__invoice_number__contains=value) | Q(invoice__order_number__contains=value) | Q(invoice__contact__name__contains=value) | Q(product__barcode__contains=value) | Q(Details__contains=value))

class InvoiceItemCopyViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.InvoiceItemCopySerializers
    queryset = models.invoice_item_copy.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoiceItemCopyFilter
    # def list(self, request, *args, **kwargs):
    #     self.serializer_class = serializers.InvoiceItemReadserializers
    #     return super().list(request, *args, **kwargs)
    
    # def retrieve(self, request, *args, **kwargs):
    #     self.serializer_class = serializers.InvoiceItemReadserializers
    #     return super().retrieve(request, *args, **kwargs)

class InvoiceExchangeFilter(django_filters.FilterSet):
    # start = django_filters.IsoDateTimeFilter(
    #     field_name="issue_date", lookup_expr='gte')
    # end = django_filters.IsoDateTimeFilter(
    #     field_name="issue_date", lookup_expr='lte')
    start = django_filters.IsoDateTimeFilter(
        method='filter_by_start_date', label='Start Date'
    )
    end = django_filters.IsoDateTimeFilter(
        method='filter_by_end_date', label='End Date'
    )
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
                  'month', 'year', 'contains_item', 'is_public' ]
        
    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice_number__contains=value) | Q(order_number__contains=value) | Q(status__icontains=value) | Q(remarks__icontains=value) | Q(contact__phone__icontains=value))
 
    def filter_by_start_date(self, queryset, name, value):
        return queryset.filter(invoice_item_copy__updated_at__gte=value).distinct()
    def filter_by_end_date(self, queryset, name, value):
        return queryset.filter(invoice_item_copy__updated_at__lte=value).distinct()
    def filter_by_month(self, queryset, name, value):
        return queryset.filter(
            Q(issue_date__month=value) | Q(issue_date__month=value)
        )
    def filter_by_year(self, queryset, name, value):
        return queryset.filter(
            Q(issue_date__year=value) | Q(issue_date__year=value)
        )
    def filter_by_item(self, queryset, name, value):
        if value:
            return queryset.filter(invoice_item__isnull=False).distinct()
        else:
            return queryset.filter(invoice_item__isnull=True).distinct()
        
class InvoiceExchangeViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.InvoiceExchangeSerializers
    queryset = models.invoice.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = InvoiceExchangeFilter