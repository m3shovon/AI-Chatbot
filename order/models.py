from django.db import models
from contact import models as contactModel
from product import models as productModel
from accounting import models as accountingModel
# from accounting.models import account
from django.utils import timezone
from django.db.models import JSONField
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from order.signals import *
import uuid
import os
import datetime
from datetime import date
# Create your models here.


class cupon(models.Model):
    """database model for Cupon"""
    Percentage = 'P'
    Amount = 'A'
    cupon_type = [
        (Percentage, 'Percentage'),
        (Amount, 'Amount'),

    ]
    name = models.CharField(max_length=255)
    amount = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    status = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    limit_type = models.CharField(
        max_length=255, null=True, blank=True, default="unlimited")
    limit = models.IntegerField(default=0)
    ref_type = models.CharField(
        max_length=2,
        choices=cupon_type,
        default=Amount,
    )

    def __str__(self):
        """return string representation of Cupon"""
        return self.name


class refund(models.Model):
    """database model for refund"""
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=255, blank=True)
    deatils = models.TextField(blank=True)

    def __str__(self):
        """return string representation of refund"""
        return self.reason


class DeliveryType(models.Model):
    Type = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        """return string representation of refund"""
        return self.name


class invoice(models.Model):
    """database model for invoice"""
    contact = models.ForeignKey(
        contactModel.contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    cupon = models.ForeignKey(
        'cupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    refund = models.ForeignKey(
        'refund',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    location = models.ForeignKey(
        to="hrm.Office",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    account = models.ForeignKey(
        accountingModel.account,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    employe = models.ForeignKey(
        to="hrm.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employe",
        related_query_name="employe",
    )
    Sales_person = models.ForeignKey(
        to="hrm.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Sales_person",
        related_query_name="Sales_person",
    )
    invoice_number = models.CharField(max_length=255, blank=True)
    order_number = models.CharField(max_length=255, blank=True)
    shipping_address = models.TextField(blank=True)
    delivery_charge = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    delivery_cost = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    delivery_person = models.CharField(max_length=255, blank=True)
    DeliveryType = models.ForeignKey(
        "DeliveryType", on_delete=models.SET_NULL, null=True, blank=True)
    delivery_date = models.DateField(blank=True, null=True)
    program_date = models.DateField(blank=True, null=True)
    Payment_method = models.CharField(max_length=255, blank=True, null=True)
    Account_no = models.CharField(max_length=255, blank=True)
    Transection_no = models.CharField(max_length=255, blank=True)
    remarks = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    bill = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    due = models.DecimalField(default=0, blank=True,
                              max_digits=20, decimal_places=2)
    receive = models.DecimalField(default=0, blank=True, null=True,
                              max_digits=20, decimal_places=2)
    refund = models.DecimalField(default=0, blank=True, null=True,
                              max_digits=20, decimal_places=2)
    discount = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    discountlimit = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    tax = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    costing = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    profit = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    payment = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    advance_payment = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    is_delivered = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    issue_date = models.DateField(auto_now_add=True, editable=True)
    Vat_issued_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=255, default="Pending", blank=True, null=True)

    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    postalCode = models.CharField(max_length=255, blank=True, null=True)
    thana = models.CharField(max_length=255, blank=True, null=True)
    s_phone = models.CharField(max_length=255, blank=True, null=True)
    shipping_method = models.CharField(max_length=255, blank=True, null=True)
    additional_discount = models.DecimalField(default=0, blank=True, null=True, max_digits=20, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.pk:
            totalbill = 0
            productbill = 0
            productcost = 0
            maxdiscount = 0
            products = invoice_item.objects.filter(
                invoice__id=self.id)
            qty = 0
            # product count
            for i in products:
                productbill = productbill + (i.price * i.quantity)
                productcost = productcost + (i.purchase_price * i.quantity)
                totalbill = totalbill + (i.price * i.quantity)
                qty = qty + i.quantity
                productdiscount = 0
                if i.product is not None:
                    if i.product.ProductDetails.discount is not None:
                        if i.product.ProductDetails.discount_type == "%":
                            productdiscount = (
                                i.product.selling_price * i.product.ProductDetails.discount)/100
                        else:
                            productdiscount = i.product.ProductDetails.discount
                maxdiscount += float(productdiscount) * i.quantity

            # Service count
            service = services.objects.filter(invoice__id=self.id)
            for i in service:
                totalbill = totalbill + (i.price * i.quantity)
                qty = qty + i.quantity
            self.quantity = qty

            # max discount
            if maxdiscount > 0:
                self.discountlimit = maxdiscount

            # New additional Discount
            additional_discount = self.additional_discount

            # DIscount calculation
            if self.cupon:

                if self.cupon.ref_type == "P":
                    discount = productbill * (self.cupon.amount/100)
                    self.discount = discount
                else:
                    if productbill > self.cupon.amount:
                        # self.discount = self.cupon.amount
                        self.discount = self.cupon.amount + additional_discount
                    else:
                        self.discount = productbill

            else:
                if additional_discount > 0:
                    self.discount = additional_discount            
            # if bill is zero or negative
            if totalbill < 1:
                self.discount = 0
                self.bill = totalbill + self.delivery_charge
            else:
                self.bill = totalbill + self.delivery_charge - self.discount

            ### if due is zero or negative ###
            # if self.bill - self.payment > 0:
            #     self.due = self.bill - self.payment
            if self.bill - (self.payment + additional_discount) > 0:
                self.due = self.bill - (self.payment + additional_discount)
                self.advance_payment = 0
            else:
                self.due = 0
                self.advance_payment = self.payment - self.bill
            self.costing = float(productcost)
            # VAT calculation
            productbill = productbill - self.discount
            self.tax = round(float(productbill) -
                             float(productbill) / 1.075, 2)

            # location = productModel.Warehouse.objects.filter(
            #     id=self.location.id)
            
            
            # payment methods
            if not self.is_public:
                if self.Payment_method != "Cash":
                    self.is_public = True
                journal_items = accountingModel.journal.objects.filter(invoice=self)
                for item in journal_items:
                    if item.account:
                        if item.account.type != "Cash" :
                            print(item.details)
                            print(item.account.type)
                            self.is_public = True
                else:
                    self.is_public = False


        else:
            # VAT Generate date
            if self.due == 0:
                self.Vat_issued_date = datetime.date.today()
                self.status = "Delivered"

            maxdiscount = 0
            products = invoice_item.objects.filter(
                invoice__id=self.id)
            # product count
            for i in products:
                productdiscount = 0
                if i.product.ProductDetails.discount is not None:
                    if i.product.ProductDetails.discount_type == "%":
                        productdiscount = (
                            i.product.selling_price * i.product.ProductDetails.discount)/100
                    else:
                        productdiscount = i.product.ProductDetails.discount
                maxdiscount += float(productdiscount) * i.quantity

            # max discount
            if maxdiscount > 0:
                self.discountlimit = maxdiscount

            # location = productModel.Warehouse.objects.filter(
            #     id=self.location.id)

            # self.order_number = location[0].name[0] + \
            #     "-" + str(self.invoice_number)[-5:]
            self.order_number = str(self.invoice_number)[-5:]
            
            # payment methods
            if not self.is_public:
                if self.Payment_method != "Cash":
                    self.is_public = True
                else:
                    self.is_public = False    
        
        return super().save(*args, **kwargs)

    def __str__(self):
        """return string representation of invoice"""
        return "Invoice No: " + str(self.invoice_number)


pre_save.connect(invoice_pre_save, sender=invoice)
post_save.connect(invoice_post_save, sender=invoice)
post_delete.connect(invoice_post_delete, sender=invoice)


class invoice_item(models.Model):
    """database model for invoice items"""
    invoice = models.ForeignKey(
        invoice,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        productModel.ProductLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    Details = models.CharField(max_length=2000, null=True, blank=True)
    quantity = models.IntegerField(default='1')
    price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    purchase_price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.product:
            Attribute_details = ""
            count = 0
            for attribute in self.product.Attributes.all():
                if count == 0:
                    Attribute_details += attribute.name
                else:
                    Attribute_details = Attribute_details + " / " + attribute.name
                count += 1
            self.Attribute_details = Attribute_details
            if Attribute_details != "":
                self.Details = self.product.ProductDetails.title + " -- " + Attribute_details
            else:
                self.Details = self.product.ProductDetails.title
        return super().save(*args, **kwargs)

    def __str__(self):
        """return string representation of invoice"""
        return "Item for Invoice No: " + str(self.invoice.invoice_number)


@receiver(post_save, sender=invoice_item)
def update_Invoice_costing(sender, created, instance, **kwargs):
    if created is False:
        instance.invoice.save()
    elif instance.data == "reload":
        instance.invoice.save()


@receiver(post_delete, sender=invoice_item)
def update_Invoice_costing(sender, instance, **kwargs):
    instance.invoice.save()

class invoice_item_copy(models.Model):
    """Database model for invoice item copy"""
    invoice = models.ForeignKey(
        invoice,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        productModel.ProductLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    Details = models.CharField(max_length=2000, null=True, blank=True)
    quantity = models.IntegerField(default='1')
    price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    purchase_price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    data = JSONField(null=True, blank=True)
    is_exchanged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        """Return string representation of invoice item copy"""
        return "Item Copied for Invoice No: " + str(self.invoice.invoice_number)
    
@receiver(post_save, sender=invoice_item)
def create_invoice_item_copy(sender, instance, created, **kwargs):
    if created:
        invoice_item_copy.objects.create(
            invoice=instance.invoice,
            product=instance.product,
            Details=instance.Details,
            quantity=instance.quantity,
            price=instance.price,
            purchase_price=instance.purchase_price,
            data=instance.data
        )    

class invoice_payment(models.Model):
    """database model for invoice"""
    invoice = models.ForeignKey(
        invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    Sales_person = models.ForeignKey(
        "hrm.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    account = models.ForeignKey(
        accountingModel.account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantity = models.IntegerField(default=0, blank=True, null=True)
    bill = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    due = models.DecimalField(default=0, blank=True,
                              max_digits=20, decimal_places=2)
    receive = models.DecimalField(default=0, blank=True, null=True,
                              max_digits=20, decimal_places=2)
    refund = models.DecimalField(default=0, blank=True, null=True,
                              max_digits=20, decimal_places=2)
    discount = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    tax = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    payment = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    advance_payment = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    # issue_date = models.DateField(auto_now_add=True)
    issue_date = models.DateField( default=date.today, blank=True)

    def __str__(self):
        """return string representation of invoice"""
        return "Payment for Invoice No: " + str(self.invoice.invoice_number)
    
class services(models.Model):
    """database model for invoice"""
    invoice = models.ForeignKey(
        invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    employe = models.ForeignKey(
        to="hrm.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        productModel.ProductLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    details = models.TextField(blank=True)
    price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    cost = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    quantity = models.IntegerField(default=0, blank=True)
    profit = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    status = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(auto_now_add=True)

    def __str__(self):
        """return string representation of invoice"""
        return "Servicces for Invoice No: " + str(self.invoice.invoice_number)


post_save.connect(notify_service_application, sender=services)
post_delete.connect(notify_service_deletion, sender=services)


@receiver(post_save, sender=services)
def update_Service_costing(sender, created, instance, **kwargs):
    if created is False:
        instance.invoice.save()
    elif instance.data == "reload":
        instance.invoice.save()


@receiver(post_delete, sender=services)
def update_Invoice_costing(sender, instance, **kwargs):
    instance.invoice.save()


class services_costing(models.Model):
    """database model for invoice"""
    services = models.ForeignKey(
        services,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        productModel.ProductLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    details = models.TextField(blank=True)
    cost = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    quantity = models.IntegerField(default=1, blank=True)
    remarks = models.TextField(blank=True, null=True)
    data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(auto_now_add=True)

    def __str__(self):
        """return string representation of invoice"""
        return "Services Costing for Invoice No: " + str(self.services.invoice.invoice_number)


post_save.connect(services_costing_post_save, sender=services_costing)
pre_delete.connect(services_costing_pre_delete, sender=services_costing)


class measurement(models.Model):
    """database model for invoice items"""
    invoice = models.ForeignKey(
        invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        productModel.ProductLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    service = models.ForeignKey(
        services,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    contact = models.ForeignKey(
        contactModel.contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    Blouse = models.BooleanField(default=False)
    Kameez = models.BooleanField(default=False)
    Gown = models.BooleanField(default=False)
    Skirt = models.BooleanField(default=False)
    Paladzo = models.BooleanField(default=False)
    Pant = models.BooleanField(default=False)
    Gharara = models.BooleanField(default=False)
    Note = models.TextField(blank=True)
    Chest = models.CharField(max_length=255, blank=True)
    Waist = models.CharField(max_length=255, blank=True)
    Hand_opening = models.CharField(max_length=255, blank=True)
    Hip = models.CharField(max_length=255, blank=True)
    Length = models.CharField(max_length=255, blank=True)
    End = models.CharField(max_length=255, blank=True)
    Slit = models.CharField(max_length=255, blank=True)
    Shoulder = models.CharField(max_length=255, blank=True)
    Neck_deep_f = models.CharField(max_length=255, blank=True)
    Arm_hole = models.CharField(max_length=255, blank=True)
    Neck_deep_b = models.CharField(max_length=255, blank=True)
    Sleeve_l = models.CharField(max_length=255, blank=True)
    Half_body = models.CharField(max_length=255, blank=True)
    Muscle = models.CharField(max_length=255, blank=True)
    Length_bottom = models.CharField(max_length=255, blank=True)
    Waist_bottom = models.CharField(max_length=255, blank=True)
    Hip_bottom = models.CharField(max_length=255, blank=True)
    Thigh = models.CharField(max_length=255, blank=True)
    Knee = models.CharField(max_length=255, blank=True)
    Leg_openning = models.CharField(max_length=255, blank=True)
    data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(auto_now_add=True)
    is_basic = models.BooleanField(default=False)

    def __str__(self):
        """return string representation of invoice"""
        if self.invoice:
            return "Measurement for Invoice No: " + str(self.invoice.invoice_number)
        else:
            return str(self.id)


class purchase(models.Model):
    """database model for invoice"""
    contact = models.ForeignKey(
        contactModel.contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    refund = models.ForeignKey(
        'refund',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    location = models.ForeignKey(
        to="hrm.Office",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    account = models.ForeignKey(
        accountingModel.account,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    employe = models.ForeignKey(
        to="hrm.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    purchase_number = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    delivery_method = models.CharField(max_length=255, blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    Payment_method = models.CharField(max_length=255, blank=True, null=True)
    Account_no = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    bill = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    due = models.DecimalField(default=0, blank=True,
                              max_digits=20, decimal_places=2)
    discount = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)

    costing = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    shipping = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    payment = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    adjustment = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    is_received = models.BooleanField(default=False)
    received_item = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    received_item_price = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(auto_now_add=True)
    tax_type = models.CharField(
        max_length=255, default="Pending", blank=True, null=True)
    status = models.CharField(
        max_length=255, default="Pending", blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk:
            totalbill = 0
            products = purchase_item.objects.filter(
                purchase__id=self.id)
            qty = 0
            received_item = 0
            received_item_price = 0
            for i in products:
                totalbill = totalbill + (i.price * i.quantity)
                qty += i.quantity
                if i.received == 1:
                    received_item += i.quantity
                    received_item_price += (i.price * i.quantity)
            self.quantity = qty
            self.received_item = received_item
            self.received_item_price = received_item_price
            # self.costing = total + self.delivery_cost
            # self.bill = totalbill + self.delivery_charge - self.discount
            self.bill = totalbill - self.discount
            self.due = self.bill - self.payment
            print("-----------------")
            print(self.received_item_price)
        return super().save(*args, **kwargs)

    def __str__(self):
        """return string representation of invoice"""
        return "Purchase No: " + str(self.purchase_number)


post_save.connect(purchase_post_save, sender=purchase)
pre_save.connect(purchase_pre_save, sender=purchase)
post_delete.connect(purchase_post_delete, sender=purchase)


class purchase_item(models.Model):
    """database model for invoice items"""
    purchase = models.ForeignKey(
        purchase,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        productModel.ProductLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    Details = models.CharField(max_length=2000, null=True, blank=True)
    quantity = models.IntegerField(default='1', blank=True, null=True)
    damage = models.IntegerField(blank=True, null=True)
    received = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(
        default=0, blank=True, null=True, max_digits=20, decimal_places=2)
    landing_price = models.DecimalField(
        default=0, blank=True, null=True, max_digits=20, decimal_places=2)
    discount = models.DecimalField(
        default=0, blank=True, null=True, max_digits=20, decimal_places=2)
    tax = models.DecimalField(
        default=0, blank=True, null=True, max_digits=20, decimal_places=2)
    data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.product:
            Attribute_details = ""
            count = 0
            for attribute in self.product.Attributes.all():
                if count == 0:
                    Attribute_details += attribute.name
                else:
                    Attribute_details = Attribute_details + " / " + attribute.name
                count += 1
            self.Attribute_details = Attribute_details
            if Attribute_details != "":
                self.Details = self.product.ProductDetails.title + " -- " + Attribute_details
            else:
                self.Details = self.product.ProductDetails.title
        return super().save(*args, **kwargs)

    # def __str__(self):
    #     """return string representation of invoice items"""
    #     return self

    def __str__(self):
        """return string representation of invoice"""
        return "Item for Purchase No: " + str(self.purchase.purchase_number)


@receiver(post_save, sender=purchase_item)
def update_Purchase_costing(sender, instance, **kwargs):
    # res = sender.objects.filter(id=instance.id)
    # if len(res) > 0:
    #     previousItem = res[0]
    #     flag = 0
    #     if instance.quantity != previousItem.quantity:
    #         flag = 1
    #     if instance.price != previousItem.price:
    #         flag = 1
    #     if instance.received != previousItem.received:
    #         flag = 1
    #     if flag == 1:
    #         print("-------------------purchase_item--------------------")
    instance.purchase.save()


@receiver(post_delete, sender=purchase_item)
def update_Purchase_costing(sender, instance, **kwargs):
    instance.purchase.save()


class wordrobe(models.Model):
    """database model for invoice"""
    contact = models.ForeignKey(
        contactModel.contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    location = models.ForeignKey(
        to="hrm.Office",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    wordrobe_number = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    registered_Address = models.TextField(
        blank=True, null=True)
    company_profile_link = models.TextField(
        blank=True, null=True)
    photographer_name = models.TextField(
        blank=True, null=True)
    model_name = models.TextField(blank=True, null=True)
    makeup_artist_name = models.TextField(
        blank=True, null=True)
    delivery_method = models.CharField(max_length=255, blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    Payment_method = models.CharField(max_length=255, blank=True, null=True)
    Account_no = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    product_cost = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    rent = models.DecimalField(default=0, blank=True,
                               max_digits=20, decimal_places=2)
    payment = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    due = models.DecimalField(default=0, blank=True,
                              max_digits=20, decimal_places=2)
    data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=255, default="Pending", blank=True, null=True)
    is_returned = models.BooleanField(default=False)

    # def __str__(self):
    #     """return string representation of invoice"""
    #     return self


class wordrobe_item(models.Model):
    """database model for invoice items"""
    wordrobe = models.ForeignKey(
        wordrobe,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        productModel.ProductLocation,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    Details = models.CharField(max_length=2000, null=True, blank=True)
    quantity = models.IntegerField(default='1', blank=True, null=True)
    price = models.DecimalField(
        default=0, blank=True, null=True, max_digits=20, decimal_places=2)
    data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(auto_now_add=True)
    is_returned = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.product:
            productname = self.product.ProductDetails.title
            if self.product.Color and self.product.Size:
                productname += " -- "
                productname += self.product.Color.name
                productname += " / "
                productname += self.product.Size.name
            else:
                if self.product.Color:
                    productname += " -- "
                    productname += self.product.Color.name
                if self.product.Size:
                    productname += " -- "
                    productname += self.product.Size.name

            self.Details = self.product.ProductDetails.title
        return super().save(*args, **kwargs)

    # def __str__(self):
    #     """return string representation of invoice items"""
    #     return self


class exchange(models.Model):
    """database model for refund"""
    invoice = models.ForeignKey(
        invoice,
        on_delete=models.CASCADE
    )
    Exchange_product = models.ForeignKey(
        productModel.ProductLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    services = models.ForeignKey(
        services,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantity = models.IntegerField(default='1', blank=True, null=True)
    price = models.DecimalField(
        default=0, blank=True, null=True, max_digits=20, decimal_places=2)
    reason = models.CharField(max_length=255)
    issue_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=255, blank=True)
    deatils = models.CharField(max_length=2550, blank=True)


# Draft Orders Start =================================================================
class DraftCostSheet(models.Model):
    style_name = models.CharField(max_length=100)
    client_name = models.CharField(max_length=100)
    style_code = models.CharField(max_length=100)
    designer_name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    # data = JSONField(null=True, blank=True)
    net_total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    profit_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    net_selling_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    data = JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate total cost and net total cost from DraftOrder instances
        draft_orders = DraftOrder.objects.filter(cost_sheet=self)
        net_total_cost = sum(order.amount for order in draft_orders)
        self.net_total_cost = net_total_cost
        profit_percentage = self.profit_percentage

        self.net_selling_price = self.net_total_cost + \
            (self.net_total_cost * profit_percentage / 100)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.style_name

def draft_image_file_path(instance, filename):
    """Generate file path for new product image"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join("uploads/draft_images/", filename)

class DraftImage(models.Model):
    cost_sheet = models.ForeignKey(DraftCostSheet, on_delete=models.CASCADE, null=True, blank=True)
    product_image = models.ImageField(upload_to=draft_image_file_path, null=True)

    def __str__(self):
        return f"Image for {self.cost_sheet}"


class DraftOrder(models.Model):
    cost_sheet = models.ForeignKey(DraftCostSheet, on_delete=models.CASCADE, null=True)
    FABRICS = 'Fabrics'
    TRIMS_ACCESSORIES = 'Trims/Accessories'
    LABOR_COST = 'Labor Cost'
    COST_SHEET_ITEMS_CHOICES = [
        (FABRICS, 'Fabrics'),
        (TRIMS_ACCESSORIES, 'Trims/Accessories'),
        (LABOR_COST, 'Labor Cost'),
    ]
    cost_sheet_items = models.CharField(
        max_length=100, choices=COST_SHEET_ITEMS_CHOICES, null=True)
    draft_name = models.CharField(max_length=255, null=True, blank=True)
    unit_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    YARDS = 'Yards'
    PCS = 'Pcs'
    HOURS = 'Hours'
    UNIT_NAME_CHOICES = [
        (YARDS, 'Yards'),
        (PCS, 'Pcs'),
        (HOURS, 'Hours'),
    ]
    unit_name = models.CharField(max_length=100, choices=UNIT_NAME_CHOICES, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    data = JSONField(null=True, blank=True)

    # def __str__(self):
    #     return f"Order for {self.cost_sheet.style_name}"
    def __str__(self):
        if self.cost_sheet is not None:
            return f"Order for > {self.cost_sheet.style_name} - {self.cost_sheet_items} - {self.draft_name}"
        return "Order without associated cost sheet"

    def save(self, *args, **kwargs):
        # Calculate amount based on unit quantity and unit price
        if self.unit_name == self.YARDS:
            self.amount = self.unit_quantity * self.unit_price
        elif self.unit_name == self.PCS:
            self.amount = self.unit_quantity * self.unit_price
        elif self.unit_name == self.HOURS:
            self.amount = self.unit_quantity * self.unit_price

        super().save(*args, **kwargs)


@receiver(post_save, sender=DraftOrder)
def update_draft_cost_sheet(sender, instance, **kwargs):
    # Update the related DraftCostSheet instance after a DraftOrder is saved
    draft_cost_sheet = instance.cost_sheet
    if draft_cost_sheet is not None:
        draft_cost_sheet.save()

# Draft Orders Ends =================================================================
