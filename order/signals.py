from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from notifications.signals import notify
# from contact.models import UserProfile, userRole
from hrm.models import Employee, Designation
from order.models import *
from order import models as order_models
from product.models import *
from accounting.models import *
from notifications.models import Notification
from decimal import Decimal
import requests
from django.db.models import Q
import datetime


def notify_service_application(sender, instance, created, update_fields, **kwargs):
    """
    Notify about service application
    """
    # if instance.Payment_method != "Cash":
    #     # print("--------Start-------")
    #     inv = sender.objects.get(id=instance.id)
    #     # print(inv.payment)
    #     # print(instance.payment)
    #     act = account.objects.get(
    #         id=instance.account.id)
    #     # print(act.cash)
    #     diff = abs(Decimal(instance.payment) - Decimal(inv.payment))
    #     act.cash = Decimal(act.cash) + Decimal(diff)
    #     # print(act.cash)
    #     act.save()
    #     # print("--------End-------")
    #     # print(act.cash)
    # else:
    #     location = instance.location
    #     inv = sender.objects.get(id=instance.id)
    #     diff = abs(Decimal(instance.payment) - Decimal(inv.payment))
    #     location.cash = Decimal(location.cash) + Decimal(diff)
    #     location.save()

    salesPersone = instance.invoice.employe
    warehouse = instance.invoice.location
    # all_warehouse = Warehouse.objects.filter(is_outlet=False)
    if created:
        '''Sending Notifications to the destination'''
        factory_managers = Employee.objects.filter(Q(Designation__name__icontains="factory manager")
                                                   | Q(Designation__name__icontains="factory")).distinct()
        # # print(factory_managers)
        for factoryManager in factory_managers:
            # print(factoryManager.name)
            # print(employee.name)
            message = f"Hello {factoryManager.name}, {salesPersone.name} Has Applied for a Service of {instance.price} Taka."
            notify.send(instance, recipient=factoryManager,
                        description='services', verb=message)
            # sendEmail(superuser, superuser.email, "Services Request", message)
        '''End Of Sending Notifications'''
    else:
        status = instance.status
        '''Sending Notifications to the source'''
        employeeList = Employee.objects.filter(Office=warehouse)
        for employee in employeeList:
            message = f"Hello {employee.name}, Your Service Request Status is {status}."
            notify.send(instance, recipient=employee,
                        description='services', verb=message)
            # sendEmail(employee, employee.email, "Service Request Status", message)
        '''End Of Sending Notifications'''


def notify_service_deletion(sender, instance, **kwargs):
    notify = Notification.objects.filter(
        actor_object_id=instance.id, description='services')
    notify.delete()


