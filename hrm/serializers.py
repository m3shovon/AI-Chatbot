from rest_framework import serializers
from contact import models
from django.contrib.admin.models import LogEntry

from contact.models import Department, userRole, EmployeeProfile
from accounting.models import account
from contact.serializers import EmployeeSerializer
from contact.models import UserProfile
from hrm.models import LeaveType, EmployeeLeave, Attendance, Salary, Loan, LoanPayment, SalaryPayment, PaySlip


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["title"] = instance.Typename
        response["key"] = instance.id
        response["value"] = instance.id
        return response


class EmployeeLeaveSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    leaveType = LeaveTypeSerializer(read_only=True)

    class Meta:
        model = EmployeeLeave
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.name
        response["leaveTypeName"] = instance.leaveType.Typename
        return response


class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.name
        return response

class AttendanceReportSerializer(serializers.ModelSerializer):
    # employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.name
        return response


class EmployeeSalarySerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Salary
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        employeeProfile = EmployeeProfile.objects.get(
            employee=instance.employee)
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.name
        response["employeePhone"] = employeeProfile.phone
        response["employeeAddress"] = employeeProfile.address
        response["defaultShift"] = employeeProfile.defaultShift
        response["defaultEntryTime"] = employeeProfile.defaultEntryTime
        response["defaultExitTime"] = employeeProfile.defaultExitTime
        response["employeeRole"] = instance.employee.user_role.name
        response["employeeBranch"] = instance.employee.branch.name
        response["dailyWage"] = round(
            instance.get_daily_payment_day_shift(), 2)
        response["perHourWageDay"] = round(
            instance.get_hourly_payment_day_shift(), 2)
        response["perHourWageNight"] = round(
            instance.get_hourly_payment_night_shift(), 2)
        return response


class EmployeeSalaryPaymentSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = SalaryPayment
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        employeeProfile = EmployeeProfile.objects.get(
            employee=instance.employee)
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.name
        response["employeePhone"] = employeeProfile.phone
        response["employeeAddress"] = employeeProfile.address
        response["employeeRole"] = instance.employee.user_role.name
        response["employeeBranch"] = instance.employee.branch.name
        response["paidAmount"] = instance.paidAmount
        response["paymentDate"] = instance.paymentDate
        return response


class EmployeeLoanSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Loan
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        employeeProfile = EmployeeProfile.objects.get(
            employee=instance.employee)
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.name
        response["employeePhone"] = employeeProfile.phone
        response["employeeAddress"] = employeeProfile.address
        response["employeeRole"] = instance.employee.user_role.name
        response["employeeBranch"] = instance.employee.branch.name
        if instance.payment_method:
            paymentmethod = account.objects.get(id=instance.payment_method.id)
            response["payment"] = instance.payment_method.name

        employeeLoanPayment = LoanPayment.objects.filter(
            employee=instance.employee, loan=instance.id)
        total_paid = 0
        total_payment_count = len(employeeLoanPayment)
        for payment in employeeLoanPayment:
            total_paid = total_paid + payment.paidAmount
        due_payment = int(instance.loanAmount) - int(total_paid)
        response["total_payment_count"] = total_payment_count
        response["total_paid"] = total_paid
        response["total_due_payment"] = due_payment
        return response




class EmployeeLoanPaymentSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    loan = EmployeeLoanSerializer(read_only=True)

    class Meta:
        model = LoanPayment
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        employeeProfile = EmployeeProfile.objects.get(
            employee=instance.employee)
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.name
        response["employeePhone"] = employeeProfile.phone
        response["employeeAddress"] = employeeProfile.address
        response["employeeRole"] = instance.employee.user_role.name
        response["employeeBranch"] = instance.employee.branch.name
        response["loanAmount"] = instance.loan.loanAmount
        response["loanType"] = instance.loan.loanType
        response["loanPayableMonths"] = instance.loan.loanPayableMonths
        response["loanPayableAmount"] = instance.loan.loanPayableAmount
        response["loanStatus"] = instance.loan.loanStatus
        response["note"] = instance.loan.note
        return response


class PaySlipSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    salary = EmployeeSalarySerializer(read_only=True)

    class Meta:
        model = PaySlip
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        employeeProfile = EmployeeProfile.objects.get(
            employee=instance.employee)
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.name
        response["employeePhone"] = employeeProfile.phone
        response["employeeAddress"] = employeeProfile.address
        response["employeeDepartment"] = instance.employee.user_role.department.name
        response["employeeRole"] = instance.employee.user_role.name
        response["employeeBranch"] = instance.employee.branch.name
        response["Basesalary"] = instance.salary.monthlySalary
        response["dailyAllowance"] = instance.salary.dailyAllowance
        response["incentive"] = instance.salary.incentive
        response["BonusPercent"] = 0
        if instance.bonusamount > 0:
            response["BonusPercent"] = (instance.bonusamount * 100)/instance.salary.monthlySalary
        response["overtimeHour"] = instance.overtimeTotal - (instance.dayOverTime + instance.nightOverTime)
        response["inTotalIncome"] = instance.salary.monthlySalary + instance.overtimeTotal + instance.dailyAllowanceTotal + instance.bonusamount
        response["inTotalDeduction"] = instance.loan_adjustment + instance.fine + instance.advance_adjustment + instance.manual_adjustment
        return response
