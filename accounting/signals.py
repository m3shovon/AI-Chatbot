from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from notifications.signals import notify
from contact.models import UserProfile
from order.models import *
from product.models import *
from accounting import models as accountingModel
from notifications.models import Notification
from decimal import Decimal
from django.db import transaction
import threading

lock = threading.Lock()

def paymentvoucher_item_post_save(sender, instance, **kwargs):
    # print("--------Start-------")
    pv = sender.objects.get(id=instance.id)
    # print(pv.amount)
    if instance.account:
        act = accountingModel.account.objects.get(
            id=instance.account.id)
        # print(act.cash)
        if pv.increase:
            act.cash = Decimal(act.cash) - Decimal(pv.amount)
        else:
            act.cash = Decimal(act.cash) + Decimal(pv.amount)
        # print(act.cash)
        act.save()
    # print("--------End-------")


def receivevoucher_item_post_save(sender, instance, **kwargs):
    # print("--------Start-------")
    pv = sender.objects.get(id=instance.id)
    # print(pv.amount)
    if instance.account:
        act = accountingModel.account.objects.get(
            id=instance.account.id)
        # print(act.cash)
        if pv.increase:
            act.cash = Decimal(act.cash) + Decimal(pv.amount)
        else:
            act.cash = Decimal(act.cash) - Decimal(pv.amount)
        # print(act.cash)
        act.save()
    # print("--------End-------")


def journalvoucher_item_post_save(sender, instance, **kwargs):
    # print("--------Start-------")
    pv = sender.objects.get(id=instance.id)
    # print(pv.amount)
    if instance.account:
        act = accountingModel.account.objects.get(
            id=instance.account.id)
        # print(act.cash)
        if pv.increase:
            act.cash = Decimal(act.cash) + Decimal(pv.amount)
        else:
            act.cash = Decimal(act.cash) - Decimal(pv.amount)
        # print(act.cash)
        act.save()
    # print("--------End-------")