def invoice_post_save(sender, instance, created, update_fields, **kwargs):
    # print(instance)
    """
    Notify about customer purchase application
    """
    contact = instance.contact
    amount = instance.bill
    payment = instance.payment
    due = instance.due
    refund = instance.refund
    vat = instance.tax
    discount = instance.discount
    cost = instance.costing
    delivery_cost = instance.delivery_cost
    outlet = instance.location
    invoice_id = instance.id
    account = instance.account
    details = "Sell with invoice no: " + str(instance.invoice_number)
    current_site = get_current_site(None)
    if created:
        # print("New Invoice Created")
        '''Sending Notifications to the customer'''
        if contact.email != "" and contact.email != None:
            if payment == 0 or payment == None:
                message = f"Hello {contact.name}, We Got Your Order Request. Your Invoice number is: {instance.invoice_number}. Follow this link to see the full invoice: {current_site}/invoice/{instance.id}. We Will keep you updated with the status of your purchase."
            else:
                message = f"Hello {contact.name}, You made a payment of  {payment} for Invoice #{instance.invoice_number}. Follow this link to see the full invoice: {current_site}/invoice/{instance.id}."

            # notify.send(instance, recipient=superuser, description='services', verb=message)
            sendEmail(contact, contact.email, "Order Request", message)
            # sending sms
            if contact.phone != "" and contact.phone != None:
                sendSms(contact.phone, message)

        ########### Telegram BOT for Solo ############
        # message = f"{instance.invoice_number} - Paid:{instance.payment} - Discount:{instance.discount}"
        # baseurl = baseurl = 'https://api.telegram.org/bot6914683636:AAGDKxR8cC8RpjH7X-OPPazBe_oyVnWH13w/sendMessage?chat_id=-4075976666&text="{}"'.format(message)
        # requests.get(baseurl)

        #### Main TELEGRAM BOT #####         
        # telegram_message = f"{instance.invoice_number} - Paid:{instance.payment} - Discount:{instance.discount}"
        # print("===============",outlet.name)
        # if outlet.name == "Cotton Club":
        #     baseurl = 'https://api.telegram.org/bot7049328635:AAGDof0B-2cIUGks7SmDlW-cA81oA2gZUtM/sendMessage?chat_id=-4075976666&text="{}"'.format(telegram_message)
        # elif outlet.name == "Nur Creation":
        #     baseurl = 'https://api.telegram.org/bot6914683636:AAGDKxR8cC8RpjH7X-OPPazBe_oyVnWH13w/sendMessage?chat_id=-4075976666&text="{}"'.format(telegram_message)
        # requests.get(baseurl)
      
        '''End Of Sending Notifications'''
        # cash on hand
        if account.type == "Cash":
            CashOnHandCode = settings.CASH
        else:
            CashOnHandCode = settings.BANK
        cash_on_hand = chartofaccount.objects.get(account_code=CashOnHandCode)
        increase_or_decrease = True
        # print("payment - " + str(payment))
        jour = journal.objects.create(chartofaccount=cash_on_hand, invoice=instance, account=account, outlet=outlet,
                                      contact=contact, details=details, amount=(payment - instance.advance_payment), increase=increase_or_decrease)
        # accounts recevable
        receivable = amount - payment
        if receivable != 0:
            accounts_receivable = chartofaccount.objects.get(
                account_code=settings.ACCOUNTS_RECEIVABLE)
            increase_or_decrease = True
            # print("due - " + str(due))
            jour = journal.objects.create(chartofaccount=accounts_receivable, invoice=instance, outlet=outlet,
                                          contact=contact, details=details, amount=receivable, increase=increase_or_decrease)
        # advance from customer
        if instance.advance_payment > 0:
            accounts_receivable = chartofaccount.objects.get(
                account_code=settings.ACCOUNTS_PAYABLE)
            increase_or_decrease = False
            # print("accounts payable - " + str(instance.advance_payment))
            advance_from_customer = chartofaccount.objects.get(
                account_code=settings.ADVANCE_FROM_CUSTOMERS)
            jour = journal.objects.create(chartofaccount=advance_from_customer, invoice=instance, outlet=outlet,
                                          contact=contact, details=details, amount=instance.advance_payment, increase=increase_or_decrease)

        # discount
        if discount != 0:
            discount_account = chartofaccount.objects.get(
                account_code=settings.SALES_DISCOUNT)
            increase_or_decrease = True
            jour = journal.objects.create(chartofaccount=discount_account, invoice=instance, outlet=outlet,
                                          contact=contact, details=details, amount=discount, increase=increase_or_decrease)

        # sales revenue
        sales_revenue = chartofaccount.objects.get(
            account_code=settings.SALES_REVENUE)
        increase_or_decrease = True
        if discount > 0:
            sales_amount = Decimal(amount) + Decimal(discount)
        else:
            sales_amount = Decimal(amount)
        # print("sales_amount - " + str(sales_amount))
        jour = journal.objects.create(chartofaccount=sales_revenue, invoice=instance, outlet=outlet,
                                      contact=contact, details=details, amount=sales_amount, increase=increase_or_decrease)
        # cost of good sold
        cost_of_good_sold = chartofaccount.objects.get(
            account_code=settings.COST_OF_GOOD_SOLD)
        increase_or_decrease = True
        # print("cost - " + str(cost))
        jour = journal.objects.create(chartofaccount=cost_of_good_sold, invoice=instance, outlet=outlet,
                                      contact=contact, details=details, amount=cost, increase=increase_or_decrease)
        # inventory asset
        inventory = chartofaccount.objects.get(
            account_code=settings.INVENTORY_ASSETS)
        increase_or_decrease = False
        # print("inventory asset - " + str(cost))
        jour = journal.objects.create(chartofaccount=inventory, invoice=instance, outlet=outlet, contact=contact, details=details, amount=cost, increase=increase_or_decrease)
        
        # VAT Generate
        if instance.due == 0:  
            # VAT issue date is updated from model while create

            # VAT payable
            details = "VAT payable for invoice no: " + str(instance.invoice_number)

            vat_account = chartofaccount.objects.get(
                account_code=settings.VAT_PAYABLE)
            increase_or_decrease = True
            jour = journal.objects.create(chartofaccount=vat_account, invoice=instance, outlet=outlet, contact=contact, details=details, amount=instance.tax, increase=increase_or_decrease)

            # Sales revenue
            details = "Sell with invoice no: " + str(instance.invoice_number)
            sales_revenue = chartofaccount.objects.get(
                account_code=settings.SALES_REVENUE)
            increase_or_decrease = False
            sales_revenue_jour = journal.objects.create(chartofaccount=sales_revenue, invoice=instance, outlet=outlet, contact=contact, details=details, amount=instance.tax, increase=increase_or_decrease)
        
        # create a invoice payment
        if instance.payment > 0:
            new_invoice_payment = order_models.invoice_payment.objects.create(invoice=instance, account=instance.account, Sales_person=instance.Sales_person,
                                                                quantity=instance.quantity, bill=instance.bill,due=instance.due,refund=instance.refund,
                                                                discount=instance.discount, tax=instance.tax, payment=instance.payment,
                                                                advance_payment=0)

    else:
        # print("Invoice Status Update")
        status = instance.status
        '''Sending Notifications to the customer'''
        if status == 'Delivered':
            # vat
            if vat != 0:
                vat_account = chartofaccount.objects.get(
                    account_code=settings.VAT_PAYABLE)
                increase_or_decrease = True
                jour, _ = journal.objects.get_or_create(chartofaccount=vat_account, invoice=instance, outlet=outlet,
                                                        contact=contact, increase=increase_or_decrease)
                jour.amount = vat
                jour.details = details
                jour.save()

                # Sales revenue
                sales_revenue = chartofaccount.objects.get(
                    account_code=settings.SALES_REVENUE)
                increase_or_decrease = False
                sales_revenue_jour = journal.objects.create(chartofaccount=sales_revenue, invoice=instance, outlet=outlet,
                                                            contact=contact, details=details, amount=vat, increase=increase_or_decrease)
                sales_revenue_jour.save()
        if contact.email != "" and contact.email != None and status == 'Delivered':
            message = f"Hello {contact.name}, Your Order Request is {status} of Invoice #{instance.invoice_number}. Follow this link to see the full invoice: {current_site}/invoice/{instance.id}."
            # notify.send(instance, recipient=superuser, description='services', verb=message)
            sendEmail(contact, contact.email,
                      "Order Request Status", message)
            # sending sms
            if contact.phone != "" and contact.phone != None:
                sendSms(contact.phone, message)

            # message = f"{contact.name} made a update on Invoice # {instance.invoice_number}."
            # baseurl = 'https://api.telegram.org/bot6914683636:AAGDKxR8cC8RpjH7X-OPPazBe_oyVnWH13w/sendMessage?chat_id=#6252780791&text="{}"'.format(message)
            # requests.get(baseurl)   

        '''End Of Sending Notifications'''


