from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contact import views
import notifications.urls
import notifications_rest.urls

router = DefaultRouter()
router.register('user', views.UserProfileViewSet)
router.register('employee', views.EmployeeViewSet)
router.register('employee-profile', views.EmployeeProfileViewSet)
router.register('employee-document', views.EmployeeDocumentViewSet)

router.register('user-role', views.userRoleViewSet)
router.register('role_permission', views.role_permissionViewSet)
router.register('department', views.DepartmentViewSet)

router.register('contact', views.ContactView)
router.register('contactP', views.ContactViewP)
router.register('contacttype', views.ContactTypeViewSet)
router.register('log', views.UserLog)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.UserLoginApiView.as_view()),
    path('inbox/notifications/',
         include(notifications.urls, namespace='notifications')),
    path('notifications/', include(notifications_rest.urls)),
]
