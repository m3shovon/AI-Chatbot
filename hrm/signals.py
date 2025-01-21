from time import time
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from notifications.signals import notify
from contact.models import UserProfile, EmployeeProfile
from notifications.models import Notification
from decimal import Decimal
from accounting import models as accounting_models
import datetime


def notify_leave_application(sender, instance, created, update_fields, **kwargs):
    """
    Notify about leave application
    """

    employee = instance.employee

    if created:
        '''Sending Notifications to admins'''

        message = f"{employee.name} Has Applied for {instance.leaveType.Typename} for {instance.leaveDays} Days"
        superusers = UserProfile.objects.filter(is_superuser=True)
        for superuser in superusers:
            notify.send(instance, recipient=superuser,
                        description='leave', verb=message)
            sendEmail(superuser, superuser.email, "Leave Request", message)
        '''End Of Sending Notifications'''
    else:
        '''Sending Notifications'''
        message = f"Hello {employee.name}, Admin Has {instance.leaveStatus} Your Application for {instance.leaveType.Typename} of {instance.leaveDays} Days"
        notify.send(instance, recipient=employee,
                    description='leave', verb=message)
        sendEmail(employee, employee.email, "Leave Request Status", message)
        '''End Of Sending Notifications'''


def notify_leave_deletion(sender, instance, **kwargs):
    notify = Notification.objects.filter(
        actor_object_id=instance.id, description='leave')
    notify.delete()


