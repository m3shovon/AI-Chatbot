from rest_framework import serializers
from contact import models
from django.contrib.admin.models import LogEntry
from product.serializers import warehouseSerilizer
from django.contrib.auth.models import Group
from software_settings import models as settings_models
from software_settings import serializers as settings_Serializer
from hrm import serializers as hrm_Serializer


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """serlizers a user profile object"""

    # data = JSONSerializerField()

    class Meta:
        model = models.UserProfile
        fields = ('id', 'email', 'name', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        """create and return a new user"""
        user = models.UserProfile.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )

        return user


# class userRoleSerializer(serializers.ModelSerializer):
#     Designation = hrm_Serializer.DesignationSerializer(read_only=True)

#     class Meta:
#         model = userRole
#         fields = '__all__'

#     def to_representation(self, instance):
#         response = super().to_representation(instance)
#         response["title"] = instance.Designation.name
#         response["key"] = instance.id
#         response["value"] = instance.id
#         # response["departmentName"] = instance.Department.name
#         # response["location_name"] = instance.department.location.name
#         # try:
#         #     group = Group.objects.get(name=instance.name)
#         #     # print(group.user_set.all().first())
#         #     permission_list = group.user_set.all().first().get_group_permissions()
#         #     response["approved_permissions_list"] = permission_list
#         # except Exception:
#         #     pass

#         permissions = role_permission.objects.filter(
#             user_role=instance.id)
#         permissions_response = []
#         for i in permissions:
#             data = role_permissionSerializer(i).data
#             if i.is_create:
#                 res = data["Module"] + "." + data["Sub_Module"] + "_is_create"
#                 permissions_response.append(res)
#             if i.is_read:
#                 res = data["Module"] + "." + data["Sub_Module"] + "_is_read"
#                 permissions_response.append(res)
#             if i.is_update:
#                 res = data["Module"] + "." + data["Sub_Module"] + "_is_update"
#                 permissions_response.append(res)
#             if i.is_delete:
#                 res = data["Module"] + "." + data["Sub_Module"] + "_is_delete"
#                 permissions_response.append(res)
#         response["approved_permissions_list"] = permissions_response
#         return response


# class userRoleWithoutPermissionsSerializer(serializers.ModelSerializer):
#     Designation = hrm_Serializer.DesignationSerializer(read_only=True)

#     class Meta:
#         model = userRole
#         fields = '__all__'

#     def to_representation(self, instance):
#         response = super().to_representation(instance)
#         response["title"] = instance.name
#         response["key"] = instance.id
#         response["value"] = instance.id
#         # response["departmentName"] = instance.department.name
#         return response


# class EmployeeSerializer(serializers.ModelSerializer):
#     """serlizers a user profile object"""

#     # data = JSONSerializerField()
#     user_role = userRoleSerializer(read_only=True)
#     branch = warehouseSerilizer(read_only=True)
#     password = serializers.CharField(
#         write_only=True,
#         required=False,
#         help_text='Leave empty if no change needed',
#         style={'input_type': 'password', 'placeholder': 'Password'}
#     )

#     class Meta:
#         model = models.UserProfile
#         fields = ('id', 'email', 'name', 'password', 'user_role', 'branch')

#     def create(self, validated_data):
#         """create and return a new user"""
#         # print(validated_data)
#         user = models.UserProfile.objects.create_user(
#             email=validated_data['email'],
#             name=validated_data['name']
#         )
#         user.set_password(validated_data['password'])
#         user.user_role = validated_data['user_role']
#         # user.branch = validated_data['branch']

#         user.save()
#         return user

#     def update(self, instance, validated_data):
#         if 'password' in validated_data:
#             password = validated_data.pop('password')
#             if password == "" or password is None:
#                 pass
#             else:
#                 instance.set_password(password)
#         return super(EmployeeSerializer, self).update(instance, validated_data)

#     def to_representation(self, instance):
#         response = super().to_representation(instance)
#         try:
#             employeeProfile = EmployeeProfile.objects.get(employee=instance)
#             url = None
#             request = self.context.get('request', None)
#             if employeeProfile.photo.name and request:
#                 url = request.build_absolute_uri(employeeProfile.photo.url)

#             if employeeProfile:
#                 response["phone"] = employeeProfile.phone
#                 response["emergency_phone"] = employeeProfile.emergency_phone
#                 response["address"] = employeeProfile.address
#                 response["defaultShift"] = employeeProfile.defaultShift
#                 response["defaultEntryTime"] = employeeProfile.defaultEntryTime
#                 response["defaultExitTime"] = employeeProfile.defaultExitTime
#                 response["profile_id"] = employeeProfile.id
#             if instance.user_role:
#                 response["user_roleName"] = instance.user_role.name
#                 response["employeeDepartment"] = instance.user_role.department.name
#             if instance.branch:
#                 response["branchName"] = instance.branch.name
#             if url:
#                 response["photo"] = url
#             response["title"] = instance.name
#             response["key"] = instance.id
#             response["value"] = instance.id
#             employeeDocuments = EmployeeDocument.objects.filter(
#                 employee=instance)
#             files = []
#             for document in employeeDocuments:
#                 url = None
#                 request = self.context.get('request', None)
#                 if document.file.name and request:
#                     name = document.file.name
#                     url = request.build_absolute_uri(document.file.url)
#                     files.append({'id': document.id, 'name': name, 'url': url})

