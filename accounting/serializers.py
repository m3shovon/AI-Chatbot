from rest_framework import serializers
from accounting import models
from product import models as productModel
from product import serializers as productSerializer
from contact import models as contactModel
from contact import serializers as contactSerializer
from order import models as orderModel
from order import serializers as orderSerializer
from hrm import models as hrmModel
from hrm import serializers as hrmSerializer


class accountparentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.accountparent
        fields = '__all__'

class AccountStatusByDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.accountStatusByDate
        fields = '__all__'


class accountSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.account
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.accountparent:
            accountparent = models.accountparent.objects.filter(
                id=instance.accountparent.id)
            accountparent_response = []
            for i in accountparent:
                accountparent_response.append(
                    accountparentSerializer(i).data)
            response["Parent"] = accountparent_response[0]
        return response


class chartofaccountSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.chartofaccount
        fields = '__all__'

    def to_representation(self, instance):

        response = super().to_representation(instance)
        if response["group"]:
            group = models.chartofaccount.objects.filter(id=instance.group.id)
            group_response = []
            for i in group:
                group_response.append(chartofaccountSerilizer(i).data)
            response["Group"] = group_response

        if response["sub_group"]:
            sub_group = models.chartofaccount.objects.filter(
                id=response["sub_group"])
            sub_group_response = []
            for i in sub_group:
                response["Sub_group"] = i.account_name
        response["title"] = instance.account_name
        response["key"] = instance.id
        response["value"] = instance.id
        return response


class journalSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.journal
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if response["chartofaccount"]:
            group = models.chartofaccount.objects.filter(
                id=instance.chartofaccount.id)
            group_response = []
            for i in group:
                group_response.append(chartofaccountSerilizer(i).data)
            response["Subgroup"] = group_response[0]["account_name"]
            response["Group"] = group_response[0]["Group"][0]["account_name"]
            response["print"] = group_response
            if response["increase"]:
                response["type"] = group_response[0]["normally_Debit"]
            else:
                if group_response[0]["normally_Debit"] == "Debit":
                    response["type"] = "Credit"
                else:
                    response["type"] = "Debit"
        
        return response


class journalSerilizerwithinvoice(serializers.ModelSerializer):
    class Meta:
        model = models.journal
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if response["chartofaccount"]:

            if instance.invoice:
                # print(instance.invoice.created_at)
                response["invoiceDate"] = instance.invoice.created_at
            if instance.account:
                response["accountname"] = instance.account.name
            group = models.chartofaccount.objects.filter(
                id=instance.chartofaccount.id)
            group_response = []
            for i in group:
                group_response.append(chartofaccountSerilizer(i).data)
            response["Subgroup"] = group_response[0]["account_name"]
            response["Group"] = group_response[0]["Group"][0]["account_name"]
            if response["increase"]:
                response["type"] = group_response[0]["normally_Debit"]
            else:
                if group_response[0]["normally_Debit"] == "Debit":
                    response["type"] = "Credit"
                else:
                    response["type"] = "Debit"
        return response


class paymentvoucherSerilizer(serializers.ModelSerializer):
    payment_methods = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.paymentvoucher
        fields = '__all__'
    def get_payment_methods(self, obj):
        result = []
        transections = []
        journal_items = models.paymentvoucheritems.objects.filter(paymentvoucher=obj)
        accounts = models.account.objects.all()
        for item in journal_items:
            if item.account:
                for account in accounts:
                    if account.id == item.account.id:
                        transections.append({"method": account.name, "amount": item.amount, "is_increase": item.increase})
        unique_methods = {transection['method'] for transection in transections}
        
        for unique_item in unique_methods:
            amount = 0
            for transection in transections:
                
                if transection["is_increase"] and unique_item == transection["method"]:
                    amount += transection["amount"]
                elif transection["is_increase"] == False and unique_item == transection["method"]:
                    amount -= transection["amount"]
            result.append({"method": unique_item, "amount": amount})
        return result
    def to_representation(self, instance):
        response = super().to_representation(instance)

        if response["location"]:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response

        if response["employee"]:
            employee = contactModel.UserProfile.objects.filter(
                id=instance.employee.id)
            employee_response = []
            for i in employee:
                employee_response.append(
                    contactSerializer.UserProfileSerializer(i).data)
            response["Employee"] = employee_response

        if response["contact"]:
            contact = contactModel.contact.objects.filter(
                id=instance.contact.id)
            contact_response = []
            for i in contact:
                contact_response.append(
                    contactSerializer.contactSerializer(i).data)
            response["Contact"] = contact_response

        if response["account"]:
            account = models.account.objects.filter(
                id=instance.account.id)
            account_response = []
            for i in account:
                account_response.append(
                    accountSerilizer(i).data)
            response["Account"] = account_response

        if response["invoice"]:
            invoice = orderModel.invoice.objects.filter(
                id=instance.invoice.id)
            invoice_response = []
            for i in invoice:
                invoice_response.append(
                    orderSerializer.Invoiceserializers(i).data)
            response["Invoice"] = invoice_response

        if response["purchasee"]:
            purchasee = orderModel.purchase.objects.filter(
                id=instance.purchasee.id)
            purchasee_response = []
            for i in purchasee:
                purchasee_response.append(
                    orderSerializer.Purchaseserializers(i).data)
            response["Purchasee"] = purchasee_response
        return response


class paymentvoucheritemsSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.paymentvoucheritems
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if response["chartofaccount"]:
            group = models.chartofaccount.objects.filter(
                id=instance.chartofaccount.id)
            group_response = []
            for i in group:
                group_response.append(chartofaccountSerilizer(i).data)
            response["Subgroup"] = group_response[0]["account_name"]
            response["Group"] = group_response[0]["Group"][0]["account_name"]
            response["print"] = group_response
            if response["increase"]:
                response["type"] = group_response[0]["normally_Debit"]

        if response["contact"]:
            contact = contactModel.contact.objects.filter(
                id=instance.contact.id)
            contact_response = []
            for i in contact:
                contact_response.append(
                    contactSerializer.contactSerializer(i).data)
            response["Contact"] = contact_response

        if response["location"]:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response

        if response["employee"]:
            employee = contactModel.UserProfile.objects.filter(
                id=instance.employee.id)
            employee_response = []
            for i in employee:
                employee_response.append(
                    contactSerializer.UserProfileSerializer(i).data)
            response["Employee"] = employee_response

        if response["account"]:
            account = models.account.objects.filter(
                id=instance.account.id)
            account_response = []
            for i in account:
                account_response.append(
                    accountSerilizer(i).data)
            response["Account"] = account_response

        if response["invoice"]:
            invoice = orderModel.invoice.objects.filter(
                id=instance.invoice.id)
            invoice_response = []
            for i in invoice:
                invoice_response.append(
                    orderSerializer.Invoiceserializers(i).data)
            response["Invoice"] = invoice_response

        if response["purchasee"]:
            purchasee = orderModel.purchase.objects.filter(
                id=instance.purchasee.id)
            purchasee_response = []
            for i in purchasee:
                purchasee_response.append(
                    orderSerializer.Purchaseserializers(i).data)
            response["Purchasee"] = purchasee_response
        return response


class receivevoucherSerilizer(serializers.ModelSerializer):
    payment_methods = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.receivevoucher
        fields = '__all__'
    
    def get_payment_methods(self, obj):
        result = []
        transections = []
        journal_items = models.receivevoucheritems.objects.filter(receivevoucher=obj)
        accounts = models.account.objects.all()
        for item in journal_items:
            if item.account:
                for account in accounts:
                    if account.id == item.account.id:
                        transections.append({"method": account.name, "amount": item.amount, "is_increase": item.increase})
        unique_methods = {transection['method'] for transection in transections}
        
        for unique_item in unique_methods:
            amount = 0
            for transection in transections:
                
                if transection["is_increase"] and unique_item == transection["method"]:
                    amount += transection["amount"]
                elif transection["is_increase"] == False and unique_item == transection["method"]:
                    amount -= transection["amount"]
            result.append({"method": unique_item, "amount": amount})
        return result

    def to_representation(self, instance):
        response = super().to_representation(instance)

        if response["location"]:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response

        if response["employee"]:
            employee = contactModel.UserProfile.objects.filter(
                id=instance.employee.id)
            employee_response = []
            for i in employee:
                employee_response.append(
                    contactSerializer.UserProfileSerializer(i).data)
            response["Employee"] = employee_response

        if response["contact"]:
            contact = contactModel.contact.objects.filter(
                id=instance.contact.id)
            contact_response = []
            for i in contact:
                contact_response.append(
                    contactSerializer.contactSerializer(i).data)
            response["Contact"] = contact_response

        if response["account"]:
            account = models.account.objects.filter(
                id=instance.account.id)
            account_response = []
            for i in account:
                account_response.append(
                    accountSerilizer(i).data)
            response["Account"] = account_response

        if response["invoice"]:
            invoice = orderModel.invoice.objects.filter(
                id=instance.invoice.id)
            invoice_response = []
            for i in invoice:
                invoice_response.append(
                    orderSerializer.Invoiceserializers(i).data)
            response["Invoice"] = invoice_response

        if response["purchasee"]:
            purchasee = orderModel.purchase.objects.filter(
                id=instance.purchasee.id)
            purchasee_response = []
            for i in purchasee:
                purchasee_response.append(
                    orderSerializer.Purchaseserializers(i).data)
            response["Purchasee"] = purchasee_response
        return response


class receivevoucheritemsSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.receivevoucheritems
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if response["chartofaccount"]:
            group = models.chartofaccount.objects.filter(
                id=instance.chartofaccount.id)
            group_response = []
            for i in group:
                group_response.append(chartofaccountSerilizer(i).data)
            response["Subgroup"] = group_response[0]["account_name"]
            response["Group"] = group_response[0]["Group"][0]["account_name"]
            response["print"] = group_response
            if response["increase"]:
                response["type"] = group_response[0]["normally_Debit"]

        if response["contact"]:
            contact = contactModel.contact.objects.filter(
                id=instance.contact.id)
            contact_response = []
            for i in contact:
                contact_response.append(
                    contactSerializer.contactSerializer(i).data)
            response["Contact"] = contact_response

        if response["location"]:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response

        if response["employee"]:
            employee = contactModel.UserProfile.objects.filter(
                id=instance.employee.id)
            employee_response = []
            for i in employee:
                employee_response.append(
                    contactSerializer.UserProfileSerializer(i).data)
            response["Employee"] = employee_response

        if response["account"]:
            account = models.account.objects.filter(
                id=instance.account.id)
            account_response = []
            for i in account:
                account_response.append(
                    accountSerilizer(i).data)
            response["Account"] = account_response

        if response["invoice"]:
            invoice = orderModel.invoice.objects.filter(
                id=instance.invoice.id)
            invoice_response = []
            for i in invoice:
                invoice_response.append(
                    orderSerializer.Invoiceserializers(i).data)
            response["Invoice"] = invoice_response

        if response["purchasee"]:
            purchasee = orderModel.purchase.objects.filter(
                id=instance.purchasee.id)
            purchasee_response = []
            for i in purchasee:
                purchasee_response.append(
                    orderSerializer.Purchaseserializers(i).data)
            response["Purchasee"] = purchasee_response
        return response


class journalvoucherSerilizer(serializers.ModelSerializer):
    payment_methods = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.journalvoucher
        fields = '__all__'

    
    def get_payment_methods(self, obj):
        result = []
        transections = []
        journal_items = models.journalvoucheritems.objects.filter(journalvoucher=obj)
        accounts = models.account.objects.all()
        for item in journal_items:
            if item.account:
                for account in accounts:
                    if account.id == item.account.id:
                        transections.append({"method": account.name, "amount": item.amount, "is_increase": item.increase})
        unique_methods = {transection['method'] for transection in transections}
        
        for unique_item in unique_methods:
            amount = 0
            for transection in transections:
                
                if transection["is_increase"] and unique_item == transection["method"]:
                    amount += transection["amount"]
                elif transection["is_increase"] == False and unique_item == transection["method"]:
                    amount -= transection["amount"]
            result.append({"method": unique_item, "amount": abs(amount)})
        return result

    def to_representation(self, instance):
        response = super().to_representation(instance)

        if response["location"]:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response

        if response["employee"]:
            employee = contactModel.UserProfile.objects.filter(
                id=instance.employee.id)
            employee_response = []
            for i in employee:
                employee_response.append(
                    contactSerializer.UserProfileSerializer(i).data)
            response["Employee"] = employee_response

        if response["contact"]:
            contact = contactModel.contact.objects.filter(
                id=instance.contact.id)
            contact_response = []
            for i in contact:
                contact_response.append(
                    contactSerializer.contactSerializer(i).data)
            response["Contact"] = contact_response

        if response["account"]:
            account = models.account.objects.filter(
                id=instance.account.id)
            account_response = []
            for i in account:
                account_response.append(
                    accountSerilizer(i).data)
            response["Account"] = account_response

        if response["invoice"]:
            invoice = orderModel.invoice.objects.filter(
                id=instance.invoice.id)
            invoice_response = []
            for i in invoice:
                invoice_response.append(
                    orderSerializer.Invoiceserializers(i).data)
            response["Invoice"] = invoice_response

        if response["purchasee"]:
            purchasee = orderModel.purchase.objects.filter(
                id=instance.purchasee.id)
            purchasee_response = []
            for i in purchasee:
                purchasee_response.append(
                    orderSerializer.Purchaseserializers(i).data)
            response["Purchasee"] = purchasee_response
        return response


class journalvoucheritemsSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.journalvoucheritems
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if response["chartofaccount"]:
            group = models.chartofaccount.objects.filter(
                id=instance.chartofaccount.id)
            group_response = []
            for i in group:
                group_response.append(chartofaccountSerilizer(i).data)
            response["Subgroup"] = group_response[0]["account_name"]
            response["Group"] = group_response[0]["Group"][0]["account_name"]
            response["print"] = group_response
            if response["increase"]:
                response["type"] = group_response[0]["normally_Debit"]

        if response["contact"]:
            contact = contactModel.contact.objects.filter(
                id=instance.contact.id)
            contact_response = []
            for i in contact:
                contact_response.append(
                    contactSerializer.contactSerializer(i).data)
            response["Contact"] = contact_response

        if response["location"]:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response

        if response["employee"]:
            employee = contactModel.UserProfile.objects.filter(
                id=instance.employee.id)
            employee_response = []
            for i in employee:
                employee_response.append(
                    contactSerializer.UserProfileSerializer(i).data)
            response["Employee"] = employee_response

        if response["account"]:
            account = models.account.objects.filter(
                id=instance.account.id)
            account_response = []
            for i in account:
                account_response.append(
                    accountSerilizer(i).data)
            response["Account"] = account_response

        if response["invoice"]:
            invoice = orderModel.invoice.objects.filter(
                id=instance.invoice.id)
            invoice_response = []
            for i in invoice:
                invoice_response.append(
                    orderSerializer.Invoiceserializers(i).data)
            response["Invoice"] = invoice_response

        if response["purchasee"]:
            purchasee = orderModel.purchase.objects.filter(
                id=instance.purchasee.id)
            purchasee_response = []
            for i in purchasee:
                purchasee_response.append(
                    orderSerializer.Purchaseserializers(i).data)
            response["Purchasee"] = purchasee_response
        return response


class contravoucherSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.contravoucher
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)

        if response["location"]:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response

        if response["employee"]:
            employee = contactModel.UserProfile.objects.filter(
                id=instance.employee.id)
            employee_response = []
            for i in employee:
                employee_response.append(
                    contactSerializer.UserProfileSerializer(i).data)
            response["Employee"] = employee_response

        if response["accountFrom"]:
            account = models.account.objects.filter(
                id=instance.accountFrom.id)
            account_response = []
            for i in account:
                account_response.append(
                    accountSerilizer(i).data)
            response["AccountFrom"] = account_response

        if response["accountTo"]:
            account = models.account.objects.filter(
                id=instance.accountTo.id)
            account_response = []
            for i in account:
                account_response.append(
                    accountSerilizer(i).data)
            response["AccountTo"] = account_response

        return response


class pettycashSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.pettycash
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)

        if response["location"]:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response
            response["Location_name"] = location_response[0]["name"]

        if response["employee"]:
            employee = contactModel.UserProfile.objects.filter(
                id=instance.employee.id)
            employee_response = []
            for i in employee:
                employee_response.append(
                    contactSerializer.UserProfileSerializer(i).data)
            response["Employee"] = employee_response
            response["Employee_name"] = employee_response[0]["name"]
        return response


class pettycashTransferSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.pettycash_transfer
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)

        if response["location"]:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response
            response["Location_name"] = location_response[0]["name"]

        if response["account"]:
            account = models.account.objects.filter(
                id=instance.account.id)
            account_response = []
            for i in account:
                account_response.append(
                    accountSerilizer(i).data)
            response["Account"] = account_response
            response["Account_name"] = account_response[0]["name"]
        return response