@transaction.atomic
def journals_pre_save(sender, instance, **kwargs):
    
    with lock:
        previous = sender.objects.filter(id=instance.id)
        contact = instance.contact
        chartofaccount = instance.chartofaccount
        outlet = instance.outlet
        employe = instance.employe
        invoice = instance.invoice
        purchasee = instance.purchasee
        account = instance.account
        
        # mufrid start
        if len(previous) > 0:
            previousdata = previous[0]
            # chart of account update
            if previousdata.chartofaccount != instance.chartofaccount:
                # update the previous value
                if previousdata.increase:
                    # decrese the previous amount
                    previousdata.chartofaccount.amount = Decimal(previousdata.chartofaccount.amount) - Decimal(previousdata.amount)
                else:
                    # increse the previous amount
                    previousdata.chartofaccount.amount = Decimal(previousdata.chartofaccount.amount) + Decimal(previousdata.amount)
                previousdata.chartofaccount.save()
                # update the current value
                if instance.increase:
                    # decrese the previous amount
                    chartofaccount.amount = Decimal(chartofaccount.amount) + Decimal(instance.amount)
                else:
                    # increse the previous amount
                    chartofaccount.amount = Decimal(chartofaccount.amount) - Decimal(instance.amount)
            elif previousdata.amount != instance.amount:
                difference = Decimal(previousdata.amount) - Decimal(instance.amount)
                if difference > 0:
                    if instance.increase:
                    # decrese the previous amount
                        chartofaccount.amount = Decimal(chartofaccount.amount) - Decimal(difference)
                    else:
                    # increse the previous amount
                        chartofaccount.amount = Decimal(chartofaccount.amount) + Decimal(difference)
                else:
                    if instance.increase:
                    # decrese the previous amount
                        chartofaccount.amount = Decimal(chartofaccount.amount) + abs(Decimal(difference))
                    else:
                    # increse the previous amount
                        chartofaccount.amount = Decimal(chartofaccount.amount) - abs(Decimal(difference))
            
            elif previousdata.increase != instance.increase:
                # update the current value
                if instance.increase:
                    # decrese the previous amount
                    chartofaccount.amount = Decimal(chartofaccount.amount) + Decimal(instance.amount)
                else:
                    # increse the previous amount
                    chartofaccount.amount = Decimal(chartofaccount.amount) - Decimal(instance.amount)
                    
            
        # mufrid end     
        
        
        # account status starts
        
        if len(previous) > 0:
        
            previousdata = previous[0]
            diff =  instance.amount - previousdata.amount
            if diff != 0:
                if instance.account:
                    if str(chartofaccount.account_code)==str(settings.CASH) or str(chartofaccount.account_code)==str(settings.BANK):
                        accountStatusByDate, created = accountingModel.accountStatusByDate.objects.get_or_create(created=instance.created.date())
                        print("Adding account status")
                        if accountStatusByDate.data:
                            flag = 0
                            amount = 0
                            for account in accountStatusByDate.data["accounts"]:
                                if account["id"] == instance.account.id:
                                    flag = 1
                                    amount = Decimal(account["amount"])
                                    if diff > 0:
                                        if instance.increase:
                                            amount = Decimal(amount) + Decimal(abs(diff))
                                        else:
                                            amount = Decimal(amount) - Decimal(abs(diff))
                                    else:
                                        if instance.increase:
                                            amount = Decimal(amount) - Decimal(abs(diff))
                                        else:
                                            amount = Decimal(amount) + Decimal(abs(diff))
                                    account["amount"] = str(amount)
                                    accountStatusByDate.save()
                            
                            # if flag == 0:
                            #     # print("no match")
                            #     amount = 0
                            #     if  instance.increase ==  False:
                            #         amount = Decimal(amount) - Decimal(instance.amount)
                            #     else:
                            #         amount = Decimal(amount) + Decimal(instance.amount)
                            #     newdata = {"id": instance.account.id, "name": instance.account.name, "amount": str(amount)}
                            #     accountStatusByDate.data["accounts"].append(newdata)
                                
                            #     accountStatusByDate.save()
                            # else: 
                                # print("match")
                            
                        # else:
                        #     amount = 0
                        #     if instance.increase == False:
                        #         amount = Decimal(amount) - Decimal(instance.amount)
                        #     else:
                        #         amount = Decimal(amount) + Decimal(instance.amount)
                        #     account = []
                        #     account.append({"id": instance.account.id, "name": instance.account.name, "amount":  str(amount)})
                        #     accountStatusByDate.data = {"accounts" : account}
                        
                        #     accountStatusByDate.save()
                    
        
        # account status ends
        
        
        account = instance.account
        if instance.details is None:
            instance.details = ""
        if purchasee:
            if contact:
                instance.details = instance.details + ", Supplier - " + contact.name
        if invoice:
            if contact:
                instance.details = instance.details + ", Customer - " + contact.name
        if outlet:
            instance.details = instance.details + ", from " + outlet.name
        if account:
            if account.type != "Cash":
                instance.details = instance.details + ", Account - " + \
                    account.name + " ( " + account.account_no + " ) "

