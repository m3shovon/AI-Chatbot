from django.db import models
from django.conf import settings
import barcode
import uuid
import os
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from django.db.models import JSONField
from django.utils.text import slugify


class business_settings(models.Model):
    """Database model for Attribute"""
    logo = models.ImageField(upload_to='business/logo', null=True, blank=True)
    signature = models.ImageField(
        upload_to='business/signature', null=True, blank=True)
    wordrobe_terms = models.TextField(null=True, blank=True)
    invoice_terms = models.TextField(null=True, blank=True)
    challan_terms = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    data = JSONField(null=True, blank=True)


class module(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        """return string representation of our user"""
        return self.name


class sub_module(models.Model):
    name = models.CharField(max_length=255, unique=True)
    module = models.ForeignKey(
        module, on_delete=models.CASCADE, default=None, blank=True, null=True)
    permission = models.TextField(null=True, blank=True)

    def __str__(self):
        """return string representation of our user"""
        return self.module.name + ' - ' + self.name
