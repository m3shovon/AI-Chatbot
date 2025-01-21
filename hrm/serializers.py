from rest_framework import serializers
from contact import models
from django.contrib.admin.models import LogEntry
from accounting.models import account
from contact.models import UserProfile
from hrm.models import LeaveType, EmployeeLeave, Attendance, Salary, Loan, LoanPayment, SalaryPayment, PaySlip, GroupOfCompany, Company, Department, Designation, OfficeType, OfficeLocation, Office, Employee, EmployeeDocument, IncreamentPolicy, Permission
class GroupOfCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupOfCompany
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["title"] = instance.name
        response["key"] = instance.id
        response["value"] = instance.id
        return response


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["title"] = instance.name
        response["key"] = instance.id
        response["value"] = instance.id
        if instance.GroupOfCompany:
            response["GroupOfCompanyName"] = instance.GroupOfCompany.name
        return response


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["title"] = instance.name
        response["key"] = instance.id
        response["value"] = instance.id
        return response


class DesignationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Designation
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["title"] = instance.name
        response["key"] = instance.id
        response["value"] = instance.id
        if instance.Department:
            response["DepartmentName"] = instance.Department.name
        permissions = Permission.objects.filter(
            Designation=instance.id)
        permissions_response = []
        for i in permissions:
            data = PermissionSerializer(i).data
            if i.is_create:
                res = data["Module"] + "." + data["Sub_Module"] + "_is_create"
                permissions_response.append(res)
            if i.is_read:
                res = data["Module"] + "." + data["Sub_Module"] + "_is_read"
                permissions_response.append(res)
            if i.is_update:
                res = data["Module"] + "." + data["Sub_Module"] + "_is_update"
                permissions_response.append(res)
            if i.is_delete:
                res = data["Module"] + "." + data["Sub_Module"] + "_is_delete"
                permissions_response.append(res)
        response["approved_permissions_list"] = permissions_response
        return response


class OfficeTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfficeType
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["title"] = instance.name
        response["key"] = instance.id
        response["value"] = instance.id
        return response


class OfficeLocationUpdateSerilizer(serializers.ModelSerializer):

    class Meta:
        model = OfficeLocation
        fields = '__all__'


class OfficeLocationSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OfficeLocation
        fields = '__all__'

    def get_children(self, obj):
        # query what your want here.
        # print(obj)
        OfficeLocations = OfficeLocation.objects.filter(
            OfficeLocation_parent=obj)
        if OfficeLocations is not None:
            return OfficeLocationSerializer(OfficeLocations, many=True).data
        else:
            return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["title"] = instance.name
        response["key"] = instance.id
        response["value"] = instance.id
        return response


class OfficeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Office
        fields = '__all__'

    def get_children(self, obj):
        # query what your want here.
        # print(obj)
        Offices = Office.objects.filter(
            Office_parent=obj)
        if Offices is not None:
            return OfficeSerializer(Offices, many=True).data
        else:
            return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["title"] = instance.name
        response["key"] = instance.id
        response["value"] = instance.id
        response["CompanyName"] = instance.Company.name
        response["OfficeTypeName"] = instance.OfficeType.name
        response["OfficeLocationName"] = instance.OfficeLocation.name
        Department = instance.Department.all()
        DepartmentList = []
        for i in Department:
            DepartmentList.append(DepartmentSerializer(i).data)
        response["DepartmentList"] = DepartmentList
        return response


class OfficeallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        # url = None
        request = self.context.get('request', None)
        # if instance.photo and request:
        #     url = request.build_absolute_uri(self.photo.url)
        if instance.Designation:
            response["user_roleName"] = instance.Designation.name
            response["Rank"] = instance.Designation.rank
            if instance.Designation.Department:
                response["employeeDepartment"] = instance.Designation.Department.name
            response["user_role"] = {
                "id": instance.Designation.id
            }
        if instance.Office:
            officequeryset = Office.objects.filter(id= instance.Office.id)
            for i in officequeryset:
                response["branch"] = OfficeSerializer(i).data
            response["branchName"] = instance.Office.name
            # response["branch"] = {"id": instance.Office.id}
            # if instance.Office.logo:
            #     response["branch"] = {
            #         "id": instance.Office.id,
            #         "logo": instance.Office.logo
            #     }
            # else:
            #     response["branch"] = {
            #         "id": instance.Office.id,
            #         "logo": "https://meherbysara.s3.amazonaws.com/uploads/products/Meher.png"
            #     }
            
            
        # if url:
        #     response["photo"] = url
        response["email"] = instance.employee.email

        response["is_active"] = instance.employee.is_active
        response["name"] = instance.employee.name
        response["title"] = instance.employee.name
        response["key"] = instance.id
        response["value"] = instance.id
        employeeDocuments = EmployeeDocument.objects.filter(
            employee=instance)
        files = []
        for document in employeeDocuments:
            url = None
            request = self.context.get('request', None)
            if document.file.name and request:
                name = document.file.name
                url = request.build_absolute_uri(document.file.url)
                files.append({'id': document.id, 'name': name, 'url': url})
        response["files"] = files
        return response


class EmployeeDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeDocument
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)

        url = None
        request = self.context.get('request', None)
        if instance.file.name and request:
            url = request.build_absolute_uri(instance.file.url)

        response["name"] = instance.employee.employee.name
        response["email"] = instance.employee.employee.email
        response["file"] = url
        response["user_roleName"] = instance.employee.Designation.name
        return response


class IncreamentPolicySerializer(serializers.ModelSerializer):

    class Meta:
        model = IncreamentPolicy
        fields = '__all__'


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
        # print(instance.employee)
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.employee.name
        response["leaveTypeName"] = instance.leaveType.Typename
        response["title"] = instance.leaveType.Typename
        response["date"] = instance.leaveStart
        response["start"] = str(instance.leaveStart)
        if instance.leaveStart != instance.leaveEnd:
            response["start"] = str(instance.leaveStart) + "T00:00:00"
            response["end"] = str(instance.leaveEnd) + "T24:00:00"
        else:
            response["end"] = str(instance.leaveEnd)
        if instance.leaveStatus == "pending":
            response["color"] = "Purple"
        else:
            response["color"] = "green"
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
        response["date"] = instance.attendanceDate
        # response["date"] = "2022-08-21"
        response["start"] = str(instance.attendanceDate) + \
            "T" + str(instance.entryTime)
        response["end"] = str(instance.attendanceDate) + \
            "T" + str(instance.exitTime)
        if instance.isAttended:
            response["title"] = "Present"
            response["color"] = "green"
        else:
            response["title"] = "Absent"
            response["color"] = "Red"
        if instance.isLate:
            response["title"] = "Late"
            response["color"] = "orange"

        return response


class EmployeeSalarySerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Salary
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.employee.name
        response["employeePhone"] = instance.employee.phone
        response["employeeAddress"] = instance.employee.address
        response["defaultShift"] = instance.employee.defaultShift
        response["defaultEntryTime"] = instance.employee.defaultEntryTime
        response["defaultExitTime"] = instance.employee.defaultExitTime
        response["employeeRole"] = instance.employee.Designation.name
        response["employeeBranch"] = instance.employee.Office.name
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
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.name
        response["employeePhone"] = instance.employee.phone
        response["employeeAddress"] = instance.employee.address
        response["employeeRole"] = instance.employee.Designation.name
        response["employeeBranch"] = instance.employee.Office.name
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
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.employee.name
        response["employeePhone"] = instance.employee.phone
        response["employeeAddress"] = instance.employee.address
        response["employeeRole"] = instance.employee.Designation.name
        response["employeeBranch"] = instance.employee.Office.name
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
        employee = Employee.objects.get(
            employee=instance.employee.id)
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.employee.name
        response["employeePhone"] = employee.phone
        response["employeeAddress"] = employee.address
        response["employeeRole"] = instance.employee.Designation.name
        response["employeeBranch"] = instance.employee.Office.name
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
        response["employeeId"] = instance.employee.id
        response["employeeName"] = instance.employee.name
        response["employeePhone"] = instance.employee.phone
        response["employeeAddress"] = instance.employee.address
        response["employeeDepartment"] = instance.employee.Designation.Department.name
        response["employeeRole"] = instance.employee.Designation.name
        response["employeeBranch"] = instance.employee.Office.name
        response["Basesalary"] = instance.salary.monthlySalary
        response["dailyAllowance"] = instance.salary.dailyAllowance
        response["incentive"] = instance.salary.incentive
        return response


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.module:
            response["Module"] = instance.module.name
        if instance.sub_module:
            response["Sub_Module"] = instance.sub_module.name
            response["Module"] = instance.sub_module.module.name
        return response
