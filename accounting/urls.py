from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounting import views

router = DefaultRouter()
router.register('accounts', views.AccountView)
router.register('accountsparent', views.AccountParentView)
router.register('chartofaccounts', views.ChartOfAccountsView)
router.register('journals', views.JournalView)
router.register('journalsP', views.JournalViewPagination)
router.register('journalswithinvoice', views.JournalwithinvoiceView)

router.register('accountStatusByDate', views.AccountStatusByDateView)

router.register('paymentvoucher', views.PaymentvoucherView)
router.register('paymentvoucheritem', views.paymentvoucheritemsView)
router.register('receivevoucher', views.ReceivevoucherView)
router.register('receivevoucheritems', views.ReceivevoucheritemsView)
router.register('journalvoucher', views.journalvoucherView)
router.register('journalvoucheritems', views.journalvoucheritemsView)
router.register('contravoucher', views.contravoucherView)

router.register('pettycash', views.pettycashView)
router.register('pettycash_transfer', views.pettycashTransferView)
router.register('bkashToBankTransfer', views.bkashToBankTransfer)
router.register('updatechartofaccounts', views.ChartOfAccountsupdateView)
router.register('resetaccounts', views.AccountsupdateView)
# router.register('resetaccounts', views.AccountsresetView)


urlpatterns = [
    path('', include(router.urls)),
]