@transaction.atomic
def journals_post_save(sender, instance, created, update_fields, **kwargs):
    # with lock:
        contact = instance.contact
        chartofaccount = instance.chartofaccount
        amount = instance.amount
        increase = instance.increase
        
        # mufrid start
        
        # ChangeLog Start
        # chart_of_account, created = chartofaccount.objects.get_or_create(name=instance.account)

        if created:
            with transaction.atomic():
                chartofaccount = accountingModel.chartofaccount.objects.select_for_update().get(pk=chartofaccount.pk)
                if increase:
                # chart_of_account.update_debit(instance.amount)
                    chartofaccount.amount = Decimal(chartofaccount.amount) + Decimal(instance.amount)
                
                else:
                # chart_of_account.update_credit(instance.amount)
                    chartofaccount.amount = Decimal(chartofaccount.amount) - Decimal(instance.amount)

            # chartofaccount.save()
    # if chartofaccount.amount > instance.amount

                if chartofaccount.amount > 0:
                    if chartofaccount.normally_Debit == 'Debit':
                        chartofaccount.status = "Debit"
                    else:
                        chartofaccount.status = "Credit"

                elif chartofaccount.amount < 0:    
                    if chartofaccount.normally_Debit == 'Debit':
                        chartofaccount.status = "Credit"
                    else:
                        chartofaccount.status = "Debit"

                chartofaccount.save()
    
                # account status starts    
                if instance.account:
                    
                    if str(chartofaccount.account_code)==str(settings.CASH) or str(chartofaccount.account_code)==str(settings.BANK):
                        
                        accountStatusByDate, created = accountingModel.accountStatusByDate.objects.get_or_create(created=instance.created.date())
                        print("Updating account status")
                        if accountStatusByDate.data:
                            flag = 0
                            amount = 0
                            
                            for account in accountStatusByDate.data["accounts"]:
                                if account["id"] == instance.account.id:
                                    flag = 1
                                    
                                    amount = Decimal(account["amount"])
                                
                                    if instance.increase ==  False:
                                        amount = Decimal(amount) - Decimal(instance.amount)
                                    else:
                                        amount = Decimal(amount) + Decimal(instance.amount)
                                        
                                
                                    account["amount"] = str(amount)
                                
                                
                                    accountStatusByDate.save()
                            
                            if flag == 0:
                                # print("no match")
                                amount = 0
                                if  instance.increase ==  False:
                                    amount = Decimal(amount) - Decimal(instance.amount)
                                else:
                                    amount = Decimal(amount) + Decimal(instance.amount)
                                newdata = {"id": instance.account.id, "name": instance.account.name, "amount": str(amount)}
                                accountStatusByDate.data["accounts"].append(newdata)
                                
                                accountStatusByDate.save()
                            # else: 
                                # print("match")
                            
                        else:
                            amount = 0
                            if instance.increase == False:
                                amount = Decimal(amount) - Decimal(instance.amount)
                            else:
                                amount = Decimal(amount) + Decimal(instance.amount)
                            account = []
                            account.append({"id": instance.account.id, "name": instance.account.name, "amount":  str(amount)})
                            accountStatusByDate.data = {"accounts" : account}
                        
                            accountStatusByDate.save()
                    
            
                # account status ends
        
        
        
        # mufrid end
        
        if instance.invoice:
            contact = instance.invoice.contact
        if instance.purchasee:
            contact = instance.purchasee.contact
        
            
        if(str(chartofaccount.account_code) == str(settings.ACCOUNTS_PAYABLE)):
            # print("Accounts Payable")
            # if contact.Type == "Customer":
            if instance.increase:
                contact.account_balance = Decimal(
                    contact.account_balance) + Decimal(amount)
            else:
                contact.account_balance = Decimal(
                    contact.account_balance) - Decimal(amount)
            contact.save()

        if(str(chartofaccount.account_code) == str(settings.ADVANCE_FROM_CUSTOMERS)):
            # print("Advance From Customers")
            if instance.increase:
                contact.account_balance = Decimal(
                    contact.account_balance) + Decimal(amount)
            else:
                contact.account_balance = Decimal(
                    contact.account_balance) - Decimal(amount)
            contact.save()

        elif (str(chartofaccount.account_code) == str(settings.ACCOUNTS_RECEIVABLE)):
            # print("Accounts Receivable")
            if instance.increase:
                contact.account_balance = Decimal(
                    contact.account_balance) - Decimal(amount)
            else:
                contact.account_balance = Decimal(
                    contact.account_balance) + Decimal(amount)
            contact.save()

        elif (str(chartofaccount.account_code) == str(settings.ADVANCE_TO_SUPPLIERS)):
            # print("Advance To Supplier")
            if instance.increase:
                contact.account_balance = Decimal(
                    contact.account_balance) - Decimal(amount)
            else:
                contact.account_balance = Decimal(
                    contact.account_balance) + Decimal(amount)
            contact.save()

        elif (str(chartofaccount.account_code) == str(settings.SALES_VAT)):
            # Sales VAT
            vat_payable = accountingModel.chartofaccount.objects.get(
                account_code=settings.VAT_PAYABLE)
            if instance.increase:
                increase_or_decrease = False
            else:
                increase_or_decrease = True
            details = "Sales VAT"
            jour = accountingModel.journal.objects.create(chartofaccount=vat_payable,
                                                        details=details, amount=amount, increase=increase_or_decrease)

            # # Sales revenue
            sales_revenue = accountingModel.chartofaccount.objects.get(
                account_code=settings.SALES_REVENUE)
            increase_or_decrease = True
            sales_revenue_jour = accountingModel.journal.objects.create(chartofaccount=sales_revenue,
                                                                        details=details, amount=amount, increase=increase_or_decrease)

