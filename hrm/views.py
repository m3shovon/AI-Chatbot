from django.contrib.auth.models import UserManager
from django.shortcuts import render, get_object_or_404
from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status, filters
# Create your views here.
# from contact.serializers import EmployeeProfileSerializer
from hrm import serializers, models
from contact import models as contact_model
from contact import serializers as contact_serializer
from django.db.models import Q
from contact import permissions


class GroupOfCompanyViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.GroupOfCompanySerializer
    queryset = models.GroupOfCompany.objects.all()


class CompanyViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.CompanySerializer
    queryset = models.Company.objects.all()


class DepartmentViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.DepartmentSerializer
    queryset = models.Department.objects.all()


class DesignationFilter(django_filters.FilterSet):
    rank = django_filters.NumberFilter(
        field_name="rank", lookup_expr='gte',)

    class Meta:
        model = models.Designation
        fields = ['rank']

    def filter_by_rank(self, queryset, name, value):
        return queryset.filter(Q(employee__name__contains=value) | Q(employee__email__contains=value))


class DesignationViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.DesignationSerializer
    queryset = models.Designation.objects.all().order_by('rank')
    filter_backends = [DjangoFilterBackend]
    filter_class = DesignationFilter


class OfficeTypeViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.OfficeTypeSerializer
    queryset = models.OfficeType.objects.all()


class OfficeLocationViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.OfficeLocationSerializer
    queryset = models.OfficeLocation.objects.all().filter(
        OfficeLocation_parent__isnull=True).order_by('id')


class OfficeLocationUpdateView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.OfficeLocationSerializer
    queryset = models.OfficeLocation.objects.all().order_by('-id')


class OfficeViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.OfficeSerializer
    queryset = models.Office.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('is_outlet', 'is_office','is_warehouse', 'id')
    
    

class OfficeallViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.OfficeallSerializer
    queryset = models.Office.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('is_outlet', 'is_office','is_warehouse', 'id')


class EmployeeFilter(django_filters.FilterSet):
    shift = django_filters.CharFilter(
        method='filter_by_shift', lookup_expr='month')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    is_active = django_filters.CharFilter(
        method='filter_by_is_active', lookup_expr='icontains')

    class Meta:
        model = models.Employee
        fields = ['id', 'name', 'Office__id',
                  'shift', 'keyward', 'is_active']

    def filter_by_is_active(self, queryset, name, value):
        val = True
        if value != "true":
            val = False
        return queryset.filter(
            Q(employee__is_active=val)
        )

    def filter_by_shift(self, queryset, name, value):
        return queryset.filter(
            Q(defaultShift=value)
        )

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(employee__name__contains=value) | Q(employee__email__contains=value))


class EmployeeViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeSerializer
    queryset = models.Employee.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = EmployeeFilter

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        email = request.data.get("email")
        password = request.data.get("password")
        Designation = request.data.get("Designation")
        Office = request.data.get("Office")

        Designation = get_object_or_404(models.Designation, id=Designation)
        Office = get_object_or_404(models.Office, id=Office)
        UserProfile, created = contact_model.UserProfile.objects.get_or_create(
            email=email, name=name)
        if created:
            UserProfile.branch = Office
            UserProfile.user_role = Designation
            UserProfile.set_password(password)
            UserProfile.save()
        _mutable = request.data._mutable
        request.data._mutable = True
        request.data["employee"] = UserProfile.id
        request.data._mutable = _mutable
        serializer = serializers.EmployeeSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        employee = serializer.save(
            employee=UserProfile, Designation=Designation, Office=Office)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        employee = get_object_or_404(
            models.Employee, id=pk)
        Designation = request.data.get("Designation")
        Office = request.data.get("Office")
        is_active = request.data.get("is_active")
        name = request.data.get("name")
        UserProfile = get_object_or_404(
            contact_model.UserProfile, id=employee.employee.id)

        Designation = get_object_or_404(models.Designation, id=Designation)
        Office = get_object_or_404(models.Office, id=Office)
        UserProfile.name = name
        if request.data.get("password"):
            UserProfile.set_password(request.data.get("password"))
        if is_active == "false":
            UserProfile.is_active = False
        else:
            UserProfile.is_active = True
        UserProfile.branch = Office
        UserProfile.user_role = Designation
        UserProfile.save()
        _mutable = request.data._mutable
        request.data._mutable = True
        request.data["employee"] = UserProfile.id
        request.data._mutable = _mutable
        serializer = serializers.EmployeeSerializer(
            instance=employee, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        employee = serializer.save(
            Designation=Designation, Office=Office)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeDocumentSerializer
    queryset = models.EmployeeDocument.objects.all()
    filterset_fields = ('employee__id', 'employee__employee__name')


class IncreamentPolicyViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.IncreamentPolicySerializer
    queryset = models.IncreamentPolicy.objects.all()


class PermissionFilter(django_filters.FilterSet):

    class Meta:
        model = models.Permission
        fields = ['id', 'Designation__id']


class PermissionViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.PermissionSerializer
    queryset = models.Permission.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = PermissionFilter


class LeaveTypeViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.LeaveTypeSerializer
    queryset = models.LeaveType.objects.all()


class EmployeeLeaveFilter(django_filters.FilterSet):
    month = django_filters.NumberFilter(
        method='filter_by_month', lookup_expr='month')
    year = django_filters.NumberFilter(
        method='filter_by_year', lookup_expr='year')
    start_date = django_filters.DateFilter(
        field_name="leaveStart", lookup_expr="gte")
    end_date = django_filters.DateFilter(
        field_name="leaveEnd", lookup_expr="lte")

    class Meta:
        model = models.EmployeeLeave
        fields = ['employee__id', 'employee__name',
                  'leaveStatus', 'month', 'year', 'start_date', 'end_date']

    def filter_by_month(self, queryset, name, value):
        return queryset.filter(
            Q(leaveStart__month=value) | Q(leaveEnd__month=value)
        )

    def filter_by_year(self, queryset, name, value):
        return queryset.filter(
            Q(leaveStart__year=value) | Q(leaveEnd__year=value)
        )


class EmployeeLeaveViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeLeaveSerializer
    queryset = models.EmployeeLeave.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = EmployeeLeaveFilter

    def create(self, request, *args, **kwargs):
        employee = request.data.get("employee")
        employee = get_object_or_404(models.Employee, id=employee)

        leaveType = request.data.get("leaveType")
        leaveType = get_object_or_404(models.LeaveType, id=leaveType)

        serialized = serializers.EmployeeLeaveSerializer(data=request.data)
        if serialized.is_valid():
            employeeLeave = serialized.save(
                employee=employee, leaveType=leaveType)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        EmployeeLeave = get_object_or_404(models.EmployeeLeave, id=pk)
        employee = request.data.get("employee_id")
        employee = get_object_or_404(models.Employee, id=employee)
        # if not request.user.has_perm('hrm.change_employeeleave'):
        # return Response("Permission Denied", status=status.HTTP_401_UNAUTHORIZED)

        leaveType = request.data.get("leaveType_id")
        leaveType = get_object_or_404(models.LeaveType, id=leaveType)

        serialized = serializers.EmployeeLeaveSerializer(
            instance=EmployeeLeave, data=request.data)
        if serialized.is_valid():
            employeeLeave = serialized.save(
                employee=employee, leaveType=leaveType)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeAttendanceFilter(django_filters.FilterSet):
    month = django_filters.NumberFilter(
        method='filter_by_month', lookup_expr='month')
    year = django_filters.NumberFilter(
        method='filter_by_year', lookup_expr='year')
    start_date = django_filters.DateFilter(
        field_name="attendanceDate", lookup_expr="gte")
    end_date = django_filters.DateFilter(
        field_name="attendanceDate", lookup_expr="lte")

    o = OrderingFilter(
        fields=(
            ('id', 'id'),
            ('attendanceDate', 'attendanceDate'),
            # and any model field you want to sort based on
        )
    )

    class Meta:
        model = models.Attendance
        fields = ['employee__id', 'attendanceDate', 'shift',
                  'employee__Office__id', 'month', 'year', "start_date", "end_date"]

    def filter_by_month(self, queryset, name, value):
        return queryset.filter(
            Q(attendanceDate__month=value)
        )

    def filter_by_year(self, queryset, name, value):
        return queryset.filter(
            Q(attendanceDate__year=value)
        )


class AttendanceViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.AttendanceSerializer
    queryset = models.Attendance.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = EmployeeAttendanceFilter

    def create(self, request, *args, **kwargs):
        employee = request.data.get("id")
        date = request.data.get("attendanceDate")
        shift = request.data.get("shift")
        employee = get_object_or_404(models.Employee, id=employee)
        attendance, _ = models.Attendance.objects.get_or_create(
            attendanceDate=date, employee=employee, shift=shift)
        print(attendance)
        serialized = serializers.AttendanceSerializer(
            instance=attendance, data=request.data)
        if serialized.is_valid():
            attendance = serialized.save(employee=employee)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeSalarySerializer
    queryset = models.Salary.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('employee__id', 'employee__employee__name')

    def create(self, request, *args, **kwargs):
        employee = request.data.get("employee")
        employee = get_object_or_404(models.Employee, id=employee)
        salary, _ = models.Salary.objects.get_or_create(employee=employee)

        serialized = serializers.EmployeeSalarySerializer(
            instance=salary, data=request.data)
        if serialized.is_valid():
            employeeSalary = serialized.save(employee=employee)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeSalaryPaymentViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeSalaryPaymentSerializer
    queryset = models.SalaryPayment.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('employee__id', 'employee__name')

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get("employee")
        employee = get_object_or_404(models.Employee, id=employee_id)
        month = request.data.get("salaryMonth")
        year = request.data.get("salaryYear")
        salary_payment, _ = models.SalaryPayment.objects.get_or_create(
            employee=employee, salaryMonth=month, salaryYear=year)
        serialized = serializers.EmployeeSalaryPaymentSerializer(
            instance=salary_payment, data=request.data)
        serialized.is_valid(raise_exception=True)
        employeeSalary = serialized.save(employee=employee)
        return Response(serialized.data, status=status.HTTP_201_CREATED)


class EmployeeLoanViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeLoanSerializer
    queryset = models.Loan.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('employee__id', 'employee__employee__name',
                        'loanStatus', 'loanPaymentStatus')

    def create(self, request, *args, **kwargs):
        employee = request.data.get("employee")
        employee = get_object_or_404(models.Employee, id=employee)

        serialized = serializers.EmployeeLoanSerializer(data=request.data)
        if serialized.is_valid():
            employeeLoan = serialized.save(employee=employee)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        Loan = get_object_or_404(models.Loan, id=pk)
        employee = request.data.get("employee_id")
        loanStatus = request.data.get("loanStatus")
        employee = get_object_or_404(models.Employee, id=employee)
        serialized = serializers.EmployeeLoanSerializer(
            instance=Loan, data=request.data)
        if serialized.is_valid():
            employeeLoan = serialized.save(employee=employee)
            if loanStatus == 'paid':
                employeeLoan.loanPaymentStatus = 'ongoing'
                employeeLoan.save()
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeLoanPaymentViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeLoanPaymentSerializer
    queryset = models.LoanPayment.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('employee__id', 'employee__employee__name', 'loan__id')

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get("employee")
        employee = get_object_or_404(models.Employee, id=employee_id)
        month = request.data.get("salaryMonth")
        year = request.data.get("salaryYear")
        loan_id = request.data.get("loan")
        loan = get_object_or_404(models.Loan, id=loan_id)
        employeeLoanPayment = models.LoanPayment.objects.filter(
            employee=employee, loan=loan)
        total_paid = 0
        for payment in employeeLoanPayment:
            total_paid = total_paid + payment.paidAmount
        due_payment = int(loan.loanAmount) - int(total_paid)
        paidAmount = request.data.get("paidAmount")
        if due_payment == paidAmount:
            loan.loanPaymentStatus = 'finished'
        loan.save()
        loan_payment, _ = models.LoanPayment.objects.get_or_create(
            employee=employee, loan=loan, paymentDate__month=month, paymentDate__year=year)

        serialized = serializers.EmployeeLoanPaymentSerializer(
            instance=loan_payment, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(employee=employee, loan=loan)
        return Response(serialized.data, status=status.HTTP_201_CREATED)


class PayslipFilter(django_filters.FilterSet):

    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    fromMonth = django_filters.CharFilter(
        method='filter_from_month', label='From Year-Month')

    toMonth = django_filters.CharFilter(
        method='filter_to_month', label='To Year-Month')

    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.PaySlip
        fields = ['start', 'end', 'employee__id', 'employee__employee__name', 'salaryMonth', 'salaryYear',
                  'payment_method_1__id', 'payment_method_2__id', ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(net_salary__contains=value))

    def filter_from_month(self, queryset, name, value):
        # print(value)
        [yyyy, mm] = value.split('-')
        return queryset.filter(salaryMonth__gte=mm, salaryYear__gte=yyyy)

    def filter_to_month(self, queryset, name, value):
        [yyyy, mm] = value.split('-')
        return queryset.filter(salaryMonth__lte=mm, salaryYear__lte=yyyy)


class PaySlipViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.PaySlipSerializer
    queryset = models.PaySlip.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = PayslipFilter

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get("employee")
        employee = get_object_or_404(models.Employee, id=employee_id)
        salary_id = request.data.get("salary")
        salary = get_object_or_404(models.Salary, id=salary_id)
        month = request.data.get("salaryMonth")
        year = request.data.get("salaryYear")
        pay_slip, _ = models.PaySlip.objects.get_or_create(
            employee=employee, salary=salary, salaryMonth=month, salaryYear=year)
        serialized = serializers.PaySlipSerializer(
            instance=pay_slip, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(employee=employee, salary=salary)
        return Response(serialized.data, status=status.HTTP_201_CREATED)
