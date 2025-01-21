from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ecommerce import views

router = DefaultRouter()
router.register('page', views.pageViewSet)
router.register('image', views.imageViewSet)
router.register('feature', views.featureViewSet)
router.register('featureitem', views.feature_itemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