def invoice_post_delete(sender, instance, **kwargs):
    # deleting all notification connected to that invoice
    # message = f"Deleted Invoice:{instance.invoice_number}"
    # baseurl = 'https://api.telegram.org/bot6914683636:AAGDKxR8cC8RpjH7X-OPPazBe_oyVnWH13w/sendMessage?chat_id=-4075976666&text="{}"'.format(message)
    # requests.get(baseurl)       
    notify = Notification.objects.filter(
        actor_object_id=instance.id, description='invoice')
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


def sendSms(to_number, customMessage, user=None):
    if settings.SMS_ENABLED is False:
        return None  # currently for development purpose
    message = customMessage

    if to_number.startswith('+88'):
        number = to_number[1:]  # remove + from number
    elif to_number.startswith('88'):
        number = to_number  # number is already in international format
    elif to_number.startswith('0'):
        number = '88' + to_number  # add country code
    else:
        # print("Invalid Phone or Message")
        return False

    if number is not None and len(number) == 13 and number.startswith('88') and message is not None:
        # api end point
        URL = settings.SMS_HOST_URL
        # PARAMS = {
        #     "APIKey": settings.SMS_API_KEY,
        #     "senderid": settings.SMS_API_SENDER_ID,
        #     "channel": settings.SMS_CHANNEL,
        #     "DCS": settings.SMS_DCS,
        #     "flashsms": settings.SMS_FLASH,
        #     "number": number,
        #     "text": message
        # }
        PARAMS = {
            "apikey": settings.SMS_API_KEY,
            "secretkey": settings.SMS_SECRET_KEY,
            "callerID": settings.SMS_API_SENDER_ID,
            "toUser": number,
            "messageContent": message
        }
        response = requests.get(url=URL, params=PARAMS)
        JsonResponse = response.json()
        return True
        # return JsonResponse['ErrorCode'] == '000'
    else:
        # print("Invalid Phone or Message")
        return False


