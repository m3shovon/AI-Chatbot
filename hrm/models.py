from django.db import models
from django.utils import timezone
import datetime
from django.db.models.signals import post_save, post_delete, pre_save
# Create your models here.
# from contact.models import UserProfile
from hrm.signals import *
from accounting.models import account
from software_settings import models as settings_models


class GroupOfCompany(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        """return string representation of our user"""
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)
    GroupOfCompany = models.ForeignKey(GroupOfCompany,
                                       on_delete=models.SET_NULL,
                                       null=True,
                                       blank=True)

    def __str__(self):
        """return string representation of our user"""
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=255)
    rank = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        """return string representation of our user"""
        return self.name


class Designation(models.Model):
    name = models.CharField(max_length=255)
    rank = models.IntegerField(default=0, null=True, blank=True)
    responsibility = models.CharField(max_length=550, null=True, blank=True)
    Department = models.ForeignKey(Department,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True)

    def __str__(self):
        """return string representation of our user"""
        res = str(self.name)
        # if self.Department:
        #     res = res + " - " + str(self.Department.name)
        # if self.rank:
        #     res = res + " - " + str(self.rank)
        return res


class OfficeType(models.Model):
    name = models.CharField(max_length=255)
    rank = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        """return string representation of our user"""
        res = str(self.name)
        if self.rank:
            res = res + " - " + str(self.rank)
        return res


class OfficeLocation(models.Model):
    name = models.CharField(max_length=255)
    OfficeLocation_parent = models.ForeignKey('self',
                                              on_delete=models.SET_NULL,
                                              null=True,
                                              blank=True)

    def __str__(self):
        """return string representation of our user"""
        return self.name


