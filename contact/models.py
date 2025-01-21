from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, BaseUserManager
from django.conf import settings
from django.utils import timezone
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from software_settings import models as settings_models
# from product import models as productModel

class UserProfileManager(BaseUserManager):
    """Manager for user profiles"""

    def create_user(self, email, name, password=None):
        """Create a new user profile"""
        if not email:
            raise ValueError('User must have a email address')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        """create and save a super user"""
        user = self.create_user(email, name, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user

    # def save(self, commit=True):
    #     # Save the provided password in hashed format
    #     user = super(self).save(commit=False)
    #     print(user)
    #     user.set_password(self.cleaned_data["password"])
    #     if commit:
    #         user.save()
    #     return user


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        """return string representation of our user"""
        return self.name


class userRole(models.Model):
    name = models.CharField(max_length=255, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, default=None, blank=True, null=True)

    def __str__(self):
        """return string representation of our user"""
        return self.name


class role_permission(models.Model):
    user_role = models.ForeignKey(
        userRole, on_delete=models.CASCADE, default=None, blank=True, null=True)
    module = models.ForeignKey(
        settings_models.module, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    sub_module = models.ForeignKey(
        settings_models.sub_module, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    is_create = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_update = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_location = models.BooleanField(default=False)

    def __str__(self):
        """return string representation of our user"""
        return self.user_role.name + ' - ' + self.sub_module.name


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database model for users in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    user_role = models.ForeignKey(
        userRole, on_delete=models.CASCADE, default=None, blank=True, null=True)
    branch = models.ForeignKey(
        'product.Warehouse', on_delete=models.CASCADE, default=None, blank=True, null=True)

    objects = UserProfileManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        """Retrive full name of the user"""
        return self.name

    def get_short_name(self):
        """Retrive short name of the user"""
        return self.name

    def __str__(self):
        """return string representation of our user"""
        return self.email

    def save(self, *args, **kwargs):
        if self.pk:
            employee = EmployeeProfile.objects.get(employee=self.id)
            employee.is_active = self.is_active
            employee.save()
        return super().save(*args, **kwargs)


class EmployeeProfile(models.Model):
    employee = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, unique=True, related_name="employee")
    branch = models.ManyToManyField('product.Warehouse',
            blank=True,
            related_name="branch",
            related_query_name="branch",)
    photo = models.ImageField(
        upload_to='employee/photo', null=True, blank=True)
    phone = models.CharField(
        unique=True, max_length=255, null=True, blank=True)
    emergency_phone = models.CharField(
        max_length=255, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    defaultShift = models.CharField(default='day', max_length=255)
    defaultEntryTime = models.TimeField(
        blank=True, null=True, default="10:00:00")
    defaultExitTime = models.TimeField(
        blank=True, null=True, default="20:00:00")
    joining_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    resignation_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """return string representation of our user"""
        return self.employee.email

    def save(self, *args, **kwargs):
        self.is_active = self.employee.is_active
        return super().save(*args, **kwargs)


def user_files_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'employee/files/user_{0}/{1}'.format(instance.employee.id, filename)


class EmployeeDocument(models.Model):
    employee = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="employee_document")
    file = models.FileField(
        upload_to=user_files_directory_path, null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """return string representation of our user"""
        return self.employee.email + ", File: " + self.file.name


@receiver(post_save, sender=UserProfile)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        EmployeeProfile.objects.create(employee=instance)


@receiver(post_save, sender=UserProfile)
def save_user_profile(sender, instance, **kwargs):
    instance.employee.save()


class ContactType(models.Model):
    Type = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        """return string representation of our user"""
        return self.name


class contact(models.Model):
    """Database model for Contact information"""
    name = models.CharField(max_length=255, null=True, blank=True)
    ecommerce_id = models.CharField(max_length=500, null=True, blank=True)
    email = models.CharField(
        max_length=255, null=True, blank=True)
    phone = models.CharField(
        max_length=255, null=True, blank=True)
    emergency_contact = models.CharField(
        max_length=255, null=True, blank=True)
    role = models.ForeignKey(
        "ContactType", on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    Type = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.CharField(max_length=550, null=True, blank=True)
    account_balance = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    points = models.CharField(max_length=550, null=True, blank=True)
    Special_Date_Type = models.CharField(max_length=255, null=True, blank=True)
    special_dates = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    data = JSONField(null=True, blank=True)
    
    def __str__(self):
        details = ""
        if self.id:
            details += str(self.phone)
        if self.name:
            details += ' - '+ str(self.name)
        return details


# class wishlist(models.Model):
#     """Database model for wishlist"""
#     product = models.ForeignKey(
#         productModel.ProductLocation,
#         on_delete=models.CASCADE
#     )
#     contact = models.ForeignKey(
#         contact,
#         on_delete=models.CASCADE
#     )

#     def __str__(self):
#         """return string representation of wishlist"""
#         return self.contact.name