def invoice_pre_save(sender, instance, **kwargs):

    inv = sender.objects.filter(id=instance.id)
    account = instance.account
    txnCharge = account.txnCharge
    contact = instance.contact
    outlet = instance.location
    current_site = get_current_site(None)

    if instance.Payment_method != "Cash":
        # print("--------Start-------")
        if len(inv) > 0:
            invv = inv[0]
            diff = abs(Decimal(instance.payment) - Decimal(invv.payment))
            transactionCharge = Decimal(
                diff) * Decimal(txnCharge) * Decimal(0.01)
            account.cash = (Decimal(account.cash) + Decimal(diff)
                            ) - Decimal(transactionCharge)
            account.save()
            if transactionCharge > 0:
                # bank charges calculation and journal entry
                bank_charge = chartofaccount.objects.get(
                    account_code=settings.BANK_COMMISSION)
                increase_or_decrease = True
                details = "Transaction Charge " + \
                    str(txnCharge) + "%" + "For Invoice#" + \
                    str(instance.invoice_number)
                jour = journal.objects.create(chartofaccount=bank_charge, invoice=instance, account=account, outlet=outlet,
                                              contact=contact, details=details, amount=transactionCharge, increase=increase_or_decrease)

                bank = chartofaccount.objects.get(account_code=settings.BANK)
                increase_or_decrease = False
                details = "Transaction Charge " + \
                    str(txnCharge) + "%" + "For Invoice#" + \
                    str(instance.invoice_number)
                jour = journal.objects.create(chartofaccount=bank, invoice=instance, account=account, outlet=outlet,
                                              contact=contact, details=details, amount=transactionCharge, increase=increase_or_decrease)

        else:
            transactionCharge = Decimal(
                instance.payment) * Decimal(txnCharge) * Decimal(0.01)
            account.cash = (
                Decimal(account.cash) + Decimal(instance.payment)) - Decimal(transactionCharge)
            account.save()
            # print("Payment: ", instance.payment)
            # print("Txn Charge: ", txnCharge)
            # print("Txn Charge Amount: ", transactionCharge)
            if transactionCharge > 0:
                # bank charges calculation and journal entry
                bank_charge = chartofaccount.objects.get(
                    account_code=settings.BANK_COMMISSION)
                increase_or_decrease = True
                details = "Transaction Charge " + \
                    str(txnCharge) + "%, " + "For Invoice#" + \
                    str(instance.invoice_number)
                jour = journal.objects.create(chartofaccount=bank_charge, account=account, outlet=outlet,
                                              contact=contact, details=details, amount=transactionCharge, increase=increase_or_decrease)

                bank = chartofaccount.objects.get(account_code=settings.BANK)
                increase_or_decrease = False
                details = "Transaction Charge " + \
                    str(txnCharge) + "%, " + "For Invoice#" + \
                    str(instance.invoice_number)
                jour = journal.objects.create(chartofaccount=bank_charge, account=account, outlet=outlet,
                                              contact=contact, details=details, amount=transactionCharge, increase=increase_or_decrease)

    else:
        location = instance.location

        if len(inv) > 0:
            invv = inv[0]
            diff = abs(Decimal(instance.payment) - Decimal(invv.payment))
            location.cash = Decimal(location.cash) + Decimal(diff)
            location.save()
        else:
            location.cash = Decimal(location.cash) + Decimal(instance.payment)
            location.save()
    # print("--------End-------")

    # checking if new entry or update

    # print(inv)
    if len(inv) > 0:
        invv = inv[0]
        diff = abs(Decimal(instance.payment) - Decimal(invv.payment))

        details = "Sell with invoice no: " + str(instance.invoice_number)

        # Vat payment date
        if instance.status == "Delivered" and invv.status != "Delivered":
            instance.Vat_issued_date = datetime.date.today()

        if diff != 0:  # if payment is changed
            if diff < 0:
                increase_or_decrease = True
            else:
                increase_or_decrease = False
                
            # create a invoice payment
            new_invoice_payment = order_models.invoice_payment.objects.create(invoice=instance, account=instance.account, Sales_person=instance.Sales_person,
                                                                 quantity=instance.quantity, bill=instance.bill,due=instance.due,
                                                                 discount=instance.discount, tax=instance.tax, payment=diff,
                                                                 advance_payment=invv.payment)
            diff = abs(diff)
            # cash on hand
            if account.type == "Cash":
                CashOnHandCode = settings.CASH
            else:
                CashOnHandCode = settings.BANK

            cash_on_hand = chartofaccount.objects.get(
                account_code=CashOnHandCode)
            jour = journal.objects.create(chartofaccount=cash_on_hand, invoice=instance, account=account, outlet=outlet,
                                          contact=contact, details=details, amount=diff, increase=(not increase_or_decrease))

            # accounts recevable
            accounts_receivable = chartofaccount.objects.get(
                account_code=settings.ACCOUNTS_RECEIVABLE)
            jour = journal.objects.create(chartofaccount=accounts_receivable, invoice=instance, outlet=outlet,
                                          contact=contact, details=details, amount=diff, increase=increase_or_decrease)

        billDiff = abs(Decimal(instance.bill) - Decimal(invv.bill))
        if billDiff != 0:  # if bill changed
            newbill = Decimal(instance.bill) - Decimal(instance.payment)
            preBill = Decimal(invv.bill) - Decimal(invv.payment)

            bill_diff = Decimal(instance.bill) - Decimal(invv.bill)
            if bill_diff > 0:
                # sales revenue
                sales_revenue = chartofaccount.objects.get(
                    account_code=settings.SALES_REVENUE)
                increase_or_decrease = True
                jour = journal.objects.create(chartofaccount=sales_revenue, invoice=instance, outlet=outlet,
                                              contact=contact, details=details, amount=billDiff, increase=increase_or_decrease)
            else:
                # sales revenue
                sales_revenue = chartofaccount.objects.get(
                    account_code=settings.SALES_REVENUE)
                increase_or_decrease = False
                jour = journal.objects.create(chartofaccount=sales_revenue, invoice=instance, outlet=outlet,
                                              contact=contact, details=details, amount=billDiff, increase=increase_or_decrease)
            absNewBill = abs(newbill)
            absPreBill = abs(preBill)
            if newbill > 0:
                increase_or_decrease = True
                # account recevable
                accounts_receivable = chartofaccount.objects.get(
                    account_code=settings.ACCOUNTS_RECEIVABLE)
                jour = journal.objects.create(chartofaccount=accounts_receivable, invoice=instance, outlet=outlet,
                                              contact=contact, details=details, amount=absNewBill, increase=increase_or_decrease)

            elif newbill < 0:
                increase_or_decrease = True
                # account payable
                # accounts_receivable = chartofaccount.objects.get(
                #     account_code=settings.ACCOUNTS_PAYABLE)
                advance_from_customer = chartofaccount.objects.get(
                    account_code=settings.ADVANCE_FROM_CUSTOMERS)
                jour = journal.objects.create(chartofaccount=advance_from_customer, invoice=instance, outlet=outlet,
                                              contact=contact, details=details, amount=absNewBill, increase=increase_or_decrease)

            if preBill > 0:
                increase_or_decrease = False
                # account recevable
                accounts_receivable = chartofaccount.objects.get(
                    account_code=settings.ACCOUNTS_RECEIVABLE)
                jour = journal.objects.create(chartofaccount=accounts_receivable, invoice=instance, outlet=outlet,
                                              contact=contact, details=details, amount=absPreBill, increase=increase_or_decrease)

            elif preBill < 0:
                increase_or_decrease = False
                # account payable
                # accounts_receivable = chartofaccount.objects.get(
                #     account_code=settings.ACCOUNTS_PAYABLE)
                advance_from_customer = chartofaccount.objects.get(
                    account_code=settings.ADVANCE_FROM_CUSTOMERS)
                jour = journal.objects.create(chartofaccount=advance_from_customer, invoice=instance, outlet=outlet,
                                              contact=contact, details=details, amount=absPreBill, increase=increase_or_decrease)

        costDiff = Decimal(instance.costing) - Decimal(invv.costing)
        print("costDiff", costDiff)
        if costDiff != 0:
            if costDiff > 0:
                # cost of good sold
                cost_of_good_sold = chartofaccount.objects.get(
                    account_code=settings.COST_OF_GOOD_SOLD)
                increase_or_decrease = True
                jour = journal.objects.create(chartofaccount=cost_of_good_sold, invoice=instance, outlet=outlet,
                                              contact=contact, details=details, amount=abs(costDiff), increase=increase_or_decrease)
                # inventory asset
                inventory = chartofaccount.objects.get(
                    account_code=settings.INVENTORY_ASSETS)
                increase_or_decrease = False
                jour = journal.objects.create(chartofaccount=inventory, invoice=instance, outlet=outlet,
                                              contact=contact, details=details, amount=abs(costDiff), increase=increase_or_decrease)
            else:
                # cost of good sold
                cost_of_good_sold = chartofaccount.objects.get(
                    account_code=settings.COST_OF_GOOD_SOLD)
                increase_or_decrease = False
                jour = journal.objects.create(chartofaccount=cost_of_good_sold, invoice=instance, outlet=outlet,
                                              contact=contact, details=details, amount=abs(costDiff), increase=increase_or_decrease)
                # inventory asset
                inventory = chartofaccount.objects.get(
                    account_code=settings.INVENTORY_ASSETS)
                increase_or_decrease = True
                jour = journal.objects.create(chartofaccount=inventory, invoice=instance, outlet=outlet,
                                              contact=contact, details=details, amount=abs(costDiff), increase=increase_or_decrease)
    
    # Notification
    if len(inv) > 0:
        invv = inv[0]
        diff = abs(Decimal(instance.payment) - Decimal(invv.payment))
        if diff != 0:
            '''Sending Notifications to the customer'''
            message = f"Hello {contact.name}, You made a payment of  {diff} for Invoice #{instance.invoice_number}. Follow this link to see the full invoice: {current_site}/invoice/{instance.id}."
            if contact.email != "" and contact.email != None:
                sendEmail(contact, contact.email,
                          "Purchase Payment Update", message)
            # sending sms
            if contact.phone != "" and contact.phone != None:
                sendSms(contact.phone, message)
            '''End Of Sending Notifications'''

    # Vat change
    if len(inv) > 0:
        # Vat payable and sales revenue
        vat_account = chartofaccount.objects.get(
                            account_code=settings.VAT_PAYABLE)
        
        # Vat payment date
        if instance.due == 0 and invv.due != 0:
        # if instance.status == "Generate Vat" and invv.status != "Generate Vat":
            instance.Vat_issued_date = datetime.date.today()
        
        # if due is changed
        # if instance.status != invv.status:
            # and changed status is Generate Vat
            # if instance.status == 'Generate Vat':
        if instance.due != invv.due:
            if instance.due == 0:            
                # getting previous vat amount
                previous_Vat = journal.objects.filter(chartofaccount=vat_account, invoice=instance, outlet=outlet,
                                      contact=contact)
                previous_vat_payable = 0
                for item in previous_Vat:
                    if item.increase:
                        previous_vat_payable = Decimal(previous_vat_payable) + Decimal(item.amount)
                    else:
                        previous_vat_payable = Decimal(previous_vat_payable) - Decimal(item.amount)
                
                
                # if there was no previous vat
                if previous_vat_payable == 0:       
                    # VAT payable
                    details = "VAT payable for invoice no: " + str(instance.invoice_number)

                    vat_account = chartofaccount.objects.get(
                        account_code=settings.VAT_PAYABLE)
                    increase_or_decrease = True
                    jour = journal.objects.create(chartofaccount=vat_account, invoice=instance, outlet=outlet,
                                    contact=contact, details=details, amount=instance.tax, increase=increase_or_decrease)


                    # Sales revenue
                    details = "Sell with invoice no: " + str(instance.invoice_number)
                    sales_revenue = chartofaccount.objects.get(
                        account_code=settings.SALES_REVENUE)
                    increase_or_decrease = False
                    sales_revenue_jour = journal.objects.create(chartofaccount=sales_revenue, invoice=instance, outlet=outlet,
                                                                contact=contact, details=details, amount=instance.tax, increase=increase_or_decrease)
                # if there was previous vat
                else:
                    vatdif = Decimal(instance.tax) - Decimal(previous_vat_payable)
                    if vatdif > 0:
                        # VAT payable
                        details = "VAT payable for invoice no: " + str(instance.invoice_number)

                        vat_account = chartofaccount.objects.get(
                            account_code=settings.VAT_PAYABLE)
                        increase_or_decrease = True
                        jour = journal.objects.create(chartofaccount=vat_account, invoice=instance, outlet=outlet,
                                        contact=contact, details=details, amount=vatdif, increase=increase_or_decrease)


                        # Sales revenue
                        details = "Sell with invoice no: " + str(instance.invoice_number)
                        sales_revenue = chartofaccount.objects.get(
                            account_code=settings.SALES_REVENUE)
                        increase_or_decrease = False
                        sales_revenue_jour = journal.objects.create(chartofaccount=sales_revenue, invoice=instance, outlet=outlet,
                                                                    contact=contact, details=details, amount=vatdif, increase=increase_or_decrease)
                        
                    elif vatdif < 0:
                        
                        # VAT payable
                        details = "VAT payable for invoice no: " + str(instance.invoice_number)

                        vat_account = chartofaccount.objects.get(
                            account_code=settings.VAT_PAYABLE)
                        increase_or_decrease = False
                        jour = journal.objects.create(chartofaccount=vat_account, invoice=instance, outlet=outlet,
                                        contact=contact, details=details, amount=abs(vatdif), increase=increase_or_decrease)


                        # Sales revenue
                        details = "Sell with invoice no: " + str(instance.invoice_number)
                        sales_revenue = chartofaccount.objects.get(
                            account_code=settings.SALES_REVENUE)
                        increase_or_decrease = True
                        sales_revenue_jour = journal.objects.create(chartofaccount=sales_revenue, invoice=instance, outlet=outlet,
                                                                    contact=contact, details=details, amount=abs(vatdif), increase=increase_or_decrease)
                                 
        # if instance.due == 0:
        # if vat is updated
        # vatdif = Decimal(instance.tax) - Decimal(invv.tax)
        # vatdif = round(vatdif, 2)
        # print(vatdif)
        # if vatdif > 0:
        #     # VAT payable
        #     details = "VAT payable for invoice no: " + str(instance.invoice_number)

        #     vat_account = chartofaccount.objects.get(
        #         account_code=settings.VAT_PAYABLE)
        #     increase_or_decrease = True
        #     jour = journal.objects.create(chartofaccount=vat_account, invoice=instance, outlet=outlet,
        #                         contact=contact, details=details, amount=vatdif, increase=increase_or_decrease)

        if instance.status == 'Generate Vat':
        # if vat is updated
            vatdif = Decimal(instance.tax) - Decimal(invv.tax)
            if vatdif > 0:
                # VAT payable
                details = "VAT payable for invoice no: " + str(instance.invoice_number)

                vat_account = chartofaccount.objects.get(
                    account_code=settings.VAT_PAYABLE)
                increase_or_decrease = True
                jour = journal.objects.create(chartofaccount=vat_account, invoice=instance, outlet=outlet,
                                    contact=contact, details=details, amount=vatdif, increase=increase_or_decrease)


                # Sales revenue
                details = "Sell with invoice no: " + str(instance.invoice_number)
                sales_revenue = chartofaccount.objects.get(
                    account_code=settings.SALES_REVENUE)
                increase_or_decrease = False
                sales_revenue_jour = journal.objects.create(chartofaccount=sales_revenue, invoice=instance, outlet=outlet,
                                                            contact=contact, details=details, amount=vatdif, increase=increase_or_decrease)
                
            elif vatdif < 0:
                
                # VAT payable
                details = "VAT payable for invoice no: " + str(instance.invoice_number)

                vat_account = chartofaccount.objects.get(
                    account_code=settings.VAT_PAYABLE)
                increase_or_decrease = False
                jour = journal.objects.create(chartofaccount=vat_account, invoice=instance, outlet=outlet,
                                    contact=contact, details=details, amount=abs(vatdif), increase=increase_or_decrease)


                # Sales revenue
                details = "Sell with invoice no: " + str(instance.invoice_number)
                sales_revenue = chartofaccount.objects.get(
                    account_code=settings.SALES_REVENUE)
                increase_or_decrease = True
                sales_revenue_jour = journal.objects.create(chartofaccount=sales_revenue, invoice=instance, outlet=outlet,
                                                            contact=contact, details=details, amount=abs(vatdif), increase=increase_or_decrease)
                
                    
                   