#             response["files"] = files
#         except EmployeeProfile.DoesNotExist:
#             print("Profile Information Not Found For: " + instance.name)

#         return response


# class EmployeeWithoutpermissionSerializer(serializers.ModelSerializer):
#     """serlizers a user profile object"""

#     # data = JSONSerializerField()
#     user_role = userRoleWithoutPermissionsSerializer(read_only=True)
#     branch = warehouseSerilizer(read_only=True)
#     password = serializers.CharField(
#         write_only=True,
#         required=False,
#         help_text='Leave empty if no change needed',
#         style={'input_type': 'password', 'placeholder': 'Password'}
#     )

#     class Meta:
#         model = models.UserProfile
#         fields = ('id', 'email', 'name', 'password', 'user_role', 'branch')

#     def to_representation(self, instance):
#         response = super().to_representation(instance)
#         try:
#             employeeProfile = EmployeeProfile.objects.get(employee=instance)

#             if employeeProfile:
#                 response["phone"] = employeeProfile.phone
#                 response["emergency_phone"] = employeeProfile.emergency_phone
#                 response["address"] = employeeProfile.address
#                 response["defaultShift"] = employeeProfile.defaultShift
#                 response["defaultEntryTime"] = employeeProfile.defaultEntryTime
#                 response["defaultExitTime"] = employeeProfile.defaultExitTime
#                 response["profile_id"] = employeeProfile.id
#             if instance.user_role:
#                 response["user_roleName"] = instance.user_role.name
#                 response["employeeDepartment"] = instance.user_role.department.name
#             if instance.branch:
#                 response["branchName"] = instance.branch.name

#             response["title"] = instance.name
#             response["key"] = instance.id
#             response["value"] = instance.id
#             employeeDocuments = EmployeeDocument.objects.filter(
#                 employee=instance)
#             files = []

#         except EmployeeProfile.DoesNotExist:
#             print("Profile Information Not Found For: " + instance.name)

#         return response


# class EmployeeProfileSerializer(serializers.ModelSerializer):
#     employee = EmployeeSerializer(read_only=True)

#     class Meta:
#         model = EmployeeProfile
#         fields = '__all__'

#     def to_representation(self, instance):
#         response = super().to_representation(instance)

#         url = None
#         request = self.context.get('request', None)
#         if instance.photo.name and request:
#             url = request.build_absolute_uri(instance.photo.url)

#         response["name"] = instance.employee.name
#         response["email"] = instance.employee.email
#         response["photo"] = url
#         response["user_roleName"] = instance.employee.user_role.name
#         response["employeeDepartment"] = instance.employee.user_role.department.name
#         employeeDocuments = EmployeeDocument.objects.filter(
#             employee=instance.employee)
#         files = []
#         for document in employeeDocuments:
#             url = None
#             request = self.context.get('request', None)
#             if document.file.name and request:
#                 name = document.file.name
#                 url = request.build_absolute_uri(document.file.url)
#                 files.append({'id': document.id, 'name': name, 'url': url})

#         response["files"] = files
#         return response


# class EmployeeDocumentSerializer(serializers.ModelSerializer):
#     employee = EmployeeSerializer(read_only=True)

#     class Meta:
#         model = EmployeeDocument
#         fields = '__all__'

#     def to_representation(self, instance):
#         response = super().to_representation(instance)

#         url = None
#         request = self.context.get('request', None)
#         if instance.file.name and request:
#             url = request.build_absolute_uri(instance.file.url)

#         response["name"] = instance.employee.name
#         response["email"] = instance.employee.email
#         response["file"] = url
#         response["user_roleName"] = instance.employee.user_role.name
#         return response


class contactSerializer(serializers.ModelSerializer):
    """serlizers a contact object"""
    data = JSONSerializerField()

    class Meta:
        model = models.contact
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.name:
            response['title'] = instance.name
        if instance.role:
            role = models.ContactType.objects.filter(
                id=instance.role.id)
            contacttype_response = []
            for i in role:
                contacttype_response.append(
                    ContactTypeSerializer(i).data)
            response["Role"] = contacttype_response[0]['name']
            response["Cupon"] = contacttype_response[0]['cupon_name']
        response['key'] = instance.id
        response['value'] = instance.id
        # response['response'] = response

        return response


class ContactTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactType
        fields = '__all__'


class userlog(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = LogEntry
        fields = '__all__'
