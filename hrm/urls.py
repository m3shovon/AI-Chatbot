from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hrm import views

router = DefaultRouter()
router.register('leave-type', views.LeaveTypeViewSet)
router.register('employee-leave', views.EmployeeLeaveViewSet)
router.register('employee-leaveP', views.EmployeeLeavePViewSet)
router.register('attendance', views.AttendanceViewSet)
router.register('attendanceReport', views.AttendanceReportViewSet)
router.register('salary', views.EmployeeSalaryViewSet)
router.register('salaryP', views.EmployeeSalaryPViewSet)
router.register('salary-payment', views.EmployeeSalaryPaymentViewSet)
router.register('loan', views.EmployeeLoanViewSet)
router.register('loanP', views.EmployeeLoanPaginationViewSet)
router.register('loan-payment', views.EmployeeLoanPaymentViewSet)
router.register('payslip', views.PaySlipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
