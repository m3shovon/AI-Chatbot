from django.conf import settings
import django_filters
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticatedOrReadOnly,AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from accounting import serializers, models
from order import models as OrderModels
from decimal import Decimal
from django.db import transaction
from time import gmtime, strftime
from datetime import datetime, timedelta, date
from django.utils import timezone
import pytz
# Create your views here.


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100000000


class AccountParentView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.accountparentSerializer
    queryset = models.accountparent.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('name',)


class AccountView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.accountSerilizer
    queryset = models.account.objects.filter(is_active=True).order_by('id')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('name',)


class ChartofAccountsFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.chartofaccount
        fields = ['account_name', 'account_code', 'keyward', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(account_name__contains=value) | Q(account_code__contains=value))


class ChartOfAccountsView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.chartofaccountSerilizer
    queryset = models.chartofaccount.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend]
    filter_class = ChartofAccountsFilter
    

class ChartOfAccountsupdateView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    serializer_class = serializers.chartofaccountSerilizer
    queryset = models.chartofaccount.objects.all().order_by('id')
    
    def list(self, request, *args, **kwargs):
        journals = models.journal.objects.all()
        heads = models.chartofaccount.objects.all()
        for head in heads:
            head.amount = 0
            for journal in journals:
                if journal.chartofaccount ==  head:
                    if journal.increase:
                        head.amount = head.amount + journal.amount
                    else:
                        head.amount = head.amount - journal.amount
            if head.amount >= 0:
                if head.normally_Debit == 'Debit':
                    head.status = "Debit"
                else:
                    head.status = "Credit"
            else:    
                if head.normally_Debit == 'Debit':
                    head.status = "Credit"
                else:
                    head.status = "Debit"
            head.save()
        return Response({"message": "Successfully updated"})


class ChartOfAccountsandaccountstatusView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    serializer_class = serializers.chartofaccountSerilizer
    queryset = models.chartofaccount.objects.all().order_by('id')
    
    # def list(self, request, *args, **kwargs):
    #     journals = models.journal.objects.all()
    #     # heads = models.chartofaccount.objects.all()
    #     statuses = models.accountStatusByDate.objects.all()
    #     # all dates
    #     for status in statuses:
    #         # all accounts in a date
    #         for account in status.data["accounts"]:
    #             # if account is cash
    #             if account["name"] == "CASH":
    #                 # get all journal of cash
    #                 journals = models.journal.objects.filter(Q(created__contains = status.created), Q(chartofaccount_id = 7))
    #                 total = 0
    #                 for journal in journals:
    #                     if journal.increase:
    #                         total = total + journal.amount
    #                     else:
    #                         total = total - journal.amount
    #                 # if date account and journal does't match
    #                 if float(total) != float(account["amount"]):
    #                     print(status)
    #                     print(account)
    #                     print(total)
    #                 #     for journal in journals:
    #                 #         print(journal)
    #                 #         print(journal.account)
    #                 #     print("------------")
                        
                        
    #         # get all journal of bank
    #         journals = models.journal.objects.filter(Q(created__contains = status.created), Q(chartofaccount_id = 31))
    #         total = 0
    #         for journal in journals:
    #             if journal.increase:
    #                 total = total + journal.amount
    #             else:
    #                 total = total - journal.amount
                    
    #         # Count other methods total of a specific date
    #         OtherMethodsTotal = 0
    #         for account in status.data["accounts"]:
    #             if account["name"] != "CASH":
    #                 OtherMethodsTotal = float(OtherMethodsTotal) + float(account["amount"])
    #         # if other methods total of a specific date and journal does't match
    #         if float(total) != float(OtherMethodsTotal):
    #             print("Others")
    #             # print(status)
    #             # print(str(total) + " --- " + str(OtherMethodsTotal))
    #             # for journal in journals:
    #             #     print(journal)
    #             #     print(journal.account)
    #             # print("------------")
                    
    #     return Response({"message": "Successfully updated"})
    
    def list(self, request, *args, **kwargs):
        journals = models.journal.objects.all()
        for journal in journals:
            if (journal.account is None) and ((str(journal.chartofaccount.account_code) == str(settings.CASH)) or (str(journal.chartofaccount.account_code) == str(settings.BANK))):
                print(journal)
                print(journal.account)
                print(journal.chartofaccount.account_code)
                print("---------")
                
            
        return Response({"message": "Successfully updated"})


