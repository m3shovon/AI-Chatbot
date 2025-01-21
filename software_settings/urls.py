from django.urls import path, include
from rest_framework.routers import DefaultRouter
from software_settings import views

router = DefaultRouter()
router.register('business', views.BusinessViewSet)
router.register('module', views.moduleViewSet)
router.register('sub_module', views.sub_moduleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
