from django.urls import path, include
from rest_framework.routers import DefaultRouter
from product import views

router = DefaultRouter()
router.register('attribute', views.AttributeView)
router.register('tag', views.TagView)
router.register('brand', views.BrandView)

router.register('term', views.AttributeTermView)
router.register('category', views.CategoryView)
# fetch product category wise
router.register('categoryProduct', views.CategoryProductView)

router.register('updatecategory', views.CategoryUpdateView)
# fetch parent product
router.register('singpleproduct', views.SingleProductView)
router.register('Details', views.ProductdetailsView)  # fetch product details

router.register('lowstock', views.LowProductdetailsView)
# create and update single product
router.register('DetailsUpdate', views.ProductdetailsUpdateView)

router.register('product', views.ProductView)  # create bulk product
router.register('bulkproduct', views.BulkProductView)

router.register('warehouse', views.warehouseView)
router.register("image", views.ProductImageView)
router.register('transfer', views.TransferViewSet)
router.register('transferP', views.TransferPViewSet)
router.register('transferitem', views.TransferItemViewSet)
# router.register('variation', views.ProductcvariationView)

router.register('custom', views.CustomQueryView)


# for online shop
router.register('shopcategory', views.ShopCategoryView)
router.register('shopitems', views.ShopitemsView)  # fetch product details
router.register('shopfilters', views.ShopfilterView)

urlpatterns = [
    path('', include(router.urls)),
    path('getvariations/<int:pk>/', views.VariationVIew.as_view()),
    path('getvariations', views.VariationAllVIew.as_view())
]
