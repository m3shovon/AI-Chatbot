from django.contrib import admin
from accounting import models


# class chartofaccountstabel(admin.ModelAdmin):
#     list_display = ['id', 'account_name', 'account_code', 'group',
#                     'sub_group', 'Financial_statement', 'normally_Debit', 'amount', 'status']

#     search_fields = ('account_name', 'account_code', 'pk', 'group__account_name',
#                      'sub_group__account_name', 'Financial_statement')


class accounttabel(admin.ModelAdmin):
    list_display = ['id', 'accountparent', 'name',
                    'account_no', 'type', 'cash', 'txnCharge', 'is_active', ]

    search_fields = ('accountparent__name', 'name',
                     'pk', 'account_no', 'type',)


class journaltabel(admin.ModelAdmin):
    list_display = ['id', 'chartofaccount', 'details',
                    'increase', 'amount', 'outlet', 'created']

    search_fields = ('details', 'chartofaccount__account_name', 'pk',)


# class vouchertabel(admin.ModelAdmin):
#     list_display = ['id', 'voucher_number', 'employee',
#                     'amount', 'location', 'referance', 'created']

#     search_fields = ('voucher_number', 'pk',)


# class paymentvoucheritemtabel(admin.ModelAdmin):
#     list_display = ['id', 'paymentvoucher', 'chartofaccount',
#                     'narration', 'increase', 'amount', 'created']

#     search_fields = ('chartofaccount__account_name', 'pk',
#                      'narration', 'paymentvoucher__voucher_number')


# class receivevoucheritemtabel(admin.ModelAdmin):
#     list_display = ['id', 'receivevoucher', 'chartofaccount',
#                     'narration', 'increase', 'amount', 'created']

#     search_fields = ('chartofaccount__account_name', 'pk',
#                      'narration', 'receivevoucher__voucher_number')


# class journalvoucheritemtabel(admin.ModelAdmin):
#     list_display = ['id', 'journalvoucher', 'chartofaccount',
#                     'narration', 'increase', 'amount', 'created']

#     search_fields = ('chartofaccount__account_name', 'pk',
#                      'narration', 'journalvoucher__voucher_number')


# Register your models here.
admin.site.register(models.account, accounttabel)
admin.site.register(models.accountStatusByDate)
# admin.site.register(models.accountStatus)
# admin.site.register(models.chartofaccount, chartofaccountstabel)
admin.site.register(models.journal, journaltabel)
# admin.site.register(models.paymentvoucher, vouchertabel)
# admin.site.register(models.paymentvoucheritems, paymentvoucheritemtabel)
# admin.site.register(models.receivevoucher, vouchertabel)
# admin.site.register(models.receivevoucheritems, receivevoucheritemtabel)
# admin.site.register(models.journalvoucher, vouchertabel)
# admin.site.register(models.journalvoucheritems, journalvoucheritemtabel)
# admin.site.register(models.contravoucher, vouchertabel)
admin.site.register(models.pettycash)
admin.site.register(models.pettycash_transfer)
