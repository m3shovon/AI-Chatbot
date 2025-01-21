from django.db import models
from product import models as productModel
from django.utils import timezone
from product import models as productModel
from contact import models as contactModel
from django.db.models.signals import post_save, post_delete, pre_save
from accounting.signals import *
from django.db.models import JSONField
from django.db import transaction
import threading

# Create your models here.
lock = threading.Lock()


class accountparent(models.Model):
    Type = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        """return string representation of account"""
        return self.name


class account(models.Model):
    """return string representation of account"""
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    account_no = models.CharField(max_length=255, blank=True, null=True)
    cash = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    txnCharge = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    accountparent = models.ForeignKey(
        "accountparent", on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)

    def __str__(self):
        """return string representation of account"""
        return self.name


class accountStatus(models.Model):
    """return string representation of account"""
    amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    account = models.ForeignKey(
        "account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    def __str__(self):
        """return string representation of account"""
        return self.account.name + " - " + str(self.amount)


class accountStatusByDate(models.Model):
    """return string representation of account"""
    created = models.DateField(default=timezone.now)
    # accountStatus = models.ManyToManyField(accountStatus)
    data = JSONField(null=True, blank=True)
    
    def __str__(self):
        """return string representation of account"""
        return str(self.created)
    
    


class chartofaccount(models.Model):
    """return string representation of account"""
    account_name = models.CharField(max_length=255)
    account_code = models.CharField(max_length=255, unique=True)
    group = models.ForeignKey(
        'chartofaccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="groupp",
        related_query_name="groupp",
    )
    sub_group = models.ForeignKey(
        'chartofaccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_groupp",
        related_query_name="sub_groupp",
    )
    Financial_statement = models.TextField(blank=True, null=True)
    normally_Debit = models.TextField(blank=True, null=True)
    status = models.TextField(null=True, blank=True)
    amount = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)

    def __str__(self):
        """return string representation of account"""
        return self.account_name


