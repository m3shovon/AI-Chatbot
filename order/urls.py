from django.urls import path, include, register_converter
from datetime import datetime
from rest_framework.routers import DefaultRouter
from order import views


class DateConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return value


register_converter(DateConverter, 'yyyy')


router = DefaultRouter()
router.register('deliverytype', views.DeliveryTypeViewSet)
router.register('invoices', views.InvoiceViewSet)
router.register('invoicesP', views.InvoiceViewSetP)
router.register('items', views.InvoiceItemViewSet)
router.register('items-copy', views.InvoiceItemCopyViewSet)
router.register('exchange', views.InvoiceExchangeViewSet)
router.register('invoicepayments', views.InvoicePayementViewSet)
router.register('solditems', views.SoldProductsViewSet)
router.register('measurement', views.MeasurementViewSet)
router.register('purchase', views.PurchaseViewSet)
router.register('purchaseP', views.PurchaseViewSetP)

router.register('purchaseitem', views.PurchaseItemViewSet)
router.register('wordrobe', views.WordrobeViewSet)
router.register('wordrobeitem', views.WordrobeItemViewSet)
router.register('wordrobeitemP', views.WordrobeItemPViewSet)
router.register('Services', views.ServicesViewSet)
router.register('ServicesP', views.ServicesPViewSet)
router.register('costings', views.ServicesCostingViewSet)
router.register('cupon', views.CuponViewSet)
router.register('delivery', views.InvoiceByDeliveryDateViewSet)
router.register('vat', views.InvoiceVatViewSet)
router.register('draftimages', views.DraftImageViewSet)
router.register('draftorders', views.DraftOrderViewSet)
router.register('draftcostsheets', views.DraftCostSheetViewSet)
# router.register('nesteddraftcostsheets', views.DraftCostSheetNestedViewSet)
router.register('excelsales', views.InvoiceExcelViewSet)


router.register('onlineorder', views.OnlineOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('report/<yyyy:date1>/<yyyy:date2>', views.reportVIewByDate.as_view()),
    path('invoice/<int:pk>',
         views.InvoiceClientViewSet.as_view({'get': 'retrieve'})),

    # path('delivery/<yyyy:date1>/<yyyy:date2>',
    #      views.DeliveryreportVIew.as_view()),
    # path('service/<yyyy:date1>/<yyyy:date2>',
    #      views.ServicereportVIew.as_view()),
]
