from django.contrib import admin
from hrm.models import LeaveType,EmployeeLeave,Attendance, Salary, SalaryPayment, Loan, LoanPayment, PaySlip
from product.models import Brand
# Register your models here.

class BrandBasedAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Example: Hide this module for a specific Brand
        restricted_brand_name = "ELOR"
        if Brand.objects.filter(name=restricted_brand_name).exists():
            return False  # Hide module
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        restricted_brand_name = "ELOR"
        if Brand.objects.filter(name=restricted_brand_name).exists():
            return False  # Hide view
        return super().has_view_permission(request)


class salaryTable(BrandBasedAdmin):
    # list_display = ['employee', 'monthlySalary']
    search_fields = ['employee__name']

class salaryPaymentTable(BrandBasedAdmin):
    search_fields = ['employee__name']

class loanTable(BrandBasedAdmin):
    search_fields = ['employee__name']    

class loanPaymentTable(BrandBasedAdmin):
    search_fields = ['employee__name']

class AttendancesTable(BrandBasedAdmin):
    list_display = ['id','employee','attendanceDate','shift','isAttended','isLate','entryTime','exitTime','note','created'] 
    search_fields = ( 'employee__name','employee__email','attendanceDate','pk','created')

class EmployeeLeaveTable(BrandBasedAdmin):
    list_display = ['id','employee','leaveType','leaveStart','leaveEnd','leaveDays','leaveStatus','note','created'] 
    search_fields = ( 'employee__name','leaveType__Typename','leaveStatus','pk','created')
    
class LeaveTypeTable(BrandBasedAdmin):
    list_display = ['id','Typename','initialDays'] 
    search_fields = ( 'Typename','pk')
    
class PaySlipTable(BrandBasedAdmin):
    list_display = ['id','employee','salaryMonth','present','absent','late','leave','loan_adjustment','advance_adjustment','net_salary','created'] 
    search_fields = ( 'employee__name','pk','created')
    
admin.site.register(LeaveType,LeaveTypeTable)
admin.site.register(EmployeeLeave,EmployeeLeaveTable)
admin.site.register(Attendance, AttendancesTable)
admin.site.register(Salary,salaryTable)
admin.site.register(SalaryPayment,salaryPaymentTable)
admin.site.register(Loan,loanTable)
admin.site.register(LoanPayment, loanPaymentTable)
admin.site.register(PaySlip, PaySlipTable)