class AccountsupdateView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    serializer_class = serializers.chartofaccountSerilizer
    queryset = models.accountStatusByDate.objects.all().order_by('id')
    
    def list(self, request, *args, **kwargs):
        journals = models.journal.objects.filter(Q(chartofaccount__account_code=settings.CASH) | Q(chartofaccount__account_code=settings.BANK))
        accountsstatusbydate = models.accountStatusByDate.objects.all()
        for data in accountsstatusbydate:
            data.data = {"accounts" : []}
            data.save()
        for journal in journals:
            if (str(journal.chartofaccount.account_code) == str(settings.CASH)) or (str(journal.chartofaccount.account_code) == str(settings.BANK) ):
                
                with transaction.atomic():
                    accountStatusByDate, created = models.accountStatusByDate.objects.get_or_create(created=journal.created.date())
                    if accountStatusByDate.data:
                        if journal.account is not None:
                            flag = 0
                            amount = 0
                            for account in accountStatusByDate.data["accounts"]:
                                if account["id"] == journal.account.id:
                                    flag = 1
                                    amount = Decimal(account["amount"])
                                    if journal.increase ==  False:
                                        amount = Decimal(amount) - Decimal(journal.amount)
                                    else:
                                        amount = Decimal(amount) + Decimal(journal.amount)
                                    account["amount"] = str(amount)
                                    accountStatusByDate.save()
                            
                            if flag == 0:
                                # print("no match")
                                amount = 0
                                if  journal.increase ==  False:
                                    amount = Decimal(amount) - Decimal(journal.amount)
                                else:
                                    amount = Decimal(amount) + Decimal(journal.amount)
                                newdata = {"id": journal.account.id, "name": journal.account.name, "amount": str(amount)}
                                accountStatusByDate.data["accounts"].append(newdata)
                                accountStatusByDate.save()
                        else:
                            # print(journal)
                            flag = 0
                            amount = 0
                            for account in accountStatusByDate.data["accounts"]:
                                if account["id"] == "999":
                                    flag = 1
                                    amount = Decimal(account["amount"])
                                    if journal.increase ==  False:
                                        amount = Decimal(amount) - Decimal(journal.amount)
                                    else:
                                        amount = Decimal(amount) + Decimal(journal.amount)
                                    account["amount"] = str(amount)
                                    accountStatusByDate.save()
                            
                            if flag == 0:
                                amount = 0
                                if  journal.increase ==  False:
                                    amount = Decimal(amount) - Decimal(journal.amount)
                                else:
                                    amount = Decimal(amount) + Decimal(journal.amount)
                                newdata = {"id": "999", "name": "Untracked", "amount": str(amount)}
                                accountStatusByDate.data["accounts"].append(newdata)
                                accountStatusByDate.save()
                    else:
                        if journal.account is not None:
                            amount = 0
                            if journal.increase == False:
                                amount = Decimal(amount) - Decimal(journal.amount)
                            else:
                                amount = Decimal(amount) + Decimal(journal.amount)
                            account = []
                            account.append({"id": journal.account.id, "name": journal.account.name, "amount":  str(amount)})
                            accountStatusByDate.data = {"accounts" : account}
                        else:
                            # print(journal)
                            amount = 0
                            if journal.increase == False:
                                amount = Decimal(amount) - Decimal(journal.amount)
                            else:
                                amount = Decimal(amount) + Decimal(journal.amount)
                            account = []
                            account.append({"id": "999", "name": "Untacked", "amount":  str(amount)})
                            accountStatusByDate.data = {"accounts" : account}
                        accountStatusByDate.save()
                    
        return Response({"message": "Successfully updated"})
    

class AccountsresetView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    # serializer_class = serializers.chartofaccountSerilizer
    queryset = models.accountStatusByDate.objects.all().order_by('id')
    
    def list(self, request, *args, **kwargs):
        accountsstatusbydate = models.accountStatusByDate.objects.all()
        for data in accountsstatusbydate:
            data.data = {"accounts" : []}
            data.save()
        return Response({"message": "Successfully updated"})
    
    
class JournalFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    code = django_filters.CharFilter(
        method='filter_by_code', lookup_expr='icontains')

    phone = django_filters.CharFilter(
        method='filter_by_phone', lookup_expr='icontains')
    haveAccount = django_filters.CharFilter(
        method='filter_by_account', lookup_expr='icontains')

    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.journal
        fields = ['start', 'end', 'keyward', 'code', 'haveAccount',
                  'is_checked', 'account__id', 'product__id',
                  'chartofaccount__account_code', 'invoice__id', 'invoice__invoice_number',
                  'purchasee__purchase_number', 'employe__id', 'contact__phone', 'invoice__contact__phone', 'phone', 'outlet'
                  ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(details__contains=value)
                               | Q(chartofaccount__account_name__contains=value) | Q(chartofaccount__account_code=value)
                               | Q(chartofaccount__group__account_code=value)
                               | Q(chartofaccount__sub_group__account_code=value))

    def filter_by_code(self, queryset, name, value):
        return queryset.filter(Q(chartofaccount__account_code=value)
                               | Q(chartofaccount__group__account_code=value)
                               | Q(chartofaccount__sub_group__account_code=value)).\
            exclude(
                chartofaccount__account_code__startswith=settings.COST_OF_GOOD_SOLD)

    def filter_by_phone(self, queryset, name, value):
        return queryset.filter(Q(invoice__contact__phone=value)
                               | Q(contact__phone=value)
                               | Q(purchasee__contact__phone=value))

    def filter_by_account(self, queryset, name, value):
        if value:
            return queryset.filter(account__id__gte=0)


class JournalView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.journalSerilizer
    queryset = models.journal.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = JournalFilter
    
    
class AccountStatusFilter(django_filters.FilterSet):
    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.accountStatusByDate
        fields = ['start', 'end', 'created']


        
class AccountStatusByDateView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.AccountStatusByDateSerializer
    queryset = models.accountStatusByDate.objects.all().order_by('-created')
    filter_backends = [DjangoFilterBackend]
    filter_class = AccountStatusFilter


class JournalwithinvoiceView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.journalSerilizerwithinvoice
    queryset = models.journal.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = JournalFilter


