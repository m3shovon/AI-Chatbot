# from unicodedata import category
# from tkinter import CASCADE
import uuid
from django.db import models
from order.models import DraftCostSheet, DraftOrder, DraftImage, services
from hrm.models import Office
from product.models import Attribute, AttributeTerm, Category, ProductDetails, ProductLocation


from django.db.models import JSONField
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from order.signals import *
# Create your models here.


class WorkOrder(models.Model):
    draft_cost_sheet = models.ForeignKey(
        DraftCostSheet, on_delete=models.CASCADE, blank=True, null=True)
    order_name = models.CharField(max_length=255, blank=True, null=True)
    order_number = models.CharField(max_length=255, blank=True, null=True)
    Product = models.ForeignKey(ProductDetails,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True)
    service = models.ForeignKey(services,on_delete=models.SET_NULL,
                                null=True,
                                blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    quantity_needed = models.IntegerField(default=0)
    
    quantity_pending = models.IntegerField(default=0)
    quantity_complete = models.IntegerField(default=0)
    quantity_damaged = models.IntegerField(default=0)
    
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)
    status = models.CharField(max_length=100, null=True, default="Pending", blank=True)

    def __str__(self):
        return f'{self.order_name} - {self.order_number}'

    def save(self, *args, **kwargs):  
        productline_items = WorkOrderItem.objects.filter(Workorder=self.id)
        quantity_needed = 0
        quantity_pending = 0
        quantity_complete = 0
        for productline_item in productline_items:
            quantity_needed += productline_item.quantity_needed
            quantity_pending += productline_item.quantity_pending
            quantity_complete += productline_item.quantity_complete
        self.quantity_pending = quantity_pending
        self.quantity_complete = quantity_complete
        self.quantity_needed = quantity_needed
        if self.quantity_needed ==  self.quantity_complete:
            self.status = "Complete"
        else:
            self.status = "Pending"        
        super().save(*args, **kwargs)

class WorkOrderItem(models.Model):
    Workorder = models.ForeignKey(
        WorkOrder, on_delete=models.CASCADE)
    Attributes = models.ManyToManyField(AttributeTerm,
                                        blank=True,
                                        related_name="AttributeTerm",
                                        related_query_name="AttributeTerm",)
    quantity_needed = models.IntegerField(default=0)
    
    quantity_pending = models.IntegerField(default=0)
    quantity_complete = models.IntegerField(default=0)
    quantity_damaged = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.Workorder.order_name} - {self.quantity_needed}'

    def save(self, *args, **kwargs):
        productline_items = ProductionLine_item.objects.filter(WorkOrderItem=self.id)
        quantity_pending = 0
        quantity_complete = 0
        for productline_item in productline_items:
            quantity_pending += productline_item.quantity_pending
            quantity_complete += productline_item.quantity_complete
        self.quantity_pending = quantity_pending
        self.quantity_complete = quantity_complete
        super().save(*args, **kwargs)

@receiver(post_save, sender=WorkOrderItem)
def update_WorkOrder(sender, created, instance, **kwargs):
    Workorder = WorkOrder.objects.get(id=instance.Workorder.id)
    Workorder.save()


class ProductionLine(models.Model):
    line_name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    capacity_consumed = models.IntegerField(default=0)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, default="Pending", blank=True)
    
    def save(self, *args, **kwargs):
        capacity_consumed = 0
        pending = 0
        ongoing = 0
        complete = 0
        processes = ProductionLine_item.objects.filter(ProductionLine = self.id)
        WorkstationItem = WorkstationItems.objects.filter(ProductionLine = self.id)
        for process in processes:
            capacity_consumed += process.capacity
            if process.status == 'Pending':
                pending  += 1
            elif process.status == 'Complete':
                complete += 1
            else:
                ongoing += 1
        if pending != 0:
            self.status = 'Pending'
        if ongoing != 0:
            self.status = 'Ongoing'
        if pending == 0 and ongoing == 0:
            self.status = 'Complete'
        if len(WorkstationItem) == 0:
            self.status = 'Initial'
            
        self.capacity_consumed = capacity_consumed
            
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.line_name} - {self.location}'




