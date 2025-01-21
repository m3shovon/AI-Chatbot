from django.db import models
from django.utils import timezone
import datetime
from django.db.models.signals import post_save, post_delete, pre_save
# Create your models here.
from contact.models import UserProfile
from hrm.signals import *
from accounting.models import account

class LeaveType(models.Model):
    """Database model for Contact information"""
    Typename = models.CharField(max_length=255)
    initialDays = models.IntegerField(default=0, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.Typename


class EmployeeLeave(models.Model):
    employee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="employee_leave")
    leaveType = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name="employee_leave_type")
    leaveStart = models.DateField(default=timezone.now)
    leaveEnd = models.DateField(default=timezone.now)
    leaveDays = models.IntegerField(default=0, null=True, blank=True)
    leaveStatus = models.CharField(default="pending", max_length=255)
    note = models.TextField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

post_save.connect(notify_leave_application, sender=EmployeeLeave)
post_delete.connect(notify_leave_deletion, sender=EmployeeLeave)


class Attendance(models.Model):
    employee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="employee_attendance")
    attendanceDate = models.DateField(default=datetime.date.today)
    shift = models.CharField(default='day', max_length=255)
    isAttended = models.BooleanField(default=False)
    entryTime = models.TimeField(blank=True, null=True)
    exitTime = models.TimeField(blank=True, null=True)
    note = models.CharField(default="", max_length=255, blank=True, null=True)
    overTime = models.FloatField(default=0.00, blank=True, null=True)
    lateTime = models.FloatField(default=0.00, blank=True, null=True)
    isLate = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Employee : ' + self.employee.name + ' Date: ' + str(self.attendanceDate)

pre_save.connect(attendance_pre_save, sender=Attendance)


class Salary(models.Model):
    employee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="employee_salary")
    monthlySalary = models.FloatField(default=0.00, blank=True, null=True)
    dailyAllowance = models.FloatField(default=0.00, blank=True, null=True)
    incentive = models.FloatField(default=0.00, blank=True, null=True)
    OvertimeNightAllowance = models.FloatField(default=0.00, blank=True, null=True)
    mobileAllowance = models.FloatField(default=0.00, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def get_daily_payment_day_shift(self):
        """Retrieve hourly payment of Day shift"""
        return self.monthlySalary / 30

    def get_hourly_payment_day_shift(self):
        """Retrieve hourly payment of Day shift"""
        return (self.monthlySalary / 30) / 10

    def get_hourly_payment_night_shift(self):
        """Retrieve hourly payment of night shift"""
        # print(self.employee.branch)
        # print(self.employee.branch.id)
        return ((self.monthlySalary / 30) / 10) * 1.5
        # if self.employee.branch.id == 3:
        #     return ((self.monthlySalary / 30) / 10) 
        # else:
        #     return ((self.monthlySalary / 30) / 10) * 1.5
    def __str__(self):
        return 'Employee : ' + self.employee.name + ' Salary: ' + str(self.monthlySalary)


class SalaryPayment(models.Model):
    employee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="employee_salary_payment")
    paidAmount = models.FloatField(default=0.00, blank=True, null=True)
    salaryMonth = models.IntegerField(default=0, blank=True, null=True)
    salaryYear = models.IntegerField(default=0, blank=True, null=True)
    paymentDate = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Employee : ' + self.employee.name +\
               ', Paid: ' + str(self.paidAmount)+ ' Month: ' + str(self.salaryMonth) + '-' + str(self.salaryYear)



             
# employee, loan amount, status-approved or not, loan type- emi/advance,
# date, if emi per month emi amount, will enter total payable month and per month amount ,
# if advance next month will deduct full
class Loan(models.Model):
    employee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="employee_loan")
    loanAmount = models.FloatField(default=0.00, blank=True, null=True)
    loanType = models.CharField(max_length=255, blank=True, null=True)
    loanPayableMonths = models.IntegerField(default=0, blank=True, null=True)
    loanPayableAmount = models.FloatField(default=0.00, blank=True, null=True)
    loanStatus = models.CharField(default="pending", max_length=255)
    loanPaymentStatus = models.CharField(default="pending", max_length=255)
    payment_method = models.ForeignKey(account, on_delete=models.SET_NULL, related_name="loan_payment_method", blank=True, null=True)
    note = models.CharField(default="", max_length=255, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Employee : ' + self.employee.name + ' Loan: ' + str(self.loanAmount)

post_save.connect(loan_post_save, sender=Loan)
pre_save.connect(loan_pre_save, sender=Loan)
post_delete.connect(loan_post_delete, sender=Loan)



class LoanPayment(models.Model):
    employee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="employee_loan_payment")
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="loan_payment_loan")
    paidAmount = models.FloatField(default=0.00, blank=True, null=True)
    paymentDate = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Employee : ' + self.employee.name +\
               ', Loan: ' + str(self.loan.loanAmount) +\
               ', Paid: ' + str(self.paidAmount)

