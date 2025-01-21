from django.db import models
from django.conf import settings
from contact.models import contact
import barcode
import uuid
import os
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from django.db.models import JSONField
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from product.signals import *
from django.dispatch import receiver
import json
from image_optimizer.fields import OptimizedImageField
# Create your models here.


class Attribute(models.Model):
    """Database model for Attribute"""
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True, null=True, blank=True)
    context = models.CharField(max_length=255, blank=True, null=True)
    data = JSONField(null=True, blank=True)

    # def get_deatils(self):
    #     """return string representation of Attribute"""
    #     return self.name

    def __str__(self):
        """return string representation of Attribute"""
        return self.name


class AttributeTerm(models.Model):
    """Database model for AttributeTerm"""
    Attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    
    slug = models.CharField(max_length=255, unique=True, null=True, blank=True)
    context = models.CharField(max_length=255, blank=True, null=True)
    url = models.TextField(null=True, blank=True, default="#")
    data = JSONField(null=True, blank=True)

    def __str__(self):
        """return string representation of Attribute terms"""
        return self.Attribute.name + "  --  " + self.name


class Category(models.Model):
    """Database model for Category"""
    Category_parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True, null=True, blank=True)
    meta_title = models.TextField(
        null=True, blank=True)
    meta_description = models.TextField(
        null=True, blank=True)
    page_title = models.TextField(
        null=True, blank=True)
    page_description = models.TextField(
        null=True, blank=True)
    url = models.TextField(null=True, blank=True, default="#")
    data = JSONField(null=True, blank=True)
    online_visible = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        """return string representation of Category"""
        return self.name
    

