from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from notifications.signals import notify
from contact.models import UserProfile
from notifications.models import Notification 
from product import models as ProductModule

def transfer_item_post_save(sender, instance, created, update_fields, **kwargs):
    print("postsave--------------------")
    source = instance.transfer.source
    destination = instance.transfer.destance
    productlocation = instance.product
    quantity = instance.quantity
    
    # if it is a new transfer
    if created:
        print("Update source item")
        # update the source object
        productlocation.quantity = productlocation.quantity - quantity
        productlocation.save()

def transfer_item_pre_save(sender, instance, **kwargs):
    print("presave--------------------")
    source = instance.transfer.source
    destination = instance.transfer.destance
    productlocation = instance.product
    quantity = instance.quantity
    
    allObjects = sender.objects.filter(id=instance.id)
    
    # if the product was not received
    # if the product is reveived now.
    if len(allObjects) > 0:
        previous_transfer_item = allObjects[0]
        if not previous_transfer_item.is_received:
            if instance.is_received:
                # update the destination object
                # get all the variations
                variations = ProductModule.ProductLocation.objects.filter(ProductDetails=productlocation.ProductDetails)
                flag = 0
                for variation in variations:
                    # checking all variation if the transfer product already exists
                    if destination == variation.Warehouse and productlocation.Size == variation.Size and productlocation.Color == variation.Color:
                        # updating the matched variation
                        print("Update existing desination item")
                        flag = 1
                        variation.quantity = variation.quantity + quantity
                        variation.save()
                        
                if flag == 0:
                    # create a new variation
                    print("create desination item")
                    new_variation = ProductModule.ProductLocation(Warehouse=destination, Color=productlocation.Color, Size=productlocation.Size,ProductDetails=productlocation.ProductDetails)
                    new_variation.quantity = quantity
                    new_variation.purchase_price = productlocation.purchase_price
                    new_variation.selling_price = productlocation.selling_price
                    new_variation.save()
        if not previous_transfer_item.is_returned:
            if instance.is_returned:
                productlocation.quantity = productlocation.quantity + quantity
                productlocation.save()

    
def transfer_item_pre_delete(sender, instance, **kwargs):
    print("delete--------------------------")
    source = instance.transfer.source
    destination = instance.transfer.destance
    productlocation = instance.product
    quantity = instance.quantity
    
    if instance.is_received:
        # get all the variations
        variations = ProductModule.ProductLocation.objects.filter(ProductDetails=productlocation.ProductDetails)
        flag = 0
        for variation in variations:
            # checking all variation
            if destination == variation.Warehouse and productlocation.Size == variation.Size and productlocation.Color == variation.Color:
                # updating the destination variation
                flag = 1
                variation.quantity = variation.quantity - quantity
                variation.save()
            # checking all variation
    if not instance.is_returned:
        productlocation.quantity = productlocation.quantity + quantity
        productlocation.save()

def notify_transfer_application(sender, instance, created, update_fields, **kwargs):
    """
    Notify about transfer application
    """

    source = instance.source
    # source = Warehouse.objects.get(id=source)
    destination = instance.destance
    # destination = Warehouse.objects.get(id=destination)

    if created:
        '''Sending Notifications to the destination'''
        employeeList = UserProfile.objects.filter(branch=destination)
        for employee in employeeList:
            message = f"Hello {employee.name},\n\nYou have a new transfer request from {source.name} to {destination.name}.\n\nKindly review the request and Accept it.\n\nThank you."
            notify.send(instance, recipient=employee, description='transfer', verb= message)
            # sendEmail(employee, employee.email, "Transfer Request", message)
        '''End Of Sending Notifications'''
    else:
        status = instance.status
        if status == 'Received':
            '''Sending Notifications to the source'''
            employeeList = UserProfile.objects.filter(branch=source)
            for employee in employeeList:
                message = f"Hello {employee.name}, \n\nYour transfer request from {source.name} to {destination.name} has been accepted.\n\nThank you."
                notify.send(instance, recipient=employee, description='transfer', verb= message)
                # sendEmail(employee, employee.email, "Leave Request Status", message)
            '''End Of Sending Notifications'''

def notify_transfer_deletion(sender, instance, **kwargs):
    notify = Notification.objects.filter(actor_object_id=instance.id, description='transfer')
    notify.delete()


def sendEmail(user, to_email, subject, customMessage):
    # current_site = get_current_site(request)
    mail_subject = subject
    message = render_to_string('email_template.html', {
        'user': user,
        # 'domain': current_site.domain,
        'message': customMessage
    })
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.content_subtype = 'html'
    email.send(fail_silently=True)