class ProductionLine_item(models.Model):
    PENDING = 'Pending'
    WORKING = 'Working'
    TESTING = 'Testing'
    COMPLETE = 'Complete'
    WORK_STATUS = [
        (PENDING, 'Pending'),
        (WORKING, 'Working'),
        (TESTING, 'Testing'),
        (COMPLETE, 'Complete'),
    ]
    ProductionLine = models.ForeignKey(
        ProductionLine, on_delete=models.CASCADE)
    Workorder = models.ForeignKey(
        WorkOrder, on_delete=models.CASCADE)
    WorkOrderItem = models.ForeignKey(
        WorkOrderItem, on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField()
    
    quantity_pending = models.IntegerField(default=0)
    quantity_complete = models.IntegerField(default=0)
    quantity_damaged = models.IntegerField(default=0)
    
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=100, choices=WORK_STATUS, null=True)
    

    def __str__(self):
        return f'{self.ProductionLine.line_name} - {self.Workorder.order_name}'
    
    def save(self, *args, **kwargs):
        if self.status == "Complete":
            self.quantity_complete = self.capacity
            self.quantity_pending = 0
        else:
            self.quantity_pending = self.capacity
            self.quantity_complete = 0
        super().save(*args, **kwargs)

@receiver(pre_save, sender=ProductionLine_item)
def update_ProductionLine(sender, instance, **kwargs):
    prev = sender.objects.filter(id=instance.id)
    if len(prev) > 0:
        previous = prev[0]
        if previous.status != "Complete" and instance.status == "Complete":
            # available product details
            product = instance.Workorder.Product
            Attributes = instance.WorkOrderItem.Attributes
            WorkOrderItem = instance.WorkOrderItem
            print(instance.Workorder.Product)
            # get all the product variations
            variations = ProductLocation.objects.filter(ProductDetails=instance.Workorder.Product.id)
            match = 0
            for variation in variations:
                if list(variation.Attributes.all()) == list(instance.WorkOrderItem.Attributes.all()):
                    # print("Match")
                    match = variation
            if match != 0:
                # update variation
                match.quantity = match.quantity + instance.capacity
                match.save()
            else:
                warehouse = Office.objects.all().first()
                newvariation = ProductLocation.objects.create(ProductDetails=product, Warehouse=warehouse,quantity=instance.capacity)
                for attribute in Attributes.all():
                    print(attribute)
                    newvariation.Attributes.add(attribute)
                newvariation.save()
        elif previous.status == "Complete" and instance.status != "Complete":
            # available product details
            product = instance.Workorder.Product
            Attributes = instance.WorkOrderItem.Attributes
            WorkOrderItem = instance.WorkOrderItem
            
            # get all the product variations
            variations = ProductLocation.objects.filter(ProductDetails=product.id)
            match = 0
            for variation in variations:
                if list(variation.Attributes.all()) == list(instance.WorkOrderItem.Attributes.all()):
                    # print("Match")
                    match = variation
            if match != 0:
                # update variation
                match.quantity = match.quantity - instance.capacity
                match.save()
            else:
                warehouse = Office.objects.all().first()
                newvariation = ProductLocation.objects.create(ProductDetails=product, Warehouse=warehouse,quantity=instance.capacity)
                for attribute in Attributes.all():
                    print(attribute)
                    newvariation.Attributes.add(attribute)
                newvariation.save()
        
    Productionline = ProductionLine.objects.get(id=instance.ProductionLine.id)
    Productionline.save()
    
@receiver(post_save, sender=ProductionLine_item)
def update_ProductionLine(sender, created, instance, **kwargs):
    Productionline = ProductionLine.objects.get(id=instance.ProductionLine.id)
    Productionline.save()
    instance.WorkOrderItem.save()

@receiver(post_delete, sender=ProductionLine_item)
def update_ProductionLine(sender, instance, **kwargs):
    Productionline = ProductionLine.objects.get(id=instance.ProductionLine.id)
    Productionline.save()
    instance.WorkOrderItem.save()


class Workstation(models.Model):
    workstation_name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=100, null=True, default="Pending", blank=True)
    
# WorkStation Signal
class WorkstationItems(models.Model):
    Workstation = models.ForeignKey(
        Workstation, on_delete=models.CASCADE, null=True)
    ProductionLine = models.ForeignKey(
        ProductionLine, on_delete=models.CASCADE, null=True)
    