def attendance_pre_save(sender, instance, update_fields, **kwargs):
    entryTime = instance.entryTime
    exitTime = instance.exitTime
    shift = instance.shift
    isAttended = instance.isAttended
    defultEntryTime = EmployeeProfile.objects.get(
        employee=instance.employee).defaultEntryTime
    defultExitTime = EmployeeProfile.objects.get(
        employee=instance.employee).defaultExitTime
    defultShift = EmployeeProfile.objects.get(
        employee=instance.employee).defaultShift
    # print(defultEntryTime)
    maxEntryTime = (datetime.datetime(2000, 1, 1, defultEntryTime.hour, defultEntryTime.minute,
                    defultEntryTime.second) + datetime.timedelta(minutes=16)).time()
    minExitTime = (datetime.datetime(2000, 1, 1, defultExitTime.hour, defultExitTime.minute,
                   defultExitTime.second) - datetime.timedelta(minutes=16)).time()

    # if isAttended and shift == defultShift and (entryTime >= maxEntryTime or exitTime <= minExitTime):
    if isAttended and shift == defultShift and (entryTime >= maxEntryTime):
        instance.isLate = True
    else:
        instance.isLate = False

    lateTime = 0
    overTime = 0
    today = datetime.date.today()

    if entryTime:
        entryTime = datetime.datetime.combine(today, entryTime)
        maxEntryTime = datetime.datetime.combine(today, maxEntryTime)
        defultEntryTime = datetime.datetime.combine(today, defultEntryTime)
        if entryTime >= maxEntryTime:
            timediff = (entryTime - defultEntryTime)
            time = timediff.total_seconds()
            hr = time//3600
            min = ((time % 3600) // 60)/100
            lateTime = lateTime + (round(hr, 2) + round(min, 2))

    if exitTime:
        exitTime = datetime.datetime.combine(today, exitTime)
        if exitTime <= entryTime:
            exitTime = exitTime + datetime.timedelta(days=1)

        minExitTime = datetime.datetime.combine(today, minExitTime)
        if minExitTime <= entryTime:
            minExitTime = minExitTime + datetime.timedelta(days=1)

        defultExitTime = datetime.datetime.combine(today, defultExitTime)
        if defultExitTime <= defultEntryTime:
            defultExitTime = defultExitTime + datetime.timedelta(days=1)

        if exitTime <= minExitTime:
            timediff = (defultExitTime - exitTime)
            time = timediff.total_seconds()
            hr = time//3600
            min = ((time % 3600) // 60)/100
            lateTime = lateTime + (round(hr, 2) + round(min, 2))

        if exitTime >= defultExitTime:
            timediff = (exitTime - defultExitTime)
            overTime = timediff.total_seconds()
            hr = overTime//3600
            min = ((overTime % 3600) // 60)/100
            overTime = round(hr, 2) + round(min, 2)

    instance.lateTime = lateTime
    instance.overTime = overTime


def loan_pre_save(sender, instance, **kwargs):
    """
    Notify about leave application
    """

    employee = instance.employee
    outlet = instance.employee.branch
    amount = instance.loanAmount
    payment_method = instance.payment_method
    prev = sender.objects.filter(id=instance.id).first()
    if prev:
        prev_status = prev.loanStatus
        if prev_status == "approved" and instance.loanStatus == "paid":
            # decreasing amount from account
            payment_method.cash = Decimal(
                payment_method.cash) - Decimal(amount)
            payment_method.save()

            details = "Paid Loan Amount of : " + str(amount) + " For " + str(
                instance.employee.name) + " of " + str(instance.loanType) + " On " + str(payment_method.name)
            employee_advance = accounting_models.chartofaccount.objects.get(
                account_code=settings.EMPLOYEE_ADVANCE)
            increase_or_decrease = True
            jour1 = accounting_models.journal.objects.create(chartofaccount=employee_advance,
                                                             outlet=outlet,
                                                             employe=instance.employee,
                                                             loan=instance,
                                                             increase=increase_or_decrease,
                                                             details=details,
                                                             amount=amount,
                                                             account=payment_method
                                                             )

            if payment_method.type == "Cash":
                CashOnHandCode = settings.CASH
            else:
                CashOnHandCode = settings.BANK
            details = "Paid Loan Amount of : " + str(amount) + " For " + str(
                instance.employee.name) + " of " + str(instance.loanType) + " On " + str(payment_method.name)
            cash_on_hand = accounting_models.chartofaccount.objects.get(
                account_code=CashOnHandCode)
            increase_or_decrease = False
            jour1 = accounting_models.journal.objects.create(chartofaccount=cash_on_hand,
                                                             outlet=outlet,
                                                             employe=instance.employee,
                                                             loan=instance,
                                                             increase=increase_or_decrease,
                                                             details=details,
                                                             amount=amount,
                                                             account=payment_method
                                                             )


def loan_post_save(sender, instance, created, update_fields, **kwargs):
    """
    Notify about leave application
    """

    employee = instance.employee
    outlet = instance.employee.branch
    amount = instance.loanAmount
    payment_method = instance.payment_method
    if created:
        '''Sending Notifications to admins'''
        message = f"{employee.name} Has Applied for {instance.loanType} Loan of {instance.loanAmount} Taka For {instance.loanPayableMonths} Months."
        superusers = UserProfile.objects.filter(is_superuser=True)
        for superuser in superusers:
            notify.send(instance, recipient=superuser,
                        description='loan', verb=message)
            sendEmail(superuser, superuser.email, "Loan Request", message)
        '''End Of Sending Notifications'''
    else:
        '''Sending Notifications'''
        message = f"Hello {employee.name}, Admin Has {instance.loanStatus} Your Application for {instance.loanType} Loan of {instance.loanAmount} Taka For {instance.loanPayableMonths} Months."
        notify.send(instance, recipient=employee,
                    description='loan', verb=message)
        sendEmail(employee, employee.email, "Loan Request Status", message)
        '''End Of Sending Notifications'''


def loan_post_delete(sender, instance, **kwargs):
    notify = Notification.objects.filter(
        actor_object_id=instance.id, description='loan')
    notify.delete()


def payslip_pre_save(sender, instance, **kwargs):
    pre = sender.objects.filter(id=instance.id).first()
    if pre:
        prePyament1 = pre.amount_1
        preAccount1 = pre.payment_method_1
        prePayment2 = pre.amount_2
        preAccount2 = pre.payment_method_2

        if preAccount1:
            preAccount1.cash = Decimal(preAccount1.cash) + Decimal(prePyament1)
            preAccount1.save()
            if preAccount1.type == "Cash":
                CashOnHandCode = settings.CASH
            else:
                CashOnHandCode = settings.BANK
            cash = accounting_models.chartofaccount.objects.get(
                account_code=CashOnHandCode)
            increase_or_decrease = False
            jour = accounting_models.journal.objects.filter(chartofaccount=cash, employe=pre.employee,
                                                            payslip=pre, increase=increase_or_decrease).first()
            if jour:
                jour.delete()

        if preAccount2:
            preAccount2.cash = Decimal(preAccount2.cash) + Decimal(prePayment2)
            preAccount2.save()
            if preAccount2.type == "Cash":
                CashOnHandCode = settings.CASH
            else:
                CashOnHandCode = settings.BANK
            cash = accounting_models.chartofaccount.objects.get(
                account_code=CashOnHandCode)
            increase_or_decrease = False
            jour = accounting_models.journal.objects.filter(chartofaccount=cash, employe=pre.employee,
                                                            payslip=pre, increase=increase_or_decrease).first()
            if jour:
                jour.delete()

    if instance.payment_method_1:
        act = instance.payment_method_1
        act.cash = Decimal(act.cash) - Decimal(instance.amount_1)
        act.save()
    if instance.payment_method_2:
        act = instance.payment_method_2
        act.cash = Decimal(act.cash) - Decimal(instance.amount_2)
        act.save()


def loan_payment_post_save(sender, instance, created, update_fields, **kwargs):
    print("Loan Payment Post Save")


def payslip_post_save(sender, instance, created, update_fields, **kwargs):
    """
    Notify about payslip application
    """
    # print("--------Start-------")

    total_salary = Decimal(instance.net_salary)
    total_paid = Decimal(instance.payment)
    outlet = instance.employee.branch
    total_adjustment = Decimal(instance.loan_adjustment) + \
        Decimal(instance.advance_adjustment)
    if total_adjustment > 0:
        total_paid = total_paid + total_adjustment
    # employee advance
    if total_adjustment > 0:
        details = "Employee Advance RePayment of " + \
            str(total_adjustment) + "For " + str(instance.employee.name)
        employee_advance = accounting_models.chartofaccount.objects.get(
            account_code=settings.EMPLOYEE_ADVANCE)
        increase_or_decrease = False
        jour, _ = accounting_models.journal.objects.get_or_create(chartofaccount=employee_advance, employe=instance.employee,
                                                                  outlet=outlet, payslip=instance, increase=increase_or_decrease)
        jour.details = details
        jour.amount = total_adjustment
        jour.save()
    # total salary
    details = "Paid Salary of : " + \
        str(total_paid) + " For " + str(instance.employee.name)

    # salary expense
    salary_expense = accounting_models.chartofaccount.objects.get(
        account_code=settings.SALARY_EXPENSES)
    increase_or_decrease = True
    jour, _ = accounting_models.journal.objects.get_or_create(chartofaccount=salary_expense, employe=instance.employee,
                                                              outlet=outlet, payslip=instance, increase=increase_or_decrease)
    jour.details = details
    jour.amount = total_paid
    jour.save()
    # for payment method 1 n
    if instance.payment_method_1 and instance.payment_method_1.type == "Cash":
        CashOnHandCode = settings.CASH
    else:
        CashOnHandCode = settings.BANK

    # payment 1
    if instance.payment_method_1 and instance.amount_1 > 0:
        details = "Paid Salary of : " + str(instance.amount_1) + " For " + str(
            instance.employee.name) + " From " + str(instance.payment_method_1.type)
        # print(details)
        cash = accounting_models.chartofaccount.objects.get(
            account_code=CashOnHandCode)
        increase_or_decrease = False
        jour1 = accounting_models.journal.objects.create(chartofaccount=cash,
                                                         outlet=outlet,
                                                         employe=instance.employee,
                                                         payslip=instance,
                                                         increase=increase_or_decrease,
                                                         details=details,
                                                         amount=instance.amount_1,
                                                         account=instance.payment_method_1
                                                         )
        # print(jour1)
    # for payment method 2
    if instance.payment_method_2 and instance.payment_method_2.type == "Cash":
        CashOnHandCode = settings.CASH
    else:
        CashOnHandCode = settings.BANK
    # payment 2
    if instance.payment_method_2 and instance.amount_2 > 0:
        details = "Paid Salary of : " + str(instance.amount_2) + " For " + str(
            instance.employee.name) + " From " + str(instance.payment_method_2.type)
        cash = accounting_models.chartofaccount.objects.get(
            account_code=CashOnHandCode)
        increase_or_decrease = False
        jour2 = accounting_models.journal.objects.create(chartofaccount=cash,
                                                         outlet=outlet,
                                                         employe=instance.employee,
                                                         payslip=instance,
                                                         increase=increase_or_decrease,
                                                         details=details,
                                                         amount=instance.amount_2,
                                                         account=instance.payment_method_2
                                                         )
        # print(jour2)
    # print("--------End-------")


def payslip_post_delete(sender, instance, **kwargs):
    notify = Notification.objects.filter(
        actor_object_id=instance.id, description='payslip')
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