def purchase_pre_save(sender, instance, **kwargs):
    # print("--------Start Pre Save-------")
    inv = sender.objects.filter(id=instance.id)
    account = instance.account
    contact = instance.contact
    is_received = instance.is_received
    bill = instance.bill
    outlet = instance.location

    discount = instance.discount
    adjustment = instance.adjustment
    details = "Purchase with invoice no: " + str(instance.purchase_number)

    if account.type == "Cash":
        CashOnHandCode = settings.CASH
    else:
        CashOnHandCode = settings.BANK

    if len(inv) > 0:
        invv = inv[0]
        diff = abs(Decimal(instance.payment) - Decimal(invv.payment))
        account.cash = Decimal(account.cash) - Decimal(diff)
        account.save()
    else:
        account.cash = Decimal(account.cash) - Decimal(instance.payment)
        account.save()

    if len(inv) > 0:
        invv = inv[0]
        diff = abs(Decimal(instance.payment) - Decimal(invv.payment))
        discountdiff = Decimal(instance.discount) - Decimal(invv.discount)
        adjustmentdiff = Decimal(instance.adjustment) - \
            Decimal(invv.adjustment)

        if adjustmentdiff > 0:  # if there is any adjustment
            # advance to supplier
            details = "Advance adjustment with purchase no: " + \
                str(instance.purchase_number)
            advance = chartofaccount.objects.get(
                account_code=settings.ADVANCE_TO_SUPPLIERS)
            increase_or_decrease = False
            jour = journal.objects.create(chartofaccount=advance, purchasee=instance, outlet=outlet,
                                          contact=contact, details=details, amount=adjustmentdiff, increase=increase_or_decrease)
            details = "Purchase with invoice no: " + \
                str(instance.purchase_number)

        # discount on update
        # if there is discount variation from previous invoice
        if discountdiff != 0:
            if discountdiff > 0:
                # if new discount is greater than previous discount
                increase_or_decrease = True
                inventory_discount = chartofaccount.objects.get(
                    account_code=settings.INVENTORY_DISCOUNT)
                jour = journal.objects.create(chartofaccount=inventory_discount, purchasee=instance, outlet=outlet,
                                              contact=contact, details=details, amount=abs(discountdiff), increase=increase_or_decrease)

                # Account payable
                increase_or_decrease = False
                accounts_payable = chartofaccount.objects.get(
                    account_code=settings.ACCOUNTS_PAYABLE)
                jour = journal.objects.create(chartofaccount=accounts_payable, purchasee=instance, outlet=outlet,
                                              contact=contact, details=details, amount=abs(discountdiff), increase=increase_or_decrease)

            else:
                # if new discount is less than previous discount
                increase_or_decrease = False
                inventory_discount = chartofaccount.objects.get(
                    account_code=settings.INVENTORY_DISCOUNT)
                jour = journal.objects.create(chartofaccount=inventory_discount, purchasee=instance, outlet=outlet,
                                              contact=contact, details=details, amount=abs(discountdiff), increase=increase_or_decrease)

                # Advance to supplier
                increase_or_decrease = True
                advance = chartofaccount.objects.get(
                    account_code=settings.ADVANCE_TO_SUPPLIERS)
                jour = journal.objects.create(chartofaccount=advance, purchasee=instance, outlet=outlet,
                                              contact=contact, details=details, amount=abs(discountdiff), increase=increase_or_decrease)
 
        # New update

        # if there is any new payment
        if Decimal(invv.payment) != Decimal(instance.payment):
            # cash on hand
            # ------------------------------------- updateamount
            updateamount = diff
            if adjustmentdiff > 0:
                updateamount = diff - adjustmentdiff
            # ------------------------------------- updateamount
            increase_or_decrease = False
            cash_on_hand = chartofaccount.objects.get(
                account_code=CashOnHandCode)
            jour = journal.objects.create(chartofaccount=cash_on_hand, purchasee=instance, account=account, outlet=outlet,
                                          contact=contact, details=details, amount=updateamount, increase=increase_or_decrease)

        if instance.received_item_price == invv.received_item_price:
            Newpayment = Decimal(instance.payment) - Decimal(invv.payment)
            if instance.payment < instance.received_item_price:
                # accounts payable
                if Newpayment > 0:
                    increase_or_decrease = False
                    accounts_payable = chartofaccount.objects.get(
                        account_code=settings.ACCOUNTS_PAYABLE)
                    jour = journal.objects.create(chartofaccount=accounts_payable, purchasee=instance, outlet=outlet,
                                                  contact=contact, details=details, amount=Newpayment, increase=increase_or_decrease)
            else:
                Restamount = instance.received_item_price - invv.payment
                if Restamount > 0:
                    # accounts payable
                    increase_or_decrease = False
                    accounts_payable = chartofaccount.objects.get(
                        account_code=settings.ACCOUNTS_PAYABLE)
                    jour = journal.objects.create(chartofaccount=accounts_payable, purchasee=instance, outlet=outlet,
                                                  contact=contact, details=details, amount=Restamount, increase=increase_or_decrease)

                    if Restamount != Newpayment:
                        # advance to supplier
                        advance_amount = Newpayment - Restamount
                        advance = chartofaccount.objects.get(
                            account_code=settings.ADVANCE_TO_SUPPLIERS)
                        increase_or_decrease = True
                        jour = journal.objects.create(chartofaccount=advance, purchasee=instance, outlet=outlet,
                                                      contact=contact, details=details, amount=advance_amount, increase=increase_or_decrease)
                elif Newpayment > 0:
                    # advance to supplier
                    details = "Purchase with invoice no: " + \
                        str(instance.purchase_number)
                    advance_amount = Newpayment - Restamount
                    advance = chartofaccount.objects.get(
                        account_code=settings.ADVANCE_TO_SUPPLIERS)
                    increase_or_decrease = True
                    jour = journal.objects.create(chartofaccount=advance, purchasee=instance, outlet=outlet,
                                                  contact=contact, details=details, amount=Newpayment, increase=increase_or_decrease)
    # print("---------End Pre Save--------")


