from django.urls import path, include
from rest_framework.routers import DefaultRouter
from userlog import views
import notifications.urls
import notifications_rest.urls

router = DefaultRouter()
router.register('logs', views.LogsViewSet)
router.register('importlogs', views.LogsImportViewSet)


urlpatterns = [
    path('', include(router.urls)),
    
]