class journal(models.Model):
    """return string representation of journal entries"""
    chartofaccount = models.ForeignKey(
        chartofaccount,
        on_delete=models.CASCADE
    )
    outlet = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        productModel.ProductDetails,
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
    employe = models.ForeignKey(
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    invoice = models.ForeignKey(
        'order.invoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    purchasee = models.ForeignKey(
        'order.purchase',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    transfer = models.ForeignKey(
        productModel.transfer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    loan = models.ForeignKey(
        'hrm.Loan',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    payslip = models.ForeignKey(
        'hrm.PaySlip',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    account = models.ForeignKey(
        "account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    details = models.TextField(blank=True, null=True)
    voucher_type = models.TextField(blank=True, null=True)
    amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    increase = models.BooleanField(default=True, null=True, blank=True)
    is_checked = models.BooleanField(default=False, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    def __str__(self):
        details = ""
        if self.id:
            details += 'journal : ' + str(self.id)
        if self.invoice:
            details += ',  ' + 'Invoice : ' + str(self.invoice.invoice_number)

        if self.purchasee:
            details += ',  ' + 'Purchase : ' + \
                str(self.purchasee.purchase_number)
        if self.outlet:
            details += ',  ' + 'Outlet : ' + \
                str(self.outlet.name)
        return details

# @receiver(post_delete, sender=journal)
# def my_model_post_delete(sender, instance, **kwargs):
#     transaction.on_commit(lambda: journals_post_delete.delay(instance.id))
    
pre_save.connect(journals_pre_save, sender=journal)
post_save.connect(journals_post_save, sender=journal)
post_delete.connect(journals_post_delete, sender=journal)


class paymentvoucher(models.Model):
    """return string representation of account"""
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employee = models.ForeignKey(
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
  
    contact = models.ForeignKey(
        contactModel.contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    account = models.ForeignKey(
        "account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    invoice = models.ForeignKey(
        'order.invoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    purchasee = models.ForeignKey(
        'order.purchase',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    voucher_number = models.CharField(max_length=255)
    narration = models.TextField(null=True, blank=True)
    referance = models.TextField(null=True, blank=True)
    amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        """return string representation """
        return self.voucher_number


class paymentvoucheritems(models.Model):
    """return string representation of account"""
    chartofaccount = models.ForeignKey(
        'chartofaccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    paymentvoucher = models.ForeignKey(
        'paymentvoucher',
        on_delete=models.CASCADE,
    )
    contact = models.ForeignKey(
        contactModel.contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employee = models.ForeignKey(
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    account = models.ForeignKey(
        "account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    invoice = models.ForeignKey(
        'order.invoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    purchasee = models.ForeignKey(
        'order.purchase',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    narration = models.TextField(null=True, blank=True)
    increase = models.BooleanField(default=True, null=True, blank=True)
    amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)


post_save.connect(paymentvoucher_item_post_save, sender=paymentvoucheritems)


class receivevoucher(models.Model):
    """return string representation of account"""
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employee = models.ForeignKey(
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    contact = models.ForeignKey(
        contactModel.contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employee = models.ForeignKey(
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    account = models.ForeignKey(
        "account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    invoice = models.ForeignKey(
        'order.invoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    purchasee = models.ForeignKey(
        'order.purchase',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    voucher_number = models.CharField(max_length=255)
    narration = models.TextField(null=True, blank=True)
    referance = models.TextField(null=True, blank=True)
    amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        """return string representation """
        return self.voucher_number


class receivevoucheritems(models.Model):
    """return string representation of account"""
    chartofaccount = models.ForeignKey(
        'chartofaccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    receivevoucher = models.ForeignKey(
        'receivevoucher',
        on_delete=models.CASCADE,
    )
    contact = models.ForeignKey(
        contactModel.contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employee = models.ForeignKey(
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    account = models.ForeignKey(
        "account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    invoice = models.ForeignKey(
        'order.invoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    purchasee = models.ForeignKey(
        'order.purchase',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    narration = models.TextField(null=True, blank=True)
    increase = models.BooleanField(default=True, null=True, blank=True)
    amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)


post_save.connect(receivevoucher_item_post_save, sender=receivevoucheritems)


class journalvoucher(models.Model):
    """return string representation of account"""
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employee = models.ForeignKey(
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    contact = models.ForeignKey(
        contactModel.contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employee = models.ForeignKey(
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    account = models.ForeignKey(
        "account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    invoice = models.ForeignKey(
        'order.invoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    purchasee = models.ForeignKey(
        'order.purchase',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    voucher_number = models.CharField(max_length=255)
    narration = models.TextField(null=True, blank=True)
    referance = models.TextField(null=True, blank=True)
    amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    debit = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    credit = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    is_payment_voucher = models.BooleanField(default=False)
    is_receive_voucher = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        """return string representation """
        return self.voucher_number


class journalvoucheritems(models.Model):
    """return string representation of account"""
    chartofaccount = models.ForeignKey(
        'chartofaccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    journalvoucher = models.ForeignKey(
        'journalvoucher',
        on_delete=models.CASCADE,
    )
    contact = models.ForeignKey(
        contactModel.contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employee = models.ForeignKey(
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    account = models.ForeignKey(
        "account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    invoice = models.ForeignKey(
        'order.invoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    purchasee = models.ForeignKey(
        'order.purchase',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    narration = models.TextField(null=True, blank=True)
    increase = models.BooleanField(default=True, null=True, blank=True)
    amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    is_printable = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)


post_save.connect(journalvoucher_item_post_save, sender=journalvoucheritems)


class contravoucher(models.Model):
    """return string representation of account"""

    accountFrom = models.ForeignKey(
        "account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accountFrom'
    )
    accountTo = models.ForeignKey(
        "account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accountTo'
    )
    employee = models.ForeignKey(
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    voucher_number = models.CharField(max_length=255)
    narration = models.TextField(null=True, blank=True)
    referance = models.TextField(null=True, blank=True)
    amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        """return string representation """
        return self.voucher_number


post_save.connect(contravoucher_post_save, sender=contravoucher)


class pettycash(models.Model):
    """return string representation of account"""
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    employee = models.ForeignKey(
        contactModel.UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    narration = models.CharField(max_length=900)
    amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    increase = models.BooleanField(default=True, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    
    
    def __str__(self):
        """return string representation """
        return self.employee.name + ' - ' + str(self.amount) + ' - ' + self.location.name


post_save.connect(petty_cash_save, sender=pettycash)


class pettycash_transfer(models.Model):
    location = models.ForeignKey(
        productModel.Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    account = models.ForeignKey(
        "account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cash_amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    pett_cash_amount = models.DecimalField(
        default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    collect_cash = models.BooleanField(default=False, null=True, blank=True)
    add_cash = models.BooleanField(default=False, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(default=timezone.now)


post_save.connect(pettycash_transfer_save, sender=pettycash_transfer)
