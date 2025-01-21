from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hrm import views

router = DefaultRouter()
router.register('GroupOfCompany', views.GroupOfCompanyViewSet)
router.register('Company', views.CompanyViewSet)

router.register('Department', views.DepartmentViewSet)
router.register('Designation', views.DesignationViewSet)

router.register('OfficeType', views.OfficeTypeViewSet)
router.register('OfficeLocation', views.OfficeLocationViewSet)
router.register('updateOfficeLocation', views.OfficeLocationUpdateView)
router.register('Office', views.OfficeViewSet)
router.register('Officeall', views.OfficeallViewSet)

router.register('Employee', views.EmployeeViewSet)
# router.register('employee-profile', views.EmployeeProfileViewSet)
router.register('EmployeeDocument', views.EmployeeDocumentViewSet)

router.register('IncreamentPolicy', views.IncreamentPolicyViewSet)
router.register('Permissions', views.PermissionViewSet)
router.register('leave-type', views.LeaveTypeViewSet)
router.register('employee-leave', views.EmployeeLeaveViewSet)
router.register('attendance', views.AttendanceViewSet)
router.register('salary', views.EmployeeSalaryViewSet)
router.register('salary-payment', views.EmployeeSalaryPaymentViewSet)
router.register('loan', views.EmployeeLoanViewSet)
router.register('loan-payment', views.EmployeeLoanPaymentViewSet)
router.register('payslip', views.PaySlipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