post_save.connect(loan_payment_post_save, sender=LoanPayment)



class PaySlip(models.Model):
    employee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="employee_payslip")
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE, related_name="payslip_salary")
    salaryMonth = models.IntegerField(default=0, blank=True, null=True)
    bonusamount = models.FloatField(default=0.00, blank=True, null=True)
    bonuspercent = models.FloatField(default=0.00, blank=True, null=True)
    salaryYear = models.IntegerField(default=0, blank=True, null=True)
    publicHoliday = models.IntegerField(default=0, blank=True, null=True)
    leave = models.IntegerField(default=0, blank=True, null=True)
    present = models.IntegerField(default=0, blank=True, null=True)
    absent = models.IntegerField(default=0, blank=True, null=True)
    late = models.IntegerField(default=0, blank=True, null=True)
    
    dayOverTime = models.FloatField(default=0.00, blank=True, null=True)
    dayOverTimeHour = models.FloatField(default=0.00, blank=True, null=True)
    nightOverTime = models.FloatField(default=0.00, blank=True, null=True)
    nightOverTimeHour = models.FloatField(default=0.00, blank=True, null=True)
    OverTime = models.FloatField(default=0.00, blank=True, null=True)
    OverTimeHour = models.FloatField(default=0.00, blank=True, null=True)
    overtimeTotal = models.FloatField(default=0.00, blank=True, null=True)
    
    incentiveTotal = models.FloatField(default=0.00, blank=True, null=True)
    dailyAllowanceTotal = models.FloatField(default=0.00, blank=True, null=True)
    OvertimeNightAllowance = models.FloatField(default=0.00, blank=True, null=True)
    mobileAllowance = models.FloatField(default=0.00, blank=True, null=True)
    fine = models.FloatField(default=0.00, blank=True, null=True)
    loan_adjustment = models.FloatField(default=0.00, blank=True, null=True)
    advance_adjustment = models.FloatField(default=0.00, blank=True, null=True)
    manual_adjustment = models.FloatField(default=0.00, blank=True, null=True)
    manual_adjustment_reference = models.TextField(blank=True, null=True)
    net_salary = models.FloatField(default=0.00, blank=True, null=True)
    
    current_salary = models.FloatField(default=0.00, blank=True, null=True)
    current_salary_day = models.FloatField(default=0.00, blank=True, null=True)
    current_salary_day_hour = models.FloatField(default=0.00, blank=True, null=True)
    current_salary_night = models.FloatField(default=0.00, blank=True, null=True)
    current_salary_night_hour = models.FloatField(default=0.00, blank=True, null=True)
    current_allowance = models.FloatField(default=0.00, blank=True, null=True)
    current_OvertimeNightAllowance = models.FloatField(default=0.00, blank=True, null=True)
    current_mobileAllowance = models.FloatField(default=0.00, blank=True, null=True)
    current_loan = models.FloatField(default=0.00, blank=True, null=True)
    
    payment = models.FloatField(default=0.00, blank=True, null=True)
    due = models.FloatField(default=0.00, blank=True, null=True)
    payment_method_1 = models.ForeignKey(account, on_delete=models.SET_NULL, related_name="employee_payment_account1", null=True)
    amount_1 = models.FloatField(default=0.00, blank=True, null=True)
    payment_method_info_1 = models.CharField(max_length=255, blank=True, null=True)
    payment_method_2 = models.ForeignKey(account, on_delete=models.SET_NULL, related_name="employee_payment_account2", null=True)
    amount_2 = models.FloatField(default=0.00, blank=True, null=True)
    payment_method_info_2 = models.CharField(max_length=255, blank=True, null=True)
    paymentDate = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Employee : ' + self.employee.name + ' Month: ' + str(self.salaryMonth) + '-' + str(self.salaryYear)

pre_save.connect(payslip_pre_save, sender=PaySlip)
post_save.connect(payslip_post_save, sender=PaySlip)
post_delete.connect(payslip_post_delete, sender=PaySlip)