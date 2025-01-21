from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contact import views
import notifications.urls
import notifications_rest.urls

router = DefaultRouter()
router.register('user', views.UserProfileViewSet)
router.register('contact', views.ContactView)
router.register('contacttype', views.ContactTypeViewSet)
router.register('log', views.UserLog)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.UserLoginApiView.as_view()),
    path('inbox/notifications/',
         include(notifications.urls, namespace='notifications')),
    path('notifications/', include(notifications_rest.urls)),
    # path('reset-session-timeout/', views.reset_session_timeout, name='reset-session-timeout'),
]
