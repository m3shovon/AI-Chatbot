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
from contact.serializers import EmployeeProfileSerializer
from hrm import serializers, models
from contact import models as contact_model
from contact import serializers as contact_serializer
from django.db.models import Q
from contact import permissions
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100000000


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
    start = django_filters.IsoDateTimeFilter(
        field_name="leaveStart", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="leaveStart", lookup_expr='lte')
    keyword = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.EmployeeLeave
        fields = ['employee__id', 'employee__name','start', 'end','keyword',
                  'leaveStatus', 'month', 'year', 'start_date', 'end_date']

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter( Q(employee__name__icontains=value) | Q(employee__email__icontains=value) | Q(employee__id__icontains=value))
    
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
        employee = get_object_or_404(contact_model.UserProfile, id=employee)

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
        employee = get_object_or_404(contact_model.UserProfile, id=employee)
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

class EmployeeLeavePViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeLeaveSerializer
    queryset = models.EmployeeLeave.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = EmployeeLeaveFilter
    pagination_class = StandardResultsSetPagination
    
    
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
                  'employee__branch__id', 'month', 'year', "start_date", "end_date"]

    def filter_by_month(self, queryset, name, value):
        return queryset.filter(
            Q(attendanceDate__month=value)
        )

    def filter_by_year(self, queryset, name, value):
        return queryset.filter(
            Q(attendanceDate__year=value)
        )

class EmployeeAttendanceReportFilter(django_filters.FilterSet):
    start_date = django_filters.IsoDateTimeFilter(
        field_name="attendanceDate", lookup_expr="gte")
    end_date = django_filters.IsoDateTimeFilter(
        field_name="attendanceDate", lookup_expr="lte")
    
    class Meta:
        model = models.Attendance
        fields = ['employee__id', 'attendanceDate', 'shift',
                  'employee__branch__id', "start_date", "end_date"]

   


class AttendanceReportViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.AttendanceReportSerializer
    queryset = models.Attendance.objects.all().order_by('attendanceDate')
    filter_backends = [DjangoFilterBackend]
    filter_class = EmployeeAttendanceReportFilter

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
        employee = get_object_or_404(contact_model.UserProfile, id=employee)
        attendance, _ = models.Attendance.objects.get_or_create(
            attendanceDate=date, employee=employee, shift=shift)

        serialized = serializers.AttendanceSerializer(
            instance=attendance, data=request.data)
        if serialized.is_valid():
            attendance = serialized.save(employee=employee)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

class SalaryFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.Salary
        fields = ['employee__id', 'employee__name','keyword']

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter( Q(employee__id__icontains=value) | Q(employee__name__icontains=value))
    

class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeSalarySerializer
    queryset = models.Salary.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = SalaryFilter

    def create(self, request, *args, **kwargs):
        employee = request.data.get("employee")
        employee = get_object_or_404(contact_model.UserProfile, id=employee)
        salary, _ = models.Salary.objects.get_or_create(employee=employee)

        serialized = serializers.EmployeeSalarySerializer(
            instance=salary, data=request.data)
        if serialized.is_valid():
            employeeSalary = serialized.save(employee=employee)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)



        
class EmployeeSalaryPViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeSalarySerializer
    queryset = models.Salary.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = SalaryFilter
    pagination_class = StandardResultsSetPagination

class EmployeeSalaryPaymentViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeSalaryPaymentSerializer
    queryset = models.SalaryPayment.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('employee__id', 'employee__name')

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get("employee")
        employee = get_object_or_404(contact_model.UserProfile, id=employee_id)
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
    queryset = models.Loan.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('employee__id', 'employee__name',
                        'loanStatus', 'loanPaymentStatus')

    def create(self, request, *args, **kwargs):
        employee = request.data.get("employee")
        employee = get_object_or_404(contact_model.UserProfile, id=employee)

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
        employee = get_object_or_404(contact_model.UserProfile, id=employee)
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


class EmployeeloanFilter(django_filters.FilterSet):
    
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    
    class Meta:
        model = models.Loan
        fields = ['employee__id', 'employee__name','loanType', 'keyward',
                    'loanStatus', 'loanPaymentStatus']
        
    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(employee__name__icontains=value) | Q(employee__id__icontains=value))


class EmployeeLoanPaginationViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeLoanSerializer
    queryset = models.Loan.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = EmployeeloanFilter
    pagination_class = StandardResultsSetPagination


class EmployeeLoanPaymentViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeLoanPaymentSerializer
    queryset = models.LoanPayment.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('employee__id', 'employee__name', 'loan__id')

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get("employee")
        employee = get_object_or_404(contact_model.UserProfile, id=employee_id)
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
        loan_payment = models.LoanPayment.objects.create(
            employee=employee, loan=loan)

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

    fromMonth = django_filters.CharFilter (
        method='filter_from_month', label='From Year-Month')

    toMonth = django_filters.CharFilter(
        method='filter_to_month', label='To Year-Month')

    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.PaySlip
        fields = ['start', 'end', 'employee__id', 'employee__name', 'salaryMonth', 'salaryYear',
         'payment_method_1__id', 'payment_method_2__id',]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(net_salary__contains=value))

    def filter_from_month(self, queryset, name, value):
        # print(value)
        [yyyy,mm] = value.split('-')
        return queryset.filter(salaryMonth__gte=mm, salaryYear__gte=yyyy)

    def filter_to_month(self, queryset, name, value):
        [yyyy,mm] = value.split('-')
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
        employee = get_object_or_404(contact_model.UserProfile, id=employee_id)
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
