import django_filters
from django.contrib.auth.models import Group
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from contact import serializers, models, permissions
import product.models as product_models
from django.contrib.admin.models import LogEntry
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Permission
import django_filters
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token

# Create your views here.
from contact.models import EmployeeProfile, UserProfile
from contact.serializers import EmployeeProfileSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100000000


class UserProfileViewSet(viewsets.ModelViewSet):
    """Handel creating and updating users"""
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email',)


class EmployeeFilter(django_filters.FilterSet):
    shift = django_filters.CharFilter(
        method='filter_by_shift', lookup_expr='month')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.UserProfile
        fields = ['id', 'name', 'branch__id', 'shift', 'keyward', 'is_active']

    def filter_by_shift(self, queryset, name, value):
        return queryset.filter(
            Q(employee__defaultShift=value)
        )

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(name__contains=value) | Q(email__contains=value))


class EmployeeViewSet(viewsets.ModelViewSet):
    """Handle creating and updating users"""
    serializer_class = serializers.EmployeeSerializer
    queryset = models.UserProfile.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.UpdateOwnProfile,
    #                       permissions.CustomDjangoModelPermissions,)
    filter_backends = [DjangoFilterBackend]
    filter_class = EmployeeFilter
    # filterset_fields = ('id', 'name', 'branch__id', 'employeeprofile__defaultShift')

    def create(self, request, *args, **kwargs):
        user_role = request.data.get("user_role")
        user_role = get_object_or_404(models.userRole, id=user_role)
        branch = request.data.get("branch")
        branch = get_object_or_404(product_models.Warehouse, id=branch)
        serializer = serializers.EmployeeSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        employee = serializer.save(user_role=user_role, branch=branch, is_active=True)
        group = Group.objects.get(id=user_role.id)
        group.user_set.add(employee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        employee = get_object_or_404(models.UserProfile, id=pk)
        new_user_role = request.data.get("user_role")
        new_user_role = get_object_or_404(models.userRole, id=new_user_role)
        branch = request.data.get("branch")
        branch = get_object_or_404(product_models.Warehouse, id=branch)
        if employee.user_role:
            old_group = Group.objects.get(id=employee.user_role.id)
            old_group.user_set.remove(employee)
        group = Group.objects.get(id=new_user_role.id)
        group.user_set.add(employee)
        serializer = serializers.EmployeeSerializer(
            instance=employee, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        employee = serializer.save(user_role=new_user_role, branch=branch)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        employee = get_object_or_404(models.UserProfile, id=pk)
        serializer = serializers.EmployeeSerializer(employee)
        permission_list = employee.get_all_permissions()
        return Response({"permissions_list": permission_list, "data": serializer.data}, status=status.HTTP_201_CREATED)


class UserLoginApiView(ObtainAuthToken):
    """Handle creating user authentication tokens"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        all_permissions_in_groups = user.get_group_permissions()
        employeeProfile = EmployeeProfile.objects.get(employee=user)
        employee_serializer = serializers.EmployeeLoginSerializer(user)
        # print(all_permissions_in_groups)

        return Response(
            {
                "token": token.key,
                "id": user.pk,
                "name": user.name,
                "email": user.email,
                "phone": employeeProfile.phone,
                "superuser": user.is_superuser,
                "staff": user.is_staff,
                "profile": employee_serializer.data,
                "is_authenticated": True,
                # "permissions": None if user.is_superuser else all_permissions_in_groups
                "permissions": employee_serializer.data["user_role"]["approved_permissions_list"]
            }
        )


class ContactTypeViewSet(viewsets.ModelViewSet):
    """Handel creating and updating users"""
    serializer_class = serializers.ContactTypeSerializer
    queryset = models.ContactType.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('Type',)


class ContactFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')

    class Meta:
        model = models.contact
        fields = ['name', 'email', 'phone', 'Type', 'keyward', 'role','start','end']

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(email__icontains=value) | Q(phone__icontains=value))


class ContactView(viewsets.ModelViewSet):
    """Hanfel creating and updating contacts"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.contactSerializer
    queryset = models.contact.objects.all().order_by('-id')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email', 'phone', 'Type')
    filter_backends = [DjangoFilterBackend]
    filter_class = ContactFilter

    def create(self, request, *args, **kwargs):
        contact_type = request.data.get("Type")
        phone = request.data.get("phone")
        role = request.data.get("role")
        print(request.data)
        roleName = ""
        if role:
            contact = models.ContactType.objects.filter(id=role).first()
            roleName = contact.name
        else:
            roleName = request.data.get("roleName")

        if roleName == "" or roleName == None or roleName == "None":
            new_contact, created = models.contact.objects.get_or_create(
                Type=contact_type, phone=phone)
            serialized = serializers.contactSerializer(
                instance=new_contact, data=request.data)
            serialized.is_valid(raise_exception=True)
            serialized.save()
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            new_role, role_created = models.ContactType.objects.get_or_create(
                name=roleName, Type=contact_type)
            new_contact, created = models.contact.objects.get_or_create(
                Type=contact_type, phone=phone)
            serialized = serializers.contactSerializer(
                instance=new_contact, data=request.data)
            serialized.is_valid(raise_exception=True)
            serialized.save(role=new_role)
            return Response(serialized.data, status=status.HTTP_201_CREATED)


class ContactViewP(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.contactSerializer
    queryset = models.contact.objects.all().order_by('-id')
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name', 'email', 'phone', 'Type')
    filter_backends = [DjangoFilterBackend]
    filter_class = ContactFilter
    pagination_class = StandardResultsSetPagination
    
    
class UserLog(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.userlog
    queryset = LogEntry.objects.all()


class userRoleViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.userRoleSerializer
    queryset = models.userRole.objects.all()

    def create(self, request, *args, **kwargs):
        group_name = request.data.get("name")
        department = request.data.get("department")
        department = get_object_or_404(models.Department, id=department)
        new_group, created = Group.objects.get_or_create(name=group_name)
        serialized = serializers.userRoleSerializer(data=request.data)
        if serialized.is_valid():
            user_role = serialized.save(department=department)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        user_role = get_object_or_404(models.userRole, id=pk)
        group_name = request.data.get("name")
        department = request.data.get("department")
        department = get_object_or_404(models.Department, id=department)
        old_group = Group.objects.get(name=user_role.name)
        old_group.name = group_name
        old_group.save()

        serialized = serializers.userRoleSerializer(
            instance=user_role, data=request.data)
        if serialized.is_valid():
            user_role = serialized.save(department=department)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class role_permissionFilter(django_filters.FilterSet):
    # keyward = django_filters.CharFilter(
    #     method='filter_by_keyward', lookup_expr='icontains')
    class Meta:
        model = models.role_permission
        fields = ['user_role__id']
    # def filter_by_keyward(self, queryset, name, value):
    #     return queryset.filter(Q(name__contains=value) | Q(email__contains=value) | Q(phone__contains=value))


class role_permissionViewSet(viewsets.ModelViewSet):
    """Handel creating and updating users"""
    serializer_class = serializers.role_permissionSerializer
    queryset = models.role_permission.objects.all()
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = role_permissionFilter


class DepartmentViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.DepartmentSerializer
    queryset = models.Department.objects.all()


class EmployeeProfileViewSet(viewsets.ViewSet):
    """
    Example empty viewset demonstrating the standard
    actions that will be handled by a router class.

    If you're using format suffixes, make sure to also include
    the `format=None` keyword argument for each action.
    """
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeProfileSerializer

    def get_permissions(self):
        if self.action in ['update']:
            self.permission_classes = [permissions.IsOwnerOrAdmin, ]
        elif self.action in ['destroy']:
            self.permission_classes = [IsAdminUser, ]
        elif self.action in ['retrieve', 'list']:
            self.permission_classes = [IsAuthenticatedOrReadOnly, ]
        return super().get_permissions()

    def list(self, request):
        queryset = EmployeeProfile.objects.all()
        serializer_class = EmployeeProfileSerializer(queryset, many=True)
        return Response(serializer_class.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(EmployeeProfile, id=pk)
        serializer = EmployeeProfileSerializer(user)
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = get_object_or_404(EmployeeProfile, id=pk)
        is_active = request.data.get("is_active")
        if is_active == "false":
            user.employee.is_active = False
            try:
                user.employee.auth_token.delete()
            except:
                print("no auth token")
        else:
            user.employee.is_active = True
        try:
            user.employee.save()
        except e:
            print("Error saving")
        serializer = EmployeeProfileSerializer(
            instance=user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        user = UserProfile.objects.get(id=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.CustomDjangoModelPermissions, )
    serializer_class = serializers.EmployeeDocumentSerializer
    queryset = models.EmployeeDocument.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('employee__id', 'employee__name')

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get("employee")
        employee = get_object_or_404(models.UserProfile, id=employee_id)
        serialized = serializers.EmployeeDocumentSerializer(data=request.data)
        serialized.is_valid(raise_exception=True)
        document = serialized.save(employee=employee)
        return Response(serialized.data, status=status.HTTP_201_CREATED)