def purchase_post_delete(sender, instance, **kwargs):
    # deleting all notification connected to that purchase
    notify = Notification.objects.filter(
        actor_object_id=instance.id, description='purcahse')
    notify.delete()


def purchase_post_save(sender, instance, created, update_fields, **kwargs):
    contact = instance.contact
    outlet = instance.location
    purchase_id = instance.id
    account = instance.account
    amount = instance.bill
    payment = instance.payment
    due = instance.due
    discount = instance.discount
    cost = instance.costing
    shipping_cost = instance.shipping
    adjustment = instance.adjustment

    details = "Purchase with invoice no: " + str(instance.purchase_number)

    if created and instance.adjustment != 0:  # if there is any adjustment
        # advance to supplier
        print("------------------Adjustment--------")
        details = "Advance adjustment with purchase no: " + \
            str(instance.purchase_number)
        advance = chartofaccount.objects.get(
            account_code=settings.ADVANCE_TO_SUPPLIERS)
        increase_or_decrease = False
        jour = journal.objects.create(chartofaccount=advance, purchasee=instance, outlet=outlet,
                                      contact=contact, details=details, amount=adjustment, increase=increase_or_decrease)
    details = "Purchase with invoice no: " + str(instance.purchase_number)
    if created:
        # inventory discount
        if discount != 0:
            inventory_discount = chartofaccount.objects.get(
                account_code=settings.INVENTORY_DISCOUNT)
            increase_or_decrease = True
            jour = journal.objects.create(chartofaccount=inventory_discount, purchasee=instance, outlet=outlet,
                                          contact=contact, details=details, amount=discount, increase=increase_or_decrease)
            # Account payable
            increase_or_decrease = False
            accounts_payable = chartofaccount.objects.get(
                account_code=settings.ACCOUNTS_PAYABLE)
            jour = journal.objects.create(chartofaccount=accounts_payable, purchasee=instance, outlet=outlet,
                                          contact=contact, details=details, amount=discount, increase=increase_or_decrease)

            # cash_on_hand = chartofaccount.objects.get(
            #     account_code=CashOnHandCode)
            # increase_or_decrease = False
            # jour = journal.objects.create(chartofaccount=cash_on_hand, purchasee=instance, account=account, outlet=outlet,
            #                               contact=contact, details=details, amount=discount, increase=increase_or_decrease)

    if created and payment > 0:
        # print("New Purchase Created")

        if account.type == "Cash":
            CashOnHandCode = settings.CASH
        else:
            CashOnHandCode = settings.BANK

        # cash on hand
        # ------------------------------------- updateamount
        updateamount = payment
        if instance.adjustment > 0:
            updateamount = payment - instance.adjustment
        # ------------------------------------- updateamount
        cash_on_hand = chartofaccount.objects.get(account_code=CashOnHandCode)
        increase_or_decrease = False
        jour = journal.objects.create(chartofaccount=cash_on_hand, purchasee=instance, account=account, outlet=outlet,
                                      contact=contact, details=details, amount=updateamount, increase=increase_or_decrease)

        # advance
        details = "Advance to supplier with purchase no: " + \
            str(instance.purchase_number)
        advance = chartofaccount.objects.get(
            account_code=settings.ADVANCE_TO_SUPPLIERS)
        increase_or_decrease = True
        jour = journal.objects.create(chartofaccount=advance, purchasee=instance, outlet=outlet,
                                      contact=contact, details=details, amount=updateamount, increase=increase_or_decrease)

    else:
        print("Purchase Status Update")