class Manufacture_Cost(models.Model):
    ProductionLine = models.ForeignKey(
        ProductionLine, on_delete=models.CASCADE)
    ProductionLine_item = models.ForeignKey(
        ProductionLine_item, on_delete=models.CASCADE)
    Product = models.ForeignKey(ProductDetails,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True)
    ProductLocation = models.ForeignKey(
        ProductLocation, on_delete=models.SET_NULL,
                                null=True,
                                blank=True)
    
    FABRICS = 'Fabrics'
    TRIMS_ACCESSORIES = 'Trims/Accessories'
    LABOR_COST = 'Labor Cost'
    COST_SHEET_ITEMS_CHOICES = [
        (FABRICS, 'Fabrics'),
        (TRIMS_ACCESSORIES, 'Trims/Accessories'),
        (LABOR_COST, 'Labor Cost'),
    ]
    type = models.CharField(
        max_length=100, choices=COST_SHEET_ITEMS_CHOICES, null=True)
    
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    unit_name = models.CharField(max_length=10, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    cost_per_unit = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)

    # def __str__(self):
    #     return f'{self.material_name} - {self.ProductionLine}'

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.cost_per_unit

        super().save(*args, **kwargs)


# @receiver(post_delete, sender=RawMaterial)
# @receiver(post_save, sender=RawMaterial)
# def update_work_order(sender, instance, **kwargs):
#     work_order = instance.order_id
#     if work_order is not None:
#         work_order.save()






class WorkstationStatus(models.Model):
    NEW = 'New'
    PROPOSED = 'Proposed'
    CONFIRM = 'Confirm'
    SOLVED = 'Solved'
    WORK_STATUS = [
        (NEW, 'New'),
        (PROPOSED, 'Proposed'),
        (CONFIRM, 'Confirm'),
        (SOLVED, 'Solved'),
    ]
    task_name = models.CharField(max_length=100)
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=WORK_STATUS, null=True)

    def __str__(self):
        return f'{self.task_name} - {self.workstation} - {self.status}'

# WorkStationStatus Signal


@receiver(post_save, sender=Workstation)
def update_workstation_status_on_workstation_save(sender, instance, **kwargs):
    workstation = instance
    workstation_status = WorkstationStatus.objects.filter(
        workstation=workstation).first()
    if workstation_status is not None:
        workstation_status.save()


@receiver(post_delete, sender=Workstation)
def update_workstation_status_on_workstation_delete(sender, instance, **kwargs):
    workstation = instance
    workstation_status = WorkstationStatus.objects.filter(
        workstation=workstation).first()
    if workstation_status is not None:
        workstation_status.save()




@receiver(post_save, sender=Workstation)
@receiver(post_delete, sender=Workstation)
def update_workstation_status(sender, instance, **kwargs):
    workstation = instance
    workstation_status = WorkstationStatus.objects.filter(
        workstation=workstation).first()
    if workstation_status is not None:
        workstation_status.save()


class QualityTestStatus(models.Model):
    BLOCK = 'Block'
    QUALITY = 'Quality'
    SCRAP = 'Scrap'
    MAINTENANCE = 'Maintenance'
    TEST_TYPE_STATUS = [
        (BLOCK, 'Block'),
        (QUALITY, 'Quality'),
        (SCRAP, 'Scrap'),
        (MAINTENANCE, 'Maintenance'),
    ]
    status = models.CharField(
        max_length=100, choices=TEST_TYPE_STATUS, null=True)
    order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, null=True,
                              blank=True)
    ProductionLine_item = models.ForeignKey(ProductionLine_item, on_delete=models.CASCADE, null=True,
                                            blank=True)

    def __str__(self):
        return f'{self.order} - {self.status}'


class QualityTest(models.Model):
    test_type = models.ForeignKey(QualityTestStatus, on_delete=models.CASCADE)
    test_date = models.DateField()
    pass_fail_status = models.BooleanField()
    notes = models.TextField()

    def __str__(self):
        return f'{self.test_type} - {self.test_date} - {self.pass_fail_status}'


class ManufacturingRecord(models.Model):
    order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)
    line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE)
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField()


# class BillOfMaterials(models.Model):
#     raw_materials = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
#     quantity_needed = models.IntegerField()
#     total_cost = models.DecimalField(max_digits=10, decimal_places=2)
