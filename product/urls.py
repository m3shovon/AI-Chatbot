from django.urls import path, include
from rest_framework.routers import DefaultRouter
from product import views

router = DefaultRouter()
router.register('attribute', views.AttributeView)
router.register('term', views.AttributeTermView)
router.register('category', views.CategoryView)
# fetch product category wise
router.register('categoryProduct', views.CategoryProductView)
router.register('updatecategory', views.CategoryUpdateView)

# fetch parent product
router.register('singpleproduct', views.SingleProductView)
router.register('productwithalldetails', views.Productwithalldetails)
# fetch product details
router.register('Details', views.ProductdetailsView)
# create and update single product
router.register('DetailsUpdate', views.ProductdetailsUpdateView)
router.register('productentryledger', views.ProductLocationEntryView)
router.register('DetailsUpdateCustom', views.ProductdetailsUpdateCustomView)
router.register('product', views.ProductView)  # create bulk product
# router.register('warehouse', views.warehouseView)
# router.register('treewarehouse', views.treewarehouseView)

router.register("image", views.ProductImageView)
router.register('transfer', views.TransferViewSet)
router.register('transferP', views.TransferPViewSet)
router.register('transferitem', views.TransferItemViewSet)
router.register('BarcodePrintList', views.BarcodePrintListViewSet)
router.register('floating-transfer-items', views.FloatingTransferItemView)
# router.register('variation', views.ProductcvariationView)

urlpatterns = [
    path('', include(router.urls)),
    path('getvariations/<int:pk>/', views.VariationVIew.as_view())
    # path('getvariations/<int:pk>/', views.VariationVIew.as_view())
]