@transaction.atomic
def journals_post_delete(sender, instance, **kwargs):
    # print("-------------- Deleteing Journal -------------")
    with lock:
        contact = instance.contact
        chartofaccount = instance.chartofaccount
        amount = instance.amount
        increase = instance.increase
        # mufrid start
        if increase:
            # chart_of_account.update_debit(instance.amount)
            chartofaccount.amount = Decimal(chartofaccount.amount) - Decimal(instance.amount)
            
        else:
            # chart_of_account.update_credit(instance.amount)
            chartofaccount.amount = Decimal(chartofaccount.amount) + Decimal(instance.amount)

        chartofaccount.save()
        # mufrid end
        
        
        # account status starts
        
        if instance.account:
            if str(chartofaccount.account_code)==str(settings.CASH) or str(chartofaccount.account_code)==str(settings.BANK):
                accountStatusByDate, created = accountingModel.accountStatusByDate.objects.get_or_create(created=instance.created.date())
                print("Removeing account status")
                if accountStatusByDate.data:
                    flag = 0
                    amount = 0
                    for account in accountStatusByDate.data["accounts"]:
                        if account["id"] == instance.account.id:
                            flag = 1
                            
                            amount = Decimal(account["amount"])
                        
                            if instance.increase ==  False:
                                amount = Decimal(amount) + Decimal(instance.amount)
                            else:
                                amount = Decimal(amount) - Decimal(instance.amount)
                                
                        
                            account["amount"] = str(amount)
                        
                        
                            accountStatusByDate.save()
                    
                    if flag == 0:
                        # print("no match")
                        amount = 0
                        if  instance.increase ==  False:
                            amount = Decimal(amount) + Decimal(instance.amount)
                        else:
                            amount = Decimal(amount) - Decimal(instance.amount)
                        newdata = {"id": instance.account.id, "name": instance.account.name, "amount": str(amount)}
                        accountStatusByDate.data["accounts"].append(newdata)
                        
                        accountStatusByDate.save()
                    # else: 
                        # print("match")
                    
                else:
                    amount = 0
                    if instance.increase == False:
                        amount = Decimal(amount) + Decimal(instance.amount)
                    else:
                        amount = Decimal(amount) - Decimal(instance.amount)
                    account = []
                    account.append({"id": instance.account.id, "name": instance.account.name, "amount":  str(amount)})
                    accountStatusByDate.data = {"accounts" : account}
                
                    accountStatusByDate.save()
                
        
        # account status ends
        if instance.invoice is not None:
            contact = instance.invoice.contact
        if instance.purchasee:
            contact = instance.purchasee.contact
            
            
        
        # print("working")   
        # Updating account
        if instance.account:
            print("has bank account")  
            act = accountingModel.account.objects.get(
                id=instance.account.id)
            # print(act.name)
            # print(act.cash)
            if instance.increase:
                # print("Decresing money from account")
                act.cash = Decimal(act.cash) - Decimal(instance.amount)
            else:
                # print("Increasing money from account")
                act.cash = Decimal(act.cash) + Decimal(instance.amount)
            # print(act.cash)
            act.save()
            
        if(str(chartofaccount.account_code) == str(settings.ACCOUNTS_PAYABLE)):
            # print("Accounts Payable")
            # if contact.Type == "Customer":
            if instance.increase:
                contact.account_balance = Decimal(
                    contact.account_balance) - Decimal(amount)
            else:
                contact.account_balance = Decimal(
                    contact.account_balance) + Decimal(amount)
            contact.save()

        if(str(chartofaccount.account_code) == str(settings.ADVANCE_FROM_CUSTOMERS)):
            # print("Advance From Customers")
            if instance.increase:
                contact.account_balance = Decimal(
                    contact.account_balance) - Decimal(amount)
            else:
                contact.account_balance = Decimal(
                    contact.account_balance) + Decimal(amount)
            contact.save()

        elif (str(chartofaccount.account_code) == str(settings.ACCOUNTS_RECEIVABLE)):
            # print("Accounts Receivable")
            if instance.increase:
                contact.account_balance = Decimal(
                    contact.account_balance) + Decimal(amount)
            else:
                contact.account_balance = Decimal(
                    contact.account_balance) - Decimal(amount)
            contact.save()

        elif (str(chartofaccount.account_code) == str(settings.ADVANCE_TO_SUPPLIERS)):
            # print("Advance To Supplier")
            if instance.increase:
                contact.account_balance = Decimal(
                    contact.account_balance) + Decimal(amount)
            else:
                contact.account_balance = Decimal(
                    contact.account_balance) - Decimal(amount)
            contact.save()

        