class JournalViewPagination(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.journalSerilizer
    queryset = models.journal.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = JournalFilter
    pagination_class = StandardResultsSetPagination


class paymentvoucherFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.paymentvoucher
        fields = ['start','end','voucher_number', 'location__id', 'account__id',
                  'employee__id', 'keyward', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(voucher_number__contains=value) | Q(employee__name__contains=value))


class PaymentvoucherView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.paymentvoucherSerilizer
    queryset = models.paymentvoucher.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = paymentvoucherFilter


class PaymentvoucherViewP(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.paymentvoucherSerilizer
    queryset = models.paymentvoucher.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = paymentvoucherFilter
    pagination_class = StandardResultsSetPagination


class paymentvoucheritemFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.paymentvoucheritems
        fields = ['start', 'end', 'paymentvoucher__voucher_number', 'paymentvoucher__id', 'location__id', 'account__id',
                  'employee__id', 'chartofaccount__id', 'contact__id', 'invoice__invoice_number', 'purchasee__purchase_number', 'keyward', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice__invoice_number__contains=value) | Q(paymentvoucher__voucher_number__contains=value))


class paymentvoucheritemsView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.paymentvoucheritemsSerilizer
    queryset = models.paymentvoucheritems.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = paymentvoucheritemFilter


class receivevoucherFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    
    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.receivevoucher
        fields = ['start','end','voucher_number', 'location__id',
                  'employee__id', 'account__id', 'keyward', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(voucher_number__contains=value) | Q(employee__name__contains=value))


class ReceivevoucherView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.receivevoucherSerilizer
    queryset = models.receivevoucher.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = receivevoucherFilter
    


class ReceivevoucherViewP(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.receivevoucherSerilizer
    queryset = models.receivevoucher.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = receivevoucherFilter
    pagination_class = StandardResultsSetPagination


class receivevoucheritemsFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.receivevoucheritems
        fields = ['start', 'end', 'receivevoucher__voucher_number', 'receivevoucher__id', 'location__id', 'account__id',
                  'employee__id', 'chartofaccount__id', 'contact__id', 'invoice__invoice_number', 'purchasee__purchase_number', 'keyward', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice__invoice_number__contains=value) | Q(receivevoucher__voucher_number__contains=value))


class ReceivevoucheritemsView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.receivevoucheritemsSerilizer
    queryset = models.receivevoucheritems.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = receivevoucheritemsFilter


class journalvoucherFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.journalvoucher
        fields = ['start','end','voucher_number', 'location__id', 'account__id',
                  'employee__id', 'keyward', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(voucher_number__contains=value) | Q(employee__name__contains=value))


class journalvoucherView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.journalvoucherSerilizer
    queryset = models.journalvoucher.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = journalvoucherFilter

class journalvoucherViewP(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.journalvoucherSerilizer
    queryset = models.journalvoucher.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = journalvoucherFilter
    pagination_class = StandardResultsSetPagination


class journalvoucheritemFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.journalvoucheritems
        fields = ['start', 'end', 'journalvoucher__voucher_number', 'journalvoucher__id', 'location__id', 'account__id',
                  'employee__id', 'chartofaccount__id', 'contact__id', 'invoice__invoice_number', 'purchasee__purchase_number', 'keyward', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(invoice__invoice_number__contains=value) | Q(journalvoucher__voucher_number__contains=value))


class journalvoucheritemsView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.journalvoucheritemsSerilizer
    queryset = models.journalvoucheritems.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = journalvoucheritemFilter


class contravoucherFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.contravoucher
        fields = ['start','end','voucher_number', 'location__id', 'accountFrom__id', 'accountTo__id',
                  'employee__id', 'keyward', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(voucher_number__contains=value) | Q(employee__name__contains=value))

class contravoucherView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.contravoucherSerilizer
    queryset = models.contravoucher.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = contravoucherFilter
    
    
class contravoucherViewP(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.contravoucherSerilizer
    queryset = models.contravoucher.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = contravoucherFilter
    pagination_class = StandardResultsSetPagination


class pettycashFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.pettycash
        fields = ['start', 'end', 'keyward', 'location__id', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(narration__contains=value) | Q(employee__name__contains=value))


class pettycashView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.pettycashSerilizer
    queryset = models.pettycash.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = pettycashFilter


class pettycashTransferFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.pettycash_transfer
        fields = ['start', 'end', 'keyward', 'location__id',
                  'account__id', 'collect_cash', 'add_cash']

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(location__name__contains=value) | Q(account__name__contains=value))


class pettycashTransferView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.pettycashTransferSerilizer
    queryset = models.pettycash_transfer.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = pettycashTransferFilter


class bkashToBankTransferNew(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    serializer_class = serializers.accountSerilizer
    queryset = models.account.objects.all().order_by('-id')
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        # print("--------Start-------")
        # bkash_merchent = models.account.objects.filter(
        #     name__startswith="BKASH-M")
        # print(datetime.today())
        startdattime = timezone.now()
        enddatetime = startdattime - timedelta(days=7)
        start = datetime.now().date() 
        end = datetime.now() - timedelta(days=7)
        end = end.date() 
        journals = models.journal.objects.filter((Q(chartofaccount__account_code=settings.CASH) | 
                                                Q(chartofaccount__account_code=settings.BANK)) &
                                                Q(created__range=[enddatetime, startdattime]))
        accountsstatusbydate = models.accountStatusByDate.objects.filter(created__range=[end,start])
        for data in accountsstatusbydate:
            data.data = {"accounts" : []}
            data.save()
        for journal in journals:
            if (str(journal.chartofaccount.account_code) == str(settings.CASH)) or (str(journal.chartofaccount.account_code) == str(settings.BANK) ):
                with transaction.atomic():
                    accountStatusByDate, created = models.accountStatusByDate.objects.get_or_create(created=journal.created.date())
                    if accountStatusByDate.data:
                        if journal.account is not None:
                            flag = 0
                            amount = 0
                            for account in accountStatusByDate.data["accounts"]:
                                if account["id"] == journal.account.id:
                                    flag = 1
                                    amount = Decimal(account["amount"])
                                    if journal.increase ==  False:
                                        amount = Decimal(amount) - Decimal(journal.amount)
                                    else:
                                        amount = Decimal(amount) + Decimal(journal.amount)
                                    account["amount"] = str(amount)
                                    accountStatusByDate.save()
                            
                            if flag == 0:
                                # print("no match")
                                amount = 0
                                if  journal.increase ==  False:
                                    amount = Decimal(amount) - Decimal(journal.amount)
                                else:
                                    amount = Decimal(amount) + Decimal(journal.amount)
                                newdata = {"id": journal.account.id, "name": journal.account.name, "amount": str(amount)}
                                accountStatusByDate.data["accounts"].append(newdata)
                                accountStatusByDate.save()
                        else:
                            # print(journal)
                            flag = 0
                            amount = 0
                            for account in accountStatusByDate.data["accounts"]:
                                if account["id"] == "999":
                                    flag = 1
                                    amount = Decimal(account["amount"])
                                    if journal.increase ==  False:
                                        amount = Decimal(amount) - Decimal(journal.amount)
                                    else:
                                        amount = Decimal(amount) + Decimal(journal.amount)
                                    account["amount"] = str(amount)
                                    accountStatusByDate.save()
                            
                            if flag == 0:
                                amount = 0
                                if  journal.increase ==  False:
                                    amount = Decimal(amount) - Decimal(journal.amount)
                                else:
                                    amount = Decimal(amount) + Decimal(journal.amount)
                                newdata = {"id": "999", "name": "Untracked", "amount": str(amount)}
                                accountStatusByDate.data["accounts"].append(newdata)
                                accountStatusByDate.save()
                    else:
                        if journal.account is not None:
                            amount = 0
                            if journal.increase == False:
                                amount = Decimal(amount) - Decimal(journal.amount)
                            else:
                                amount = Decimal(amount) + Decimal(journal.amount)
                            account = []
                            account.append({"id": journal.account.id, "name": journal.account.name, "amount":  str(amount)})
                            accountStatusByDate.data = {"accounts" : account}
                        else:
                            # print(journal)
                            amount = 0
                            if journal.increase == False:
                                amount = Decimal(amount) - Decimal(journal.amount)
                            else:
                                amount = Decimal(amount) + Decimal(journal.amount)
                            account = []
                            account.append({"id": "999", "name": "Untacked", "amount":  str(amount)})
                            accountStatusByDate.data = {"accounts" : account}
                        accountStatusByDate.save()
        
        
        # Account transfer according to account status
        todaysentry = models.accountStatusByDate.objects.get(created=start)
        bkash_merchent = models.account.objects.filter(
            type="Mobile banking")
        bank_account = models.account.objects.filter(
            account_no=settings.BKASH_TRANSFER_ACCOUNT).first()

        for bkash in bkash_merchent:
            if not bkash.name == "BKASH-P-922":
                if not bkash.name == "ROCKET-92222":
                    for account in todaysentry.data["accounts"]:
                        if bkash.id == account["id"]:
                            if float(account["amount"]) > 0:
                                print(account)
                                amount =  Decimal(account["amount"])
                                txnCharge = bkash.txnCharge
                                transactionCharge = Decimal(
                                    amount) * Decimal(txnCharge) * Decimal(0.01)
                                # bikash decrease
                                bank = models.chartofaccount.objects.get(account_code=settings.BANK)
                                increase_or_decrease = False
                                details = "From Bkash Account: " + str(
                                    bkash.name)
                                jour = models.journal.objects.create(chartofaccount=bank, account=bkash,
                                                                    details=details, amount=(amount-transactionCharge), increase=increase_or_decrease)
                                # bank increase
                                bank = models.chartofaccount.objects.get(
                                    account_code=settings.BANK)
                                increase_or_decrease = True
                                details = "To Bank Account: " + str(bank_account.name)
                                jour = models.journal.objects.create(chartofaccount=bank, account=bank_account,
                                                                    details=details, amount=(amount-transactionCharge), increase=increase_or_decrease)
                                if txnCharge == 0:
                                    continue
                                # bank charges calculation and journal entry
                                bank_charge = models.chartofaccount.objects.get(
                                    account_code=settings.BANK_COMMISSION)
                                increase_or_decrease = True
                                details = "Transaction Charge " + str(txnCharge) + "%" + " For Bkash Account: " + str(
                                    bkash.name)
                                jour = models.journal.objects.create(chartofaccount=bank_charge, account=bkash,
                                                                    details=details, amount=transactionCharge, increase=increase_or_decrease)

                                bank = models.chartofaccount.objects.get(
                                    account_code=settings.BANK)
                                increase_or_decrease = False
                                details = "Transaction Charge " + str(txnCharge) + "%" + " For Bkash Account: " + str(
                                    bkash.name)
                                jour = models.journal.objects.create(chartofaccount=bank, account=bkash,
                                                                    details=details, amount=transactionCharge, increase=increase_or_decrease)
                                
                                
                    
                    
                    
        # print("--------End-------")
        return Response({"message": "Transferd Successfully"})


class AccountstatusresetView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    serializer_class = serializers.accountSerilizer
    queryset = models.account.objects.all().order_by('-id')
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        startdattime = timezone.now()
        enddatetime = startdattime - timedelta(days=7)
        start = datetime.now().date() 
        end = datetime.now() - timedelta(days=7)
        end = end.date() 
        journals = models.journal.objects.filter((Q(chartofaccount__account_code=settings.CASH) | 
                                                Q(chartofaccount__account_code=settings.BANK)) &
                                                Q(created__range=[enddatetime, startdattime]))
        accountsstatusbydate = models.accountStatusByDate.objects.filter(created__range=[end,start])
        for data in accountsstatusbydate:
            data.data = {"accounts" : []}
            data.save()
        for journal in journals:
            if (str(journal.chartofaccount.account_code) == str(settings.CASH)) or (str(journal.chartofaccount.account_code) == str(settings.BANK) ):
                with transaction.atomic():
                    accountStatusByDate, created = models.accountStatusByDate.objects.get_or_create(created=journal.created.date())
                    if accountStatusByDate.data:
                        if journal.account is not None:
                            flag = 0
                            amount = 0
                            for account in accountStatusByDate.data["accounts"]:
                                if account["id"] == journal.account.id:
                                    flag = 1
                                    amount = Decimal(account["amount"])
                                    if journal.increase ==  False:
                                        amount = Decimal(amount) - Decimal(journal.amount)
                                    else:
                                        amount = Decimal(amount) + Decimal(journal.amount)
                                    account["amount"] = str(amount)
                                    accountStatusByDate.save()
                            
                            if flag == 0:
                                # print("no match")
                                amount = 0
                                if  journal.increase ==  False:
                                    amount = Decimal(amount) - Decimal(journal.amount)
                                else:
                                    amount = Decimal(amount) + Decimal(journal.amount)
                                newdata = {"id": journal.account.id, "name": journal.account.name, "amount": str(amount)}
                                accountStatusByDate.data["accounts"].append(newdata)
                                accountStatusByDate.save()
                        else:
                            # print(journal)
                            flag = 0
                            amount = 0
                            for account in accountStatusByDate.data["accounts"]:
                                if account["id"] == "999":
                                    flag = 1
                                    amount = Decimal(account["amount"])
                                    if journal.increase ==  False:
                                        amount = Decimal(amount) - Decimal(journal.amount)
                                    else:
                                        amount = Decimal(amount) + Decimal(journal.amount)
                                    account["amount"] = str(amount)
                                    accountStatusByDate.save()
                            
                            if flag == 0:
                                amount = 0
                                if  journal.increase ==  False:
                                    amount = Decimal(amount) - Decimal(journal.amount)
                                else:
                                    amount = Decimal(amount) + Decimal(journal.amount)
                                newdata = {"id": "999", "name": "Untracked", "amount": str(amount)}
                                accountStatusByDate.data["accounts"].append(newdata)
                                accountStatusByDate.save()
                    else:
                        if journal.account is not None:
                            amount = 0
                            if journal.increase == False:
                                amount = Decimal(amount) - Decimal(journal.amount)
                            else:
                                amount = Decimal(amount) + Decimal(journal.amount)
                            account = []
                            account.append({"id": journal.account.id, "name": journal.account.name, "amount":  str(amount)})
                            accountStatusByDate.data = {"accounts" : account}
                        else:
                            # print(journal)
                            amount = 0
                            if journal.increase == False:
                                amount = Decimal(amount) - Decimal(journal.amount)
                            else:
                                amount = Decimal(amount) + Decimal(journal.amount)
                            account = []
                            account.append({"id": "999", "name": "Untacked", "amount":  str(amount)})
                            accountStatusByDate.data = {"accounts" : account}
                        accountStatusByDate.save()
        return Response({"message": "Done"})


class Cashbankinvoice(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    serializer_class = serializers.accountSerilizer
    queryset = models.account.objects.all().order_by('-id')
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        startdattime = timezone.now()
        enddatetime = startdattime - timedelta(days=10)
        start = datetime.now().date() 
        end = datetime.now() - timedelta(days=1)
        end = end.date() 
        invoices = OrderModels.invoice.objects.filter(Q(created_at__range=[enddatetime, startdattime]))
        for invoice in invoices:
            journals = models.journal.objects.filter(Q(invoice=invoice) &
                                                    (Q(chartofaccount__account_code=settings.CASH) |
                                                    Q(chartofaccount__account_code=settings.BANK)) &
                                                    Q(created__range=[enddatetime, startdattime]))
            flag = 0
            cash = 0
            bank = 0
            bracbank = 0
            for journal in journals:
                if str(journal.chartofaccount.account_code) == str(settings.BANK):
                    bank = 1
                elif str(journal.chartofaccount.account_code) == str(settings.CASH):
                    cash = 1
                if journal.account.id == 36:
                    bracbank = 1
            if cash == 1 and bank == 1:
                # print("cash and bank transactions")
                invoice.is_mute = True
                invoice.save()
            elif cash == 0 and bank == 1:
                # print("only bank transactions")
                invoice.is_mute = True
                invoice.save()
            elif cash == 1 and bank == 0:
                # print("only cash transactions")
                invoice.is_mute = False
                invoice.save()
            if bracbank == 1:
                # print("bracbank transactions")
                invoice.is_mute = False
                invoice.save()
            # print("----")
        return Response({"message": "Done"})
        
        
# class bkashToBankTransfer(viewsets.ModelViewSet):
#     """Handel creating and updating Attribute"""
#     serializer_class = serializers.accountSerilizer
#     queryset = models.account.objects.all().order_by('-id')
#     permission_classes = (IsAuthenticatedOrReadOnly,)
    
#     def list(self, request, *args, **kwargs):
#         # print("--------Start-------")
#         # bkash_merchent = models.account.objects.filter(
#         #     name__startswith="BKASH-M")
#         bkash_merchent = models.account.objects.filter(
#             type="Mobile banking")
#         bank_account = models.account.objects.filter(
#             account_no=settings.BKASH_TRANSFER_ACCOUNT).first()

#         for bkash in bkash_merchent:
            
#             if not bkash.name == "BKASH-P-922":
#                 if not bkash.name == "ROCKET-92222":
#                     print(bkash.name)
#                     if bkash.cash == 0:
#                         continue

#                     amount = bkash.cash
                    
#                     txnCharge = bkash.txnCharge
#                     transactionCharge = Decimal(
#                         amount) * Decimal(txnCharge) * Decimal(0.01)
#                     # account update
#                     bkash.cash = bkash.cash - amount
#                     bank_account.cash = (bank_account.cash +
#                                         amount) - transactionCharge
#                     bkash.save()
#                     bank_account.save()
                    
                    
#                     # bikash decrease
#                     bank = models.chartofaccount.objects.get(
#                         account_code=settings.BANK)
#                     increase_or_decrease = False
#                     details = "From Bkash Account: " + str(
#                         bkash.name)
#                     jour = models.journal.objects.create(chartofaccount=bank, account=bkash,
#                                                         details=details, amount=(amount-transactionCharge), increase=increase_or_decrease)

#                     # bank increase
#                     bank = models.chartofaccount.objects.get(
#                         account_code=settings.BANK)
#                     increase_or_decrease = True
#                     details = "To Bank Account: " + str(bank_account.name)
#                     jour = models.journal.objects.create(chartofaccount=bank, account=bank_account,
#                                                         details=details, amount=(amount-transactionCharge), increase=increase_or_decrease)

#                     if txnCharge == 0:
#                         continue
#                     # bank charges calculation and journal entry
#                     bank_charge = models.chartofaccount.objects.get(
#                         account_code=settings.BANK_COMMISSION)
#                     increase_or_decrease = True
#                     details = "Transaction Charge " + str(txnCharge) + "%" + " For Bkash Account: " + str(
#                         bkash.name)
#                     jour = models.journal.objects.create(chartofaccount=bank_charge, account=bkash,
#                                                         details=details, amount=transactionCharge, increase=increase_or_decrease)

#                     bank = models.chartofaccount.objects.get(
#                         account_code=settings.BANK)
#                     increase_or_decrease = False
#                     details = "Transaction Charge " + str(txnCharge) + "%" + " For Bkash Account: " + str(
#                         bkash.name)
#                     jour = models.journal.objects.create(chartofaccount=bank, account=bkash,
#                                                         details=details, amount=transactionCharge, increase=increase_or_decrease)
#         # print("--------End-------")
#         return Response({"message": "Transferd Successfully"})