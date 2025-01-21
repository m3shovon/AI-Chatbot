from django.db import models
from django.conf import settings
from django.utils import timezone
from contact.models import contact
import barcode
import uuid
import os
import json
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from django.db.models import JSONField
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from product.signals import *
from django.dispatch import receiver
from datetime import datetime

# Create your models here.


class Attribute(models.Model):
    """Database model for Attribute"""
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, null=True, blank=True)
    context = models.CharField(max_length=255, blank=True, null=True)
    data = JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.name)
            check = Attribute.objects.filter(slug=self.slug).count()
            if check > 0:
                obj = Attribute.objects.latest('id')
                self.slug = self.slug + "-" + str(obj.id + 1)
        else:
            self.slug = slugify(self.name)
            check = Attribute.objects.filter(slug=self.slug).count()
            if check > 0:
                self.slug = self.slug + "-" + str(self.pk)
        super(Attribute, self).save(*args, **kwargs)

    def __str__(self):
        """return string representation of Attribute"""
        return self.name


class AttributeTerm(models.Model):
    """Database model for AttributeTerm"""
    Attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, null=True, blank=True)
    context = models.CharField(max_length=255, blank=True, null=True)
    data = JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.Attribute.name + " " + self.name)
            check = AttributeTerm.objects.filter(slug=self.slug).count()
            if check > 0:
                obj = AttributeTerm.objects.latest('id')
                self.slug = self.slug + "-" + str(obj.id + 1)
        else:
            self.slug = slugify(self.name)
            check = AttributeTerm.objects.filter(slug=self.slug).count()
            if check > 0:
                self.slug = self.slug + "-" + str(self.pk)
        super(AttributeTerm, self).save(*args, **kwargs)

    def __str__(self):
        """return string representation of Attribute terms"""
        return self.Attribute.name + "  --  " + self.name


class Category(models.Model):
    """Database model for Category"""
    Category_parent = models.ForeignKey('self',
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        blank=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True, null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.name)
            check = Category.objects.filter(slug=self.slug).count()
            if check > 0:
                obj = Category.objects.latest('id')
                self.slug = self.slug + "-" + str(obj.id + 1)
        else:
            self.slug = slugify(self.name)
            check = Category.objects.filter(slug=self.slug).count()
            if check > 0:
                self.slug = self.slug + "-" + str(self.pk)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        """return string representation of Category"""
        return self.name


class ProductDetails(models.Model):
    """Database model for Product"""
    Category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Product_Category",
        related_query_name="Product_Category",
    )
    Sub_Category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Product_Sub_Category",
        related_query_name="Product_Sub_Category",
    )
    Merchandiser = models.ForeignKey(contact,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True)
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True, null=True, blank=True)
    Short_description = models.TextField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    stock_unit = models.CharField(max_length=255, null=True, blank=True)
    stock_alart_amount = models.IntegerField(null=True, blank=True)
    height = models.DecimalField(max_digits=20,
                                 decimal_places=2,
                                 null=True,
                                 blank=True)
    width = models.DecimalField(max_digits=20,
                                decimal_places=2,
                                null=True,
                                blank=True)
    weight = models.DecimalField(max_digits=20,
                                 decimal_places=2,
                                 null=True,
                                 blank=True)
    discount_type = models.CharField(max_length=255, null=True, blank=True)
    discount = models.DecimalField(max_digits=20,
                                   decimal_places=2,
                                   null=True,
                                   blank=True)
    tax = models.DecimalField(max_digits=20,
                              decimal_places=2,
                              null=True,
                              blank=True)
    is_active = models.BooleanField(default=False, null=True, blank=True)
    product_code = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    min_price = models.DecimalField(default=0,
                                    blank=True,
                                    max_digits=20,
                                    decimal_places=2)
    max_price = models.DecimalField(default=0,
                                    blank=True,
                                    max_digits=20,
                                    decimal_places=2)
    product_discount_type = models.CharField(max_length=255, null=True, blank=True)
    product_discount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    product_discount_price = models.DecimalField(default=0, blank=True, max_digits=20, decimal_places=2)
    data = JSONField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """return string representation of Product"""
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.title)
            check = ProductDetails.objects.filter(slug=self.slug).count()
            if check > 0:
                obj = ProductDetails.objects.latest('id')
                self.slug = self.slug + "-" + str(obj.id + 1)
        else:
            self.slug = slugify(self.title)
            check = ProductDetails.objects.filter(slug=self.slug).count()
            if check > 0:
                self.slug = self.slug + "-" + str(self.pk)
        number = self.title.split("/")
        code = self.Category.slug
        if len(number) > 1:
            code = code + number[1]
        # self.product_code = code
        variations = ProductLocation.objects.filter(ProductDetails__id=self.id)
        total_quantity = 0
        max = min = total_quantity
        if len(variations) > 0:
            min = variations[0].selling_price
            max = variations[0].selling_price
        for variation in variations:
            total_quantity += variation.quantity
            if variation.selling_price > max:
                max = variation.selling_price
            elif variation.selling_price < min:
                min = variation.selling_price

        self.quantity = total_quantity
        self.max_price = max
        self.min_price = min
        return super().save(*args, **kwargs)