def contravoucher_post_save(sender, instance, **kwargs):
    # print("--------Start-------")
    accountFrom = instance.accountFrom
    accountTo = instance.accountTo
    amount = instance.amount
    accountFrom.cash = Decimal(accountFrom.cash) - Decimal(amount)
    accountTo.cash = Decimal(accountTo.cash) + Decimal(amount)
    accountFrom.save()
    accountTo.save()

    fromType = accountFrom.type
    toType = accountTo.type
    if fromType == "Cash":
        fromCode = settings.CASH
    else:
        fromCode = settings.BANK

    if toType == "Cash":
        toCode = settings.CASH
    else:
        toCode = settings.BANK

    details = "Contra Voucher with voucher number " + \
        str(instance.voucher_number)
    # cash on hand
    increase_or_decrease = False
    from_jounral_credit = accountingModel.chartofaccount.objects.get(
        account_code=fromCode)
    jour = accountingModel.journal.objects.create(chartofaccount=from_jounral_credit, account=accountFrom,
                                                  details=details, amount=amount, increase=increase_or_decrease)
    # accounts recevable
    increase_or_decrease = True
    to_journal_debit = accountingModel.chartofaccount.objects.get(
        account_code=toCode)
    jour = accountingModel.journal.objects.create(chartofaccount=to_journal_debit, account=accountTo,
                                                  details=details, amount=amount, increase=increase_or_decrease)

    # print("--------End-------")


def petty_cash_save(sender, instance, **kwargs):
    # print("--------Start-------")
    pv = sender.objects.get(id=instance.id)
    act = Warehouse.objects.get(
        id=instance.location.id)
    amount = instance.amount
    details = "Petty Cash Expense From " + \
        str(act.name) + "Of Amount " + str(amount)

    if pv.increase:
        act.petty_cash = Decimal(act.petty_cash) - Decimal(pv.amount)
        # petty cash
        increase_or_decrease = False
        petty_cash = accountingModel.chartofaccount.objects.get(
            account_code=settings.PETTY_CASH)
        jour = accountingModel.journal.objects.create(chartofaccount=petty_cash, outlet=act,
                                                      details=details, amount=amount, increase=increase_or_decrease)
        # expense from petty cash
        increase_or_decrease = True
        expense_from_petty_cash = accountingModel.chartofaccount.objects.get(
            account_code=settings.EXPENSE_FROM_PETTY_CASH)
        jour = accountingModel.journal.objects.create(chartofaccount=expense_from_petty_cash, outlet=act,
                                                      details=details, amount=amount, increase=increase_or_decrease)

    else:
        act.petty_cash = Decimal(act.petty_cash) + Decimal(pv.amount)
        # petty cash
        increase_or_decrease = True
        petty_cash = accountingModel.chartofaccount.objects.get(
            account_code=settings.PETTY_CASH)
        jour = accountingModel.journal.objects.create(chartofaccount=petty_cash, outlet=act,
                                                      details=details, amount=amount, increase=increase_or_decrease)
        # expense from petty cash
        increase_or_decrease = False
        expense_from_petty_cash = accountingModel.chartofaccount.objects.get(
            account_code=settings.EXPENSE_FROM_PETTY_CASH)
        jour = accountingModel.journal.objects.create(chartofaccount=expense_from_petty_cash, outlet=act,
                                                      details=details, amount=amount, increase=increase_or_decrease)

    act.save()
    # print("--------End-------")


def pettycash_transfer_save(sender, instance, **kwargs):
    # print("--------Start-------")
    print("Petty Cash Transfer")
    # print("--------End-------")