class Tag(models.Model):
    """Database model for Category"""
    name = models.CharField(max_length=255)
    meta_title = models.TextField(
        null=True, blank=True)
    meta_description = models.TextField(
        null=True, blank=True)
    slug = models.CharField(max_length=255, unique=True, null=True, blank=True)
    url = models.TextField(null=True, blank=True, default="#")
    online_visible = models.BooleanField(default=False, null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def __str__(self):
        """return string representation of Tag"""
        return self.name

class Brand(models.Model):
    """Database model for Category"""
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True, null=True, blank=True)
    logo = models.ImageField(
        upload_to='business/outlet/logo', null=True, blank=True)
    url = models.TextField(null=True, blank=True, default="#")
    online_visible = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        """return string representation of Tag"""
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
    Tag = models.ManyToManyField('Tag',
            blank=True,
            related_name="Tag",
            related_query_name="Tag",)
    Brand = models.ForeignKey('Brand',
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name="Brand",
            related_query_name="Brand",)
    Sub_Category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Product_Sub_Category",
        related_query_name="Product_Sub_Category",
    )
    Merchandiser = models.ForeignKey(
        contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255,null=True, blank=True)
    slug = models.CharField(max_length=255, unique=True, null=True, blank=True)
    Short_description = models.TextField(
        null=True, blank=True) 
    long_description = models.TextField(
        null=True, blank=True)
    meta_description = models.TextField(
        null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    stock_unit = models.CharField(max_length=255, null=True, blank=True)
    stock_alart_amount = models.IntegerField(null=True, blank=True)
    height = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=255, null=True, blank=True)
    discount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    tax = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=False, null=True, blank=True)
    product_code = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    min_price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    max_price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    url = models.TextField(null=True, blank=True)
    attribute_list = JSONField(null=True, blank=True)
    breadcrumbs = JSONField(null=True, blank=True)
    is_sellable = models.BooleanField(default=False, null=True, blank=True)
    is_live = models.BooleanField(default=False, null=True, blank=True)
    live_date = models.DateField(null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def __str__(self):
        """return string representation of Product"""
        return self.title
    
    def get_breadcrumbs(self, Category, breadcrumbs):
        
        breadcrumbs.insert(0 ,{"id": Category.id, "name": Category.name, "slug" : Category.slug, "url": Category.url})
        if Category.Category_parent:
            self.get_breadcrumbs(Category.Category_parent, breadcrumbs)
        else:
            return {"id": Category.id, "name": Category.name, "slug" : Category.slug, "url": Category.url}

    def save(self, *args, **kwargs):
        # slug
        # self.slug = slugify(self.slug)
        if self.slug == "":
            if self.name:
                self.slug = slugify(self.name)
            else:
                self.slug = slugify(self.title)
        # url
        self.url = "/" + str(self.slug)
        brand = Brand.objects.get(id=1)
        self.Brand = brand
        
        
        # breadcrumbss
        # breadcrumbs = []
        # self.get_breadcrumbs(self.Category, breadcrumbs)
        # self.breadcrumbs = breadcrumbs
        
        # product code
        number = self.title.split("/")
        code = self.Category.slug
        if len(number) > 1:
            code = code + number[1]
        self.product_code = code
        
        # get variations
        variations = ProductLocation.objects.filter(ProductDetails__id=self.id)
        
        
        total_quantity = 0
        colors = []
        sizes = []
        attribute_Set = []
        max = min = total_quantity
        if len(variations) > 0:
            min = variations[0].selling_price
            max = variations[0].selling_price
        for variation in variations:
            
            
            
            # color
            if variation.Color:
                flag = 0
                for color in colors:
                    if variation.Color.id == color["id"]:
                        flag = 1;
                if flag == 0:    
                    attribute_Set.append(variation.Color.id)
                    colors.append({"name" : variation.Color.name , "id" : variation.Color.id, "code" : variation.Color.context, "class": "bg-babypink" })
                
            
            # size
            if variation.Size:
                flag = 0
                inStock = True
                if variation.quantity < 1:
                    inStock = False
                for size in sizes:
                    if variation.Size.id == size["id"]:
                        flag = 1;
                if flag == 0:    
                    attribute_Set.append(variation.Size.id)
                    sizes.append({"name" : variation.Size.name , "id" : variation.Size.id, "inStock" :  inStock})

            # quantity  
            total_quantity += variation.quantity
            
            # price
            if variation.selling_price > max:
                max = variation.selling_price
            elif variation.selling_price < min:
                min = variation.selling_price

        self.quantity = total_quantity
        self.max_price = max
        self.min_price = min
        self.data = {"colors": colors, "sizes": sizes}
        self.attribute_list = attribute_Set
        
        return super().save(*args, **kwargs)


class BulkProduct(models.Model):
    """Database model for Bulk Product"""
    Category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Category",
        related_query_name="Category",
    )
    Sub_Category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Sub_Category",
        related_query_name="Sub_Category",
    )
    Merchandiser = models.ForeignKey(
        contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True, null=True, blank=True)
    Short_description = models.TextField(
        null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    purchase_price = models.IntegerField(null=True, blank=True)
    selling_price = models.IntegerField(default=0, null=True, blank=True)
    price = models.IntegerField(default=0, null=True, blank=True)
    stock_unit = models.CharField(max_length=255, null=True, blank=True)
    stock_alart_amount = models.IntegerField(null=True, blank=True)
    height = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=255, null=True, blank=True)
    discount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    tax = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    barcode = models.CharField(
        max_length=255, unique=True, null=True, blank=True)
    product_code = models.CharField(max_length=255, null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def __str__(self):
        """return string representation of Bulk Product"""
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        number = self.title.split("/")
        code = self.Category.slug
        if len(number) > 1:
            code = code + number[1]
        self.product_code = code
        return super().save(*args, **kwargs)


class BulkProductList(models.Model):
    """list of bulk product"""
    BulkProduct = models.ForeignKey(
        'BulkProduct',
        on_delete=models.CASCADE,
    )
    ProductDetails = models.ForeignKey(
        'ProductDetails',
        on_delete=models.CASCADE,
    )
    data = JSONField(null=True, blank=True)

    def __str__(self):
        """return string representation of Bulk Product List"""
        return self.BulkProduct.title + "  ----  " + self.ProductDetails.title


class Warehouse(models.Model):
    """Warehouse details"""
    logo = models.ImageField(
        upload_to='business/outlet/logo', null=True, blank=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, null=True, blank=True)
    contact = models.CharField(max_length=500, null=True, blank=True)
    petty_cash = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    cash = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    is_outlet = models.BooleanField(default=False, null=True, blank=True)
    is_office = models.BooleanField(default=False, null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def __str__(self):
        """return string representation of Warehouse"""
        return self.name


class ProductLocation(models.Model):
    """Product Location details"""
    Single = 'S'
    Bulk = 'B'
    product_type = [
        (Single, 'Single'),
        (Bulk, 'Bulk'),
    ]
    ref_type = models.CharField(
        max_length=2,
        choices=product_type,
        default=Single,
    )
    BulkProduct = models.ForeignKey(
        'BulkProduct',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    Color = models.ForeignKey(
        'AttributeTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Color",
        related_query_name="Color",
    )
    Size = models.ForeignKey(
        'AttributeTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Size",
        related_query_name="Size",
    )
    Custom_one = models.ForeignKey(
        'AttributeTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Custom_one",
        related_query_name="Custom_one",
    )
    Custom_two = models.ForeignKey(
        'AttributeTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Custom_two",
        related_query_name="Custom_two",
    )
    ProductDetails = models.ForeignKey(
        'ProductDetails',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    Warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField(default=0)
    purchase_price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    selling_price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    discounted_price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    barcode = models.CharField(
        max_length=255, null=True, blank=True)
    data = JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # self.slug = slugify(self.title)
        # print("---------------------------------------------------------")
        color = "000"
        size = "00"
        if(self.Color):
            if(self.Color.id < 9):
                color = "00" + str(self.Color.id)
            elif(self.Color.id < 90):
                color = "0" + str(self.Color.id)
            else:
                color = str(self.Color.id)
        if(self.Size):
            if(self.Size.id < 9):
                size = "0" + str(self.Size.id)
            else:
                size = str(self.Size.id)
        
        if(self.ProductDetails.discount):
            if self.ProductDetails.discount_type == "%":
                self.discounted_price = self.selling_price - ((self.selling_price * self.ProductDetails.discount) / 100)
            else:
                self.discounted_price = self.selling_price - self.ProductDetails.discount
        else:
            self.discounted_price = self.selling_price
        try:
            product_code = int(self.ProductDetails.id) + 100000
        except Exception as e:
            product_code = 100001
        self.barcode = str(product_code) + color + size
        # print(self.barcode)

        super(ProductLocation, self).save(*args, **kwargs)

    def __str__(self):
        """return string representation of Warehouse"""
        return self.ProductDetails.title


@receiver(post_save, sender=ProductLocation)
def update_Product_Details(sender, instance, **kwargs):
    instance.ProductDetails.save()


def product_image_file_path(instance, filename):
    """Generate file path for new product image"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join("uploads/products/", filename)


class ProductImage(models.Model):
    """Product image details"""
    ProductDetails = models.ForeignKey(
        'ProductDetails',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    ProductLocation = models.ForeignKey(
        'ProductLocation',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    Color = models.ForeignKey(
        'AttributeTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    photo = models.ImageField(null=True, upload_to=product_image_file_path)
    thumbnail = OptimizedImageField(
        null=True,
        blank=True,
        upload_to=product_image_file_path,
        optimized_image_output_size=(600, 900),
        optimized_image_resize_method="thumbnail"  #  "crop", "cover", "contain", "width", "height", "thumbnail" or None
    )
    is_active = models.BooleanField(default=True, null=True, blank=True)

    # def __str__(self):
    #     """return string representation of Warehouse"""
    #     return self.photo


class transfer(models.Model):
    """database model for refund"""
    source = models.ForeignKey(
        'Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source",
        related_query_name="source",
    )
    destance = models.ForeignKey(
        'Warehouse',
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
    transfer = models.ForeignKey(
        'transfer',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        'ProductLocation',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    quantity = models.IntegerField(default='1', blank=True, null=True)
    is_received = models.BooleanField(default=False, null=True, blank=True)
    is_returned = models.BooleanField(default=False, null=True, blank=True)
    issue_date = models.DateField(auto_now_add=True)
    data = JSONField(null=True, blank=True)

pre_save.connect(transfer_item_pre_save, sender=transfer_item)
post_save.connect(transfer_item_post_save, sender=transfer_item)
pre_delete.connect(transfer_item_pre_delete, sender=transfer_item)