class Warehouse(models.Model):
    """Warehouse details"""
    Warehouse_parent = models.ForeignKey('self',
                                         on_delete=models.SET_NULL,
                                         null=True,
                                         blank=True)
    logo = models.ImageField(upload_to='business/outlet/logo',
                             null=True,
                             blank=True)
    logoWidth = models.CharField(max_length=500, null=True, blank=True)
    logoHeight = models.CharField(max_length=500, null=True, blank=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, null=True, blank=True)
    contact = models.CharField(max_length=500, null=True, blank=True)
    petty_cash = models.DecimalField(default=0,
                                     blank=True,
                                     max_digits=20,
                                     decimal_places=2)
    cash = models.DecimalField(default=0,
                               blank=True,
                               max_digits=20,
                               decimal_places=2)
    is_outlet = models.BooleanField(default=False, null=True, blank=True)
    is_office = models.BooleanField(default=False, null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def __str__(self):
        """return string representation of Warehouse"""
        return self.name


class ProductLocation(models.Model):
    """Product Location details"""
    Attributes = models.ManyToManyField('AttributeTerm',
                                        blank=True,
                                        related_name="Attributes",
                                        related_query_name="Attributes",)
    ProductDetails = models.ForeignKey('ProductDetails',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    Warehouse = models.ForeignKey(
        to='hrm.Office',
        on_delete=models.CASCADE,
    )
    description = models.CharField(max_length=2000, null=True,
                                   blank=True)
    Attribute_details = models.CharField(max_length=2000, null=True,
                                         blank=True)
    quantity = models.IntegerField(default=0)
    purchase_price = models.DecimalField(default=0,
                                         blank=True,
                                         max_digits=20,
                                         decimal_places=2)
    selling_price = models.DecimalField(default=0,
                                        blank=True,
                                        max_digits=20,
                                        decimal_places=2)
    price = models.DecimalField(default=0,
                                blank=True,
                                max_digits=20,
                                decimal_places=2)
    barcode = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # try:
        #     # product_code = int(self.id) + 100000000
        #     product_code = int(self.ProductDetails.id) + 100000000 
        # except Exception as e:
        #     product_code = 100000001
        # self.barcode = str(product_code)
        if self.pk:
            product_code = int(self.ProductDetails.id) + 100000
            if self.Attributes.exists():
                # print("--------------------------------")
                # print(self.Attributes.exists())
                # print(self.Attributes.all())
                newcode = ""
                for Attribute in self.Attributes.all():
                    
                    if Attribute.Attribute.name == "Size":
                        newcode =  str(int(Attribute.id) + 100) + str(newcode)
                    else:
                        newcode = str(newcode) + str(int(Attribute.id) + 100)
                product_code = str(product_code) + str(newcode)
                print("--------------------------------")
                print(self.barcode)
                print(product_code)
            self.barcode = str(product_code)
        super(ProductLocation, self).save(*args, **kwargs)

    def has_same_attributes(self, other_location):
        if not isinstance(other_location, ProductLocation):
            return False

        if self.Attributes.exists():
            # Get the set of attribute IDs for the current location
            current_attributes = set(self.Attributes.values_list('id', flat=True))

            # Get the set of attribute IDs for the other location
            other_attributes = set(other_location.Attributes.values_list('id', flat=True))

            # Compare the two sets
            return current_attributes == other_attributes
        else:
            return True

    def create_new_with_attributes(self, other_location):
        # Check if the attributes are different
        if not self.has_same_attributes(other_location):
            # Create a new ProductLocation object
            new_location = ProductLocation.objects.create(
                ProductDetails=self.ProductDetails,
                Warehouse=self.Warehouse,
                description=self.description,
                Attribute_details=self.Attribute_details,
                # quantity=self.quantity,
                purchase_price=self.purchase_price,
                selling_price=self.selling_price,
                price=self.price,
                barcode=self.barcode,
                created=timezone.now()  # or self.created if you want to keep the same creation time
            )

            # Copy the attributes from the current location to the new location
            # if self.Attributes.exists():
            #     new_location.Attributes.set(self.Attributes.all())

            return new_location
        else:
            return None
    
    def __str__(self):
        """return string representation of Warehouse"""
        # print("======================",self)
        return self.ProductDetails.title + "  --  "  + str(self.barcode) + "  --  " + str(self.Warehouse.name) + "  -  " + str(self.Attribute_details)


@ receiver(post_save, sender=ProductLocation)
def update_Product_Details(sender, instance, **kwargs):
    instance.ProductDetails.save()


def product_image_file_path(instance, filename):
    """Generate file path for new product image"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join("uploads/products/", filename)

class ProductLocationEntry(models.Model):
    """Product Location details"""
    ProductLocation = models.ForeignKey('ProductLocation',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    quantity = models.IntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    remarks = models.CharField(max_length=2000, null=True,
                                   blank=True)
    
    
class ProductImage(models.Model):
    """Product image details"""
    ProductDetails = models.ForeignKey('ProductDetails',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    ProductLocation = models.ForeignKey('ProductLocation',
                                        on_delete=models.CASCADE,
                                        null=True,
                                        blank=True)
    Color = models.ForeignKey('AttributeTerm',
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)
    photo = models.ImageField(null=True, upload_to=product_image_file_path)
    is_active = models.BooleanField(default=True, null=True, blank=True)

    # def __str__(self):
    #     """return string representation of Warehouse"""
    #     return self.photo


class transfer(models.Model):
    """database model for refund"""
    source = models.ForeignKey(
        to='hrm.Office',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source",
        related_query_name="source",
    )
    destance = models.ForeignKey(
        to='hrm.Office',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="destance",
        related_query_name="destance",
    )
    reference = models.CharField(max_length=255, blank=True, null=True)
    tansfer_number = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=255, blank=True)
    deatils = models.CharField(max_length=2550, blank=True)
    data = JSONField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.status == 'Received':
            items = transfer_item.objects.filter(transfer=self.pk)
            for item in items:
                item.is_received = True
                item.save()
        if self.status == 'Returned':
            items = transfer_item.objects.filter(transfer=self.pk)
            for item in items:
                item.is_returned = True
                item.save()
        super(transfer, self).save(*args, **kwargs)
    
    def __str__(self):
        """return string representation of Warehouse"""
        return self.tansfer_number


post_save.connect(notify_transfer_application, sender=transfer)
post_delete.connect(notify_transfer_deletion, sender=transfer)


class transfer_item(models.Model):
    """database model for refund"""
    transfer = models.ForeignKey('transfer',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    product = models.ForeignKey('ProductLocation',
                                on_delete=models.CASCADE,
                                null=True,
                                blank=True)
    quantity = models.IntegerField(default='1', blank=True, null=True)
    is_received = models.BooleanField(default=False, null=True, blank=True)
    is_returned = models.BooleanField(default=False, null=True, blank=True)
    issue_date = models.DateField(auto_now_add=True)
    data = JSONField(null=True, blank=True)


pre_save.connect(transfer_item_pre_save, sender=transfer_item)
post_save.connect(transfer_item_post_save, sender=transfer_item)
pre_delete.connect(transfer_item_pre_delete, sender=transfer_item)


# Saving Printed Barcode Based on Date
class BarcodePrintList(models.Model):
    challan_number = models.CharField(max_length=255, blank=True, null=True)
    product_locations = models.ForeignKey('ProductLocation', on_delete=models.CASCADE, null=True, blank=True, related_name="ProductLocation",)
    comments = models.TextField(blank=True, null=True)
    list_quantity = models.IntegerField(blank=True, null=True)
    issue_date = models.DateField(auto_now_add=True)
    data = JSONField(null=True, blank=True)

    def __str__(self):
        return f"Printed List:{self.challan_number} || List Quantity: {self.list_quantity} || Date:{self.issue_date}"
    
    class Meta:
        verbose_name = "Barcode Print List"
        verbose_name_plural = "Barcode Print Lists"
    
    def save(self, *args, **kwargs):
        total_quantity = 0
        if not self.challan_number:
            current_timestamp = datetime.now().strftime('%d%m%Y%H%M%S')
            self.challan_number = current_timestamp

        if self.product_locations:
            product_location_data = {
                'barcode': self.product_locations.barcode,
                'Attribute_details': self.product_locations.Attribute_details,
                'quantity': self.product_locations.quantity,
                'title': self.product_locations.ProductDetails.title,
                'product_code': self.product_locations.ProductDetails.product_code,
            }
            total_quantity += self.product_locations.quantity

            # product_location_json = json.dumps(product_location_data)
            # self.data = product_location_json
        if self.data:
            for product in self.data:
                total_quantity = total_quantity + int(product["quantity"])
        self.list_quantity = total_quantity 
        super().save(*args, **kwargs)
    
# class ProductHoldList(models.Model):
#     location = models.ForeignKey(ProductLocation, on_delete=models.CASCADE, null=True, blank=True, related_name="Location",)
#     warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True, related_name="Location")
#     note = models.TextField(blank=True, null=True)
    
