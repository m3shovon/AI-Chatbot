from django.db import models
from contact import models as contactModel
from product import models as productModel
from accounting import models as accountingModel
from django.utils import timezone
from django.db.models import JSONField
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from order.signals import *

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
    location = models.ForeignKey(
        productModel.Warehouse,
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
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employe",
        related_query_name="employe",
    )
    Sales_person = models.ForeignKey(
        contactModel.UserProfile,
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
    is_refunded = models.BooleanField(default=False)
    is_sms_enabled = models.BooleanField(default=True)
    is_mute = models.BooleanField(default=True)
    data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(auto_now_add=True)
    Vat_issued_date = models.DateField(null=True, blank=True)
    Received_by_factory_date = models.DateField(null=True, blank=True)
    delivered_date = models.DateField(null=True, blank=True)
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

            # DIscount calculation
            if self.cupon:
               
                if self.cupon.ref_type == "P":
                    discount = productbill * (self.cupon.amount/100)
                    self.discount = discount
                else:
                    if productbill > self.cupon.amount:
                        self.discount = self.cupon.amount
                    else:
                        self.discount = productbill
            # if bill is zero or negative
            if totalbill < 1:
                self.discount = 0
                self.bill = totalbill + self.delivery_charge
            else:
                self.bill = totalbill + self.delivery_charge - self.discount

            # if due is zero or negative
            if self.bill - self.payment > 0:
                self.due = self.bill - self.payment
                self.advance_payment = 0
            else:
                self.due = 0
                self.advance_payment = self.payment - self.bill
                self.is_refunded = False
            self.costing = float(productcost)
            # VAT calculation
            productbill = productbill - self.discount
            brand = productModel.Brand.objects.get(id=1)
            if brand.name == "ELOR":
                self.tax = round(float(productbill) - float(productbill) / 1.050, 2)
            else:
                self.tax = round(float(productbill) - float(productbill) / 1.075, 2)

            location = productModel.Warehouse.objects.filter(
                id=self.location.id)
            
            journal_items = accountingModel.journal.objects.filter(invoice=self.id, account=36).count()
            if journal_items > 0:
                self.is_mute = False
            # print(journal_items)
            
        else:
            self.is_sms_enabled = True
            self.is_mute = True
           
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

            location = productModel.Warehouse.objects.filter(
                id=self.location.id)
           
            self.order_number = location[0].name[0] + "-" + str(self.invoice_number)[-5:]
        return super().save(*args, **kwargs)

    def __str__(self):
        """return string representation of invoice"""
        return "Invoice No: " + str(self.invoice_number)


pre_save.connect(invoice_pre_save, sender=invoice)
post_save.connect(invoice_post_save, sender=invoice)
post_delete.connect(invoice_post_delete, sender=invoice)


@receiver(pre_delete, sender=invoice)
def delete_items_journals(sender, instance, **kwargs):
    # invoiceitems = invoice_item.objects.filter(invoice=instance.id)
    # for invoiceitem in invoiceitems:
    #     invoiceitem.delete()
    
    journals = accountingModel.journal.objects.filter(invoice=instance.id)
    for journal in journals:
        # print(journal)
        journal.delete()
    # journals = accountingModel.journal.objects.filter(invoice=instance.id)
    # print(journals)
    
    


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
            self.Details = productname
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
def update_product(sender, instance, **kwargs):
    if instance.product:
        # print(instance.product.quantity)
        instance.product.quantity = instance.product.quantity + instance.quantity
        # print(instance.product.quantity)
        instance.product.save()
    else:
        instance.invoice.save()

@receiver(pre_save, sender=invoice_item)
def update_product_presave(sender, instance, **kwargs):
    # if instance.invoice.location == "Ecommerce":
    #     inv_item = sender.objects.filter(id=instance.id)
        
    #     if instance.invoice.payment > 0:
    #         if instance.product:
    #             if len(inv_item) > 0:
    #                 previous = inv_item[0]
    #                 diff = int(previous.quantity) - int(instance.quantity)
    #                 instance.product.quantity = instance.product.quantity + diff
    #                 instance.product.save()
    #             else:
    #                 instance.product.quantity = instance.product.quantity - instance.quantity
    #                 instance.product.save()
    # else:
    if instance.product:
        inv_item = sender.objects.filter(id=instance.id)
        if len(inv_item) > 0:
            previous = inv_item[0]
            diff = int(previous.quantity) - int(instance.quantity)
            instance.product.quantity = instance.product.quantity + diff
            instance.product.save()
        else:
            instance.product.quantity = instance.product.quantity - instance.quantity
            instance.product.save()

class online_order(models.Model):
    data = JSONField(null=True, blank=True)
    confirm = models.BooleanField(default=False)
    invoice_number = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class services(models.Model):
    """database model for invoice"""
    invoice = models.ForeignKey(
        invoice,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    employe = models.ForeignKey(
        contactModel.UserProfile,
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
    realter = models.BooleanField(default=False)
    data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(auto_now_add=True)

    # def __str__(self):
    #     """return string representation of invoice"""
    #     return "Servicces for Invoice No: " + str(self.invoice.invoice_number)


post_save.connect(notify_service_application, sender=services)
post_delete.connect(notify_service_deletion, sender=services)


@receiver(post_save, sender=services)
def update_Service_costing(sender, created, instance, **kwargs):
    if created is False:
        instance.invoice.save()
    elif instance.data  == "reload":
        instance.invoice.save()


@receiver(post_delete, sender=services)
def update_Invoice_costing(sender, instance, **kwargs):
    if instance.invoice:
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
    # Measurement_body = models.BooleanField(default=False)
    # Measurement_dress = models.BooleanField(default=False)
    body = 'body'
    dress = 'dress'
    Measurement_type = [
        (body, 'body'),
        (dress, 'dress'),
    ]
    Type = models.CharField(
        max_length=250,
        choices=Measurement_type,
        null=True,
        blank=True
    )
    Sleeve_less = models.BooleanField(default=False)
    # Sleeve_length = models.BooleanField(default=False)
    
    Blouse = models.BooleanField(default=False)
    Kameez = models.BooleanField(default=False)
    Gown = models.BooleanField(default=False)
    Skirt = models.BooleanField(default=False)
    Paladzo = models.BooleanField(default=False)
    Pant = models.BooleanField(default=False)
    Gharara = models.BooleanField(default=False)
    Gown_bottom = models.BooleanField(default=False)
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
    
    body = models.CharField(max_length=255, blank=True)
    mala = models.CharField(max_length=255, blank=True)
    pagri = models.CharField(max_length=255, blank=True)

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

    location = models.ForeignKey(
        productModel.Warehouse,
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
        contactModel.UserProfile,
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
            self.Details = productname
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
        productModel.Warehouse,
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

    def __str__(self):
        """return string representation of invoice"""
        return self.wordrobe_number


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
    
class Refund(models.Model):
    """database model for refund"""
    invoice = models.ForeignKey(
        invoice,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    in_account = models.ForeignKey(
        accountingModel.account,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="in_account",
        related_query_name="in_account",
    )
    out_account = models.ForeignKey(
        accountingModel.account,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="out_account",
        related_query_name="out_account",
    )
    amount = models.DecimalField(
        default=0, blank=True, null=True, max_digits=20, decimal_places=2)
    reason = models.CharField(max_length=255,null=True, blank=True)
    issue_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=255, blank=True)

class Refund_item(models.Model):
    """database model for refund"""
    Refunded_product = models.ForeignKey(
        productModel.ProductLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    quantity = models.IntegerField(default='1', blank=True, null=True)
    price = models.DecimalField(
        default=0, blank=True, null=True, max_digits=20, decimal_places=2)
    reason = models.CharField(max_length=255)
    issue_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=255, blank=True)
    deatils = models.CharField(max_length=2550, blank=True)

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


class IPN(models.Model):
    """database model for Ecommerce transactions"""
    tran_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(
        default=0, blank=True, max_digits=20, decimal_places=2)
    status = models.CharField(max_length=255, null=True, blank=True)
    card_type = models.CharField(max_length=255, null=True, blank=True)
    tran_date = models.DateTimeField(null=True, blank=True)
    issue_date = models.DateField(auto_now_add=True)


    def __str__(self):
        """return string representation of Cupon"""
        return self.tran_id