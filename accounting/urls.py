from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounting import views

router = DefaultRouter()
router.register('accounts', views.AccountView)
router.register('accountsparent', views.AccountParentView)
router.register('chartofaccounts', views.ChartOfAccountsView)
router.register('accountStatusByDate', views.AccountStatusByDateView)

router.register('journals', views.JournalView)
router.register('journalsP', views.JournalViewPagination)
router.register('journalswithinvoice', views.JournalwithinvoiceView)

router.register('paymentvoucher', views.PaymentvoucherView)
router.register('paymentvoucherP', views.PaymentvoucherViewP)
router.register('paymentvoucheritem', views.paymentvoucheritemsView)

router.register('receivevoucher', views.ReceivevoucherView)
router.register('receivevoucherP', views.ReceivevoucherViewP)
router.register('receivevoucheritems', views.ReceivevoucheritemsView)

router.register('journalvoucher', views.journalvoucherView)
router.register('journalvoucherP', views.journalvoucherViewP)
router.register('journalvoucheritems', views.journalvoucheritemsView)

router.register('contravoucher', views.contravoucherView)
router.register('contravoucherP', views.contravoucherViewP)

router.register('pettycash', views.pettycashView)
router.register('pettycash_transfer', views.pettycashTransferView)

# bank to bkash transfer
router.register('bkashToBankTransfer', views.bkashToBankTransferNew)

# Chart of accounts update
router.register('updatechartofaccounts', views.ChartOfAccountsupdateView)

# Reset all account status
router.register('resetaccounts', views.AccountsupdateView)

# Check account status and chart of accounts
router.register('statusandchatofaccounts', views.ChartOfAccountsandaccountstatusView)

# account status check
router.register('accountstatusreset', views.AccountstatusresetView)

# account status check
router.register('cashbankinvoicefilter', views.Cashbankinvoice)


urlpatterns = [
    path('', include(router.urls)),
]
