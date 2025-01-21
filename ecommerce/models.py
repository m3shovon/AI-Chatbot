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
from image_optimizer.fields import OptimizedImageField


class page(models.Model):
    """Database model for Attribute"""
    name = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    slug = models.TextField(null=True, blank=True)
    meta_title = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    is_campaign_page = models.BooleanField(default=False)
    
    def __str__(self):
        """return string representation"""
        return self.name
    

class image(models.Model):
    """Database model for Attribute"""
    image = models.ImageField(
        upload_to='ecommerce', null=True, blank=True)
    thumbnail = OptimizedImageField(
        null=True,
        blank=True,
        upload_to='ecommerce',
        optimized_image_output_size=(120, 120),
        optimized_image_resize_method="cover"  #  "crop", "cover", "contain", "width", "height", "thumbnail" or None
    )
    alt = models.TextField(null=True, blank=True)
    
    
class feature(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255,null=True, blank=True)
    page = models.ForeignKey(
        page, on_delete=models.CASCADE, default=None, blank=True, null=True)
    is_slider = models.BooleanField(default=False)

    def __str__(self):
        """return string representation"""
        return self.page.name + ' - ' + self.name


class feature_item(models.Model):
    feature = models.ForeignKey(
        feature, on_delete=models.CASCADE, default=None, blank=True, null=True)
    image = models.ForeignKey(
        image, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    title = models.TextField(null=True, blank=True)
    sub_title = models.TextField(null=True, blank=True)
    button_name = models.CharField(max_length=255, null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    alt = models.TextField(null=True, blank=True)
    href = models.TextField(null=True, blank=True)

    def __str__(self):
        """return string representation"""
        return self.feature.name + ' - ' + self.title