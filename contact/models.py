from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, BaseUserManager
from django.conf import settings
from django.utils import timezone
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
# from hrm import models as hrm_models
from software_settings import models as settings_models


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


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database model for users in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    user_role = models.ForeignKey(
        'hrm.Designation', on_delete=models.CASCADE, default=None, blank=True, null=True)
    branch = models.ForeignKey(
        'hrm.Office', on_delete=models.CASCADE, default=None, blank=True, null=True)

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


# @receiver(post_save, sender=UserProfile)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         hrm_models.EmployeeProfile.objects.create(employee=instance)


# @receiver(post_save, sender=UserProfile)
# def save_user_profile(sender, instance, **kwargs):
#     instance.employee.save()


class ContactType(models.Model):
    Type = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    cupon_name = models.CharField(max_length=255, null=True, blank=True)


class contact(models.Model):
    """Database model for Contact information"""
    name = models.CharField(max_length=255, null=True, blank=True)
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
    data = JSONField(null=True, blank=True)