class Office(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='business/outlet/logo',
                             null=True,
                             blank=True)
    Office_parent = models.ForeignKey('self',
                                      on_delete=models.SET_NULL,
                                      null=True,
                                      blank=True)
    Company = models.ForeignKey(Company,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True)
    Department = models.ManyToManyField(
        Department,
        blank=True,
    )
    OfficeType = models.ForeignKey(OfficeType,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True)
    OfficeLocation = models.ForeignKey(OfficeLocation,
                                       on_delete=models.SET_NULL,
                                       null=True,
                                       blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    contact = models.CharField(max_length=500, null=True, blank=True)
    petty_cash = models.DecimalField(default=0,
                                     blank=True,
                                     max_digits=20,
                                     decimal_places=2)
    cash = models.DecimalField(default=0,
                               blank=True,
                               max_digits=20,
                               decimal_places=2)
    is_outlet = models.BooleanField(default=False, null=True, blank=True)
    is_office = models.BooleanField(default=False, null=True, blank=True)
    is_warehouse = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        """return string representation of our user"""
        return self.name


class Employee(models.Model):
    employee = models.OneToOneField('contact.UserProfile',
                                    on_delete=models.CASCADE,
                                    unique=True,
                                    related_name="hrm_employee")
    name = models.CharField(max_length=255)
    Office = models.ForeignKey(Office,
                               on_delete=models.SET_NULL,
                               null=True,
                               blank=True)
    Designation = models.ForeignKey(Designation,
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)
    photo = models.ImageField(upload_to='employee/photo',
                              null=True,
                              blank=True)
    phone = models.CharField(unique=True,
                             max_length=255,
                             null=True,
                             blank=True)
    emergency_phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    defaultShift = models.CharField(default='day', max_length=255)
    defaultEntryTime = models.TimeField(blank=True,
                                        null=True,
                                        default="10:00:00")
    defaultExitTime = models.TimeField(blank=True,
                                       null=True,
                                       default="20:00:00")
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.name = self.employee.name
        super(Employee, self).save(*args, **kwargs)

    def __str__(self):
        """return string representation of our user"""
        return self.employee.email


def user_files_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'employee/files/user_{0}/{1}'.format(instance.employee.id, filename)


class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee,
                                 on_delete=models.CASCADE,
                                 related_name="hrm_employee_document")
    file = models.FileField(upload_to=user_files_directory_path,
                            null=True,
                            blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """return string representation of our user"""
        return self.employee.email + ", File: " + self.file.name


class IncreamentPolicy(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    note = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """return string representation of our user"""
        return self.employee.email + ", File: " + self.file.name


class LeaveType(models.Model):
    """Database model for Contact information"""
    Typename = models.CharField(max_length=255)
    initialDays = models.IntegerField(default=0, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)


class EmployeeLeave(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employee_leave")
    leaveType = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE, related_name="employee_leave_type")
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
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employee_attendance")
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
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employee_salary")
    monthlySalary = models.FloatField(default=0.00, blank=True, null=True)
    dailyAllowance = models.FloatField(default=0.00, blank=True, null=True)
    incentive = models.FloatField(default=0.00, blank=True, null=True)

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
        return ((self.monthlySalary / 30) / 10) * 1.5

    def __str__(self):
        return 'Employee : ' + self.employee.employee.name + ' Salary: ' + str(self.monthlySalary)


class SalaryPayment(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employee_salary_payment")
    paidAmount = models.FloatField(default=0.00, blank=True, null=True)
    salaryMonth = models.IntegerField(default=0, blank=True, null=True)
    salaryYear = models.IntegerField(default=0, blank=True, null=True)
    paymentDate = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Employee : ' + self.employee.name +\
               ', Paid: ' + str(self.paidAmount) + ' Month: ' + \
            str(self.salaryMonth) + '-' + str(self.salaryYear)


# employee, loan amount, status-approved or not, loan type- emi/advance,
# date, if emi per month emi amount, will enter total payable month and per month amount ,
# if advance next month will deduct full
class Loan(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employee_loan")
    loanAmount = models.FloatField(default=0.00, blank=True, null=True)
    loanType = models.CharField(max_length=255, blank=True, null=True)
    loanPayableMonths = models.IntegerField(default=0, blank=True, null=True)
    loanPayableAmount = models.FloatField(default=0.00, blank=True, null=True)
    loanStatus = models.CharField(default="pending", max_length=255)
    loanPaymentStatus = models.CharField(default="pending", max_length=255)
    payment_method = models.ForeignKey(
        account, on_delete=models.SET_NULL, related_name="loan_payment_method", blank=True, null=True)
    note = models.CharField(default="", max_length=255, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Employee : ' + self.employee.name + ' Loan: ' + str(self.loanAmount)


post_save.connect(loan_post_save, sender=Loan)
pre_save.connect(loan_pre_save, sender=Loan)
post_delete.connect(loan_post_delete, sender=Loan)


class LoanPayment(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employee_loan_payment")
    loan = models.ForeignKey(
        Loan, on_delete=models.CASCADE, related_name="loan_payment_loan")
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
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employee_payslip")
    salary = models.ForeignKey(
        Salary, on_delete=models.CASCADE, related_name="payslip_salary")
    salaryMonth = models.IntegerField(default=0, blank=True, null=True)
    salaryYear = models.IntegerField(default=0, blank=True, null=True)
    publicHoliday = models.IntegerField(default=0, blank=True, null=True)
    leave = models.IntegerField(default=0, blank=True, null=True)
    present = models.IntegerField(default=0, blank=True, null=True)
    absent = models.IntegerField(default=0, blank=True, null=True)
    late = models.IntegerField(default=0, blank=True, null=True)
    dayOverTime = models.IntegerField(default=0, blank=True, null=True)
    nightOverTime = models.IntegerField(default=0, blank=True, null=True)
    overtimeTotal = models.FloatField(default=0.00, blank=True, null=True)
    incentiveTotal = models.FloatField(default=0.00, blank=True, null=True)
    dailyAllowanceTotal = models.FloatField(
        default=0.00, blank=True, null=True)
    fine = models.FloatField(default=0.00, blank=True, null=True)
    loan_adjustment = models.FloatField(default=0.00, blank=True, null=True)
    advance_adjustment = models.FloatField(default=0.00, blank=True, null=True)
    net_salary = models.FloatField(default=0.00, blank=True, null=True)
    payment = models.FloatField(default=0.00, blank=True, null=True)
    due = models.FloatField(default=0.00, blank=True, null=True)
    payment_method_1 = models.ForeignKey(
        account, on_delete=models.SET_NULL, related_name="employee_payment_account1", null=True)
    amount_1 = models.FloatField(default=0.00, blank=True, null=True)
    payment_method_info_1 = models.CharField(
        max_length=255, blank=True, null=True)
    payment_method_2 = models.ForeignKey(
        account, on_delete=models.SET_NULL, related_name="employee_payment_account2", null=True)
    amount_2 = models.FloatField(default=0.00, blank=True, null=True)
    payment_method_info_2 = models.CharField(
        max_length=255, blank=True, null=True)
    paymentDate = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'Employee : ' + self.employee.name + ' Month: ' + str(self.salaryMonth) + '-' + str(self.salaryYear)
    
    # def save(self, *args, **kwargs):
    #     if self.payment_method_info_1:
    #         self.payment_method_info_1 = self.payment_method_info_1[:255]
    #         print("======================",self.payment_method_info_1)       
            

    #     if self.payment_method_info_2:
    #         self.payment_method_info_2 = self.payment_method_info_2[:255]
        
    #     super(PaySlip, self).save(*args, **kwargs)



pre_save.connect(payslip_pre_save, sender=PaySlip)
post_save.connect(payslip_post_save, sender=PaySlip)
post_delete.connect(payslip_post_delete, sender=PaySlip)


class Permission(models.Model):
    Designation = models.ForeignKey(
        Designation, on_delete=models.CASCADE, default=None, blank=True, null=True)
    module = models.ForeignKey(
        settings_models.module, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    sub_module = models.ForeignKey(
        settings_models.sub_module, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    is_create = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_update = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        """return string representation of our user"""
        return self.Designation.name + ' - ' + self.sub_module.name