def services_costing_post_save(sender, instance, created, update_fields, **kwargs):
    services = instance.services
    product = instance.product
    quantity = instance.quantity
    cost = instance.cost
    details = "Services costing: " + \
        str(cost)+", for Invoice No: " + \
        str(instance.services.invoice.invoice_number)

    cost_of_good_sold = chartofaccount.objects.get(
        account_code=settings.COST_OF_GOOD_SOLD)
    increase_or_decrease = True
    jour = journal.objects.create(chartofaccount=cost_of_good_sold, invoice=instance.services.invoice,
                                  amount=cost, details=details, increase=increase_or_decrease)

    # if product is choosen
    if instance.product:
        inventory_assete = chartofaccount.objects.get(
            account_code=settings.INVENTORY_ASSETS)
        increase_or_decrease = False
        jour = journal.objects.create(chartofaccount=inventory_assete, invoice=instance.services.invoice,
                                      amount=cost, details=details, increase=increase_or_decrease)
    # else:
    #     increase_or_decrease = False
    #     cash_on_hand = chartofaccount.objects.get(account_code=settings.CASH)
    #     jour = journal.objects.create(chartofaccount=cash_on_hand, invoice=instance.services.invoice,
    #                                   account=account, details=details, amount=cost, increase=increase_or_decrease)


def services_costing_pre_delete(sender, instance, **kwargs):

    services = instance.services
    product = instance.product
    quantity = instance.quantity
    cost = instance.cost
    details = "Services costing: " + \
        str(cost)+", for Invoice No: " + \
        str(instance.services.invoice.invoice_number)

    cost_of_good_sold = chartofaccount.objects.get(
        account_code=settings.COST_OF_GOOD_SOLD)
    increase_or_decrease = False
    jour = journal.objects.create(chartofaccount=cost_of_good_sold, invoice=instance.services.invoice,
                                  amount=cost, details=details, increase=increase_or_decrease)

    inventory_assete = chartofaccount.objects.get(
        account_code=settings.INVENTORY_ASSETS)
    increase_or_decrease = True
    jour = journal.objects.create(chartofaccount=inventory_assete, invoice=instance.services.invoice,
                                  amount=cost, details=details, increase=increase_or_decrease)




