from tokenize import Double
from rest_framework import serializers
from order import models
from accounting import models as accountModel
from accounting import serializers as accountSerializer
from product import models as productModel
from product import serializers as productSerializer
from contact import models as contactModel
from contact import serializers as contactSerializer
from django.contrib.admin.models import LogEntry
from decimal import Decimal
from datetime import date


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class Cuponserializers(serializers.ModelSerializer):

    class Meta:
        model = models.cupon
        fields = '__all__'

class IPNserializers(serializers.ModelSerializer):

    class Meta:
        model = models.IPN
        fields = '__all__'


class DeliveryypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeliveryType
        fields = '__all__'

class AllOnlineOrderserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.online_order
        fields = '__all__'
        
class Invoiceserializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    # cupon = Cuponserializers(read_only=True)
    # DeliveryType = DeliveryypeSerializer(read_only=True)

    class Meta:
        model = models.invoice
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.contact:
            contact = contactModel.contact.objects.filter(
                id=instance.contact.id)
            contact_response = []
            for i in contact:
                contact_response.append(
                    contactSerializer.contactSerializer(i).data)
            response["Contact"] = contact_response
        
        if instance.Sales_person:
            response["Sales_person_name"] = instance.Sales_person.name

        if instance.cupon:
            cuponn = models.cupon.objects.filter(
                id=instance.cupon.id)
            cupon_response = []
            for i in cuponn:
                cupon_response.append(
                    Cuponserializers(i).data)
            response["cupon"] = cupon_response[0]

        if instance.employe:
            employe = contactModel.UserProfile.objects.filter(
                id=instance.employe.id)
            employe_response = []
            for i in employe:
                employe_response.append(
                    contactSerializer.EmployeeSerializer(i).data)
            response["Employe"] = employe_response
        if instance.account:
            account = accountModel.account.objects.filter(
                id=instance.account.id)
            account_response = []
            for i in account:
                account_response.append(
                    accountSerializer.accountSerilizer(i).data)
            response["Account"] = account_response
            response["Payment_method"] = account_response[0]["name"]

        if instance.location:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response
            response["Location_name"] = instance.location.name

        response["DeliveryTypeName"] = ""
        if instance.DeliveryType:
            response["DeliveryType"] = instance.DeliveryType.id
            response["DeliveryTypeName"] = instance.DeliveryType.name

        return response


class InvoiceReadserializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    # cupon = Cuponserializers(read_only=True)
    # DeliveryType = DeliveryypeSerializer(read_only=True)
    employe = contactSerializer.EmployeeWithoutpermissionSerializer(
        read_only=True)
    contact = contactSerializer.contactSerializer(read_only=True)
    account = accountSerializer.accountSerilizer(read_only=True)
    location = productSerializer.warehouseSerilizer(read_only=True)
    DeliveryType = DeliveryypeSerializer(read_only=True)
    cupon = Cuponserializers(read_only=True)
    payment_methods = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.invoice
        fields = '__all__'
    
    def get_payment_methods(self, obj):
        result = []
        transections = []
        journal_items = accountModel.journal.objects.filter(invoice=obj)
        accounts = accountModel.account.objects.all()
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
        response["Contact"] = [response["contact"]]
    
        if instance.cupon:
            response["cupon"] = response["cupon"]

        if instance.employe:
            response["Employe"] = [response["employe"]]
            
        if instance.Sales_person:
            response["Sales_person_name"] = instance.Sales_person.name

        if instance.account:
            response["Payment_method"] = response["account"]["name"]

        if instance.location:
            response["Location"] = [response["location"]]
            response["Location_name"] = response["location"]['name']
            response["location"] = response["location"]['id']

        if instance.account:
            response["Account"] = [response["account"]]
            response["account"] = response["account"]["id"]

        response["DeliveryTypeName"] = ""
        if instance.DeliveryType:
            response["DeliveryTypeName"] = response["DeliveryType"]["name"]
            response["DeliveryType"] = response["DeliveryType"]["id"]
        
        
        status = ""
        if instance.delivery_date:
            if instance.delivered_date:
                delta = instance.delivery_date - instance.delivered_date
                if delta.days > 0:
                    status = "On time delivery"
                else:
                    status = str(abs(delta.days)) + " days delayed"
            else:
                delta = instance.delivery_date - date.today()
                if delta.days > 0:
                    status = str(abs(delta.days)) + " days remianing"
                else:
                    status = str(abs(delta.days)) + " days delayed"
            # print(status)
        else:
            status = ""
        response["delivery_status"] = status

        return response


class InvoiceReportserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.invoice
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.sum:
            response['total'] = instance.sum
        if instance.count:
            response['number'] = instance.count

        contact = contactModel.contact.objects.filter(
            id=instance.contact.id)
        contact_response = []
        for i in contact:
            contact_response.append(
                contactSerializer.contactSerializer(i).data)
        response["Contact"] = contact_response
        return response


class InvoiceReportReadserializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    contact = contactSerializer.contactSerializer(read_only=True, many=True)

    class Meta:
        model = models.invoice
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.sum:
            response['total'] = instance.sum
        if instance.count:
            response['number'] = instance.count

        response["Contact"] = response["contact"]
        return response


class InvoiceItemserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.invoice_item
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.product:
            product = productModel.ProductLocation.objects.filter(
                id=instance.product.id)
            product_response = []
            for i in product:
                product_response.append(
                    productSerializer.ProductDetailsSerilizer(i).data)
            response["Product"] = product_response
        
        return response


class InvoiceItemReadserializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    product = productSerializer.ProductDetailsSerilizer(read_only=True)

    class Meta:
        model = models.invoice_item
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.product:
            response["Product"] = [response["product"]]
        if instance.invoice:
            response["Invoice_no"] = instance.invoice.invoice_number
            if instance.invoice.contact:
                response["Customer"] = instance.invoice.contact.name
                response["Contact"] = instance.invoice.contact.phone
        if instance.product:
            if instance.product.ProductDetails:
                if instance.product.ProductDetails.Category:
                    response["main_category"] = instance.product.ProductDetails.Category.name
                    if instance.product.ProductDetails.Category.Category_parent:
                        response["parent_category"] = instance.product.ProductDetails.Category.Category_parent.name
            
                
        return response


class InvoiceItemSOldReadserializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    # product = productSerializer.ProductDetailsSerilizer(read_only=True)

    class Meta:
        model = models.invoice_item
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.product:
            response["Product"] = [response["product"]]
        if instance.invoice:
            response["Invoice_no"] = instance.invoice.invoice_number
            if instance.invoice.contact:
                response["Customer"] = instance.invoice.contact.name
                response["Contact"] = instance.invoice.contact.phone
        if instance.product:
            if instance.product.ProductDetails:
                if instance.product.ProductDetails.Category:
                    response["main_category"] = instance.product.ProductDetails.Category.name
                    if instance.product.ProductDetails.Category.Category_parent:
                        response["parent_category"] = instance.product.ProductDetails.Category.Category_parent.name
            
                
        return response


class Measurementserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.measurement
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["measuremnt_name"] = "Invoice measurment"
        if instance.product:            
            response["measuremnt_name"] = instance.product.ProductDetails.title
        if instance.service:            
            response["measuremnt_name"] = instance.service.details
        return response
    
    


class Servicesserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.services
        fields = '__all__'

    def to_representation(self, instance):

        response = super().to_representation(instance)
        if instance.invoice:
            # invoice = models.invoice.objects.filter(
            #     id=instance.invoice.id)
            # invoice_response = []
            # for i in invoice:
            #     invoice_response.append(
            #         Invoiceserializers(i).data)
            # response["delivery_date"] = invoice_response[0]['delivery_date']
            # response["invoice_id"] = invoice_response[0]['id']
            # response["invoice_number"] = invoice_response[0]['invoice_number']
            # response["order_number"] = invoice_response[0]['order_number']
            
            response["delivery_date"] = instance.invoice.delivery_date
            response["invoice_id"] = instance.invoice.id
            response["invoice_number"] = instance.invoice.invoice_number
            response["order_number"] = instance.invoice.order_number

        return response


class ServicesReadserializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    # invoice = Invoiceserializers(read_only=True)
    # employee = contactSerializer.EmployeeSerializer(read_only=True)
    # employe = contactSerializer.EmployeeSerializer(read_only=True)

    class Meta:
        model = models.services
        fields = '__all__'
    
    

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.invoice:
            response["delivery_date"] = instance.invoice.delivery_date
            response["Received_by_factory_date"] = instance.invoice.Received_by_factory_date
            response["delivered_date"] = instance.invoice.delivered_date
            response["invoice_id"] = instance.invoice.id
            response["invoice_number"] = instance.invoice.invoice_number
            response["order_number"] = instance.invoice.order_number
            if instance.product:
                product = instance.product.ProductDetails.title
                if instance.product.Color:
                    product = product + " - " + instance.product.Color.name
                if instance.product.Size:
                    product = product + " / " + instance.product.Size.name
                # print(instance.product)
                response["product_name"] = product
            else:
                response["product_name"] = "Individual service"
            status = ""
            if instance.invoice.delivery_date:
                if instance.invoice.delivered_date:
                    delta = instance.invoice.delivery_date - instance.invoice.delivered_date
                    if delta.days > 0:
                        status = "On time delivery"
                    else:
                        status = str(abs(delta.days)) + " days delayed"
                else:
                    delta = instance.invoice.delivery_date - date.today()
                    if delta.days > 0:
                        status = str(abs(delta.days)) + " days remianing"
                    else:
                        status = str(abs(delta.days)) + " days delayed"
                # print(status)
            response["delivery_status"] = status
        return response


class Services_costingserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.services_costing
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.product:
            product = productModel.ProductLocation.objects.filter(
                id=instance.product.id)
            product_response = []
            for i in product:
                product_response.append(
                    productSerializer.ProductDetailsSerilizer(i).data)
            response["Material"] = product_response[0]
        return response


class Services_costingReadserializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    product = productSerializer.ProductDetailsSerilizer(read_only=True)

    class Meta:
        model = models.services_costing
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.product:
            response["Material"] = response["product"]
            response["Product"] = [response["product"]]
        return response


class Purchaseserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.purchase
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        contact = contactModel.contact.objects.filter(
            id=instance.contact.id)
        contact_response = []
        for i in contact:
            contact_response.append(
                contactSerializer.contactSerializer(i).data)
        response["Contact"] = contact_response

        if instance.location:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response

        if instance.employe:
            employe = contactModel.UserProfile.objects.filter(
                id=instance.employe.id)
            employe_response = []
            for i in employe:
                employe_response.append(
                    contactSerializer.EmployeeSerializer(i).data)
            response["Employee"] = employe_response

        if instance.account:
            account = accountModel.account.objects.filter(
                id=instance.account.id)
            account_response = []
            for i in account:
                account_response.append(
                    accountSerializer.accountSerilizer(i).data)
            response["Account"] = account_response

        return response


class PurchaseseReadrializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    contact = contactSerializer.contactSerializer(read_only=True)
    location = productSerializer.warehouseSerilizer(read_only=True)
    account = accountSerializer.accountSerilizer(read_only=True)
    employe = contactSerializer.EmployeeWithoutpermissionSerializer(
        read_only=True)

    class Meta:
        model = models.purchase
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)

        if instance.contact:
            response["Contact"] = [response["contact"]]

        if instance.location:
            response["Location"] = [response["location"]]
            response["location"] = response["location"]["id"]

        if instance.employe:
            response["Employee"] = [response["employe"]]

        if instance.account:
            response["Account"] = [response["account"]]
            response["account"] = response["account"]["id"]

        return response


class PurchaseItemserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.purchase_item
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.product:
            product = productModel.ProductLocation.objects.filter(
                id=instance.product.id)
            product_response = []
            for i in product:
                product_response.append(
                    productSerializer.ProductDetailsSerilizer(i).data)
            response["Product"] = product_response
        return response


class PurchaseItemsReaderializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    product = productSerializer.ProductDetailsSerilizer(read_only=True)

    class Meta:
        model = models.purchase_item
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.product:
            response["Product"] = [response["product"]]
        return response


class Wordrobeserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.wordrobe
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.contact:
            contact = contactModel.contact.objects.filter(
                id=instance.contact.id)
            contact_response = []
            for i in contact:
                contact_response.append(
                    contactSerializer.contactSerializer(i).data)
            response["Contact"] = contact_response

        if instance.location:
            location = productModel.Warehouse.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    productSerializer.warehouseSerilizer(i).data)
            response["Location"] = location_response
            response["Location_name"] = location_response[0]['name']

        return response


class WordrobeReadserializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    contact = contactSerializer.contactSerializer(read_only=True)
    location = productSerializer.warehouseSerilizer(read_only=True)

    class Meta:
        model = models.wordrobe
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["Contact"] = [response["contact"]]

        if instance.location:
            response["Location"] = [response["location"]]
            response["Location_name"] = response["location"]['name']
            response["location"] = response["location"]["id"]

        return response


class WordrobeItemserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.wordrobe_item
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.product:
            product = productModel.ProductLocation.objects.filter(
                id=instance.product.id)
            product_response = []
            for i in product:
                product_response.append(
                    productSerializer.ProductDetailsSerilizer(i).data)
                response["Product"] = product_response
                response["title"] = product_response[0]["title"]
                response["category"] = product_response[0]["category"]
                # if product_response[0]["color"]:
                #     response["color"] = product_response[0]["color"]
                response["Warehouse_name"] = product_response[0]["Warehouse_name"]
                # if product_response[0]["size"]:
                #     response["size"] = product_response[0]["size"]
                response["barcode"] = product_response[0]["barcode"]

        wordrobe = models.wordrobe.objects.filter(
            id=instance.wordrobe.id)
        wordrobe_response = []
        for i in wordrobe:
            wordrobe_response.append(
                Wordrobeserializers(i).data)
            response["Wordrobe"] = wordrobe_response
            response["wordrobe_number"] = wordrobe_response[0]["wordrobe_number"]
        return response


class WordrobeItemReadserializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    product = productSerializer.ProductDetailsSerilizer(read_only=True)
    wordrobe = Wordrobeserializers(read_only=True)

    class Meta:
        model = models.wordrobe_item
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.product:
            response["Product"] = [response["product"]]
            response["title"] = response["product"]["title"]
            response["category"] = response["product"]["category"]
            response["Warehouse_name"] = response["product"]["Warehouse_name"]
            response["barcode"] = response["product"]["barcode"]

        if instance.wordrobe:
            response["Wordrobe"] = [response["wordrobe"]]
            response["wordrobe_number"] = response["wordrobe"]["wordrobe_number"]
        return response


class ClientInvoiceSerializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    contact = contactSerializer.contactSerializer(read_only=True)
    cupon = Cuponserializers(read_only=True, many=True)
    location = productSerializer.warehouseSerilizer(read_only=True)
    account = accountSerializer.accountSerilizer(read_only=True)
    employe = contactSerializer.EmployeeSerializer(read_only=True)
    invoice_items = serializers.SerializerMethodField(read_only=True)
    measurement = serializers.SerializerMethodField(read_only=True)
    services = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.invoice
        fields = '__all__'

    def get_invoice_items(self, obj):
        invoice_items = models.invoice_item.objects.filter(invoice=obj)
        return InvoiceItemserializers(invoice_items, many=True).data

    def get_measurement(self, obj):
        measurement = models.measurement.objects.filter(invoice=obj)
        return Measurementserializers(measurement, many=True).data

    def get_services(self, obj):
        services = models.services.objects.filter(invoice=obj)
        return Servicesserializers(services, many=True).data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["Contact"] = [response["contact"]]
        return response

class SalesPersonSerializers(serializers.ModelSerializer):
    # data = JSONSerializerField()
    # location = productSerializer.warehouseSerilizer(read_only=True)
    # total_price = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = models.invoice
        fields = '__all__'

    # def get_total_price(self, obj):
    #     invoice_items = models.invoice_item.objects.filter(invoice=obj)
    #     total_price = 0
    #     for item in invoice_items:
    #         total_price = Decimal(total_price) + \
    #             Decimal(item.quantity) * Decimal(item.price)
    #     service_items = models.services.objects.filter(invoice=obj)
    #     for item in service_items:
    #         total_price = Decimal(total_price) + \
    #             Decimal(item.quantity) * Decimal(item.price)
       
    #     return total_price

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     return response

class InvoiceVatSerializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    contact = contactSerializer.contactSerializer(read_only=True)
    cupon = Cuponserializers(read_only=True)
    location = productSerializer.warehouseSerilizer(read_only=True)
    account = accountSerializer.accountSerilizer(read_only=True)
    invoice_items = serializers.SerializerMethodField(read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)
    payment_methods = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.invoice
        fields = '__all__'

    def get_invoice_items(self, obj):
        result = []
        invoice_items = models.invoice_item.objects.filter(invoice=obj)
        service_items = models.services.objects.filter(invoice=obj)
        for item in invoice_items:
            result.append(InvoiceItemserializers(item).data)
        for item in service_items:
            result.append(Servicesserializers(item).data)
        return result

    def get_payment_methods(self, obj):
        result = []
        transections = []
        journal_items = accountModel.journal.objects.filter(invoice=obj)
        accounts = accountModel.account.objects.all()
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

    def get_total_price(self, obj):
        invoice_items = models.invoice_item.objects.filter(invoice=obj)
        total_price = 0
        for item in invoice_items:
            total_price = Decimal(total_price) + \
                Decimal(item.quantity) * Decimal(item.price)
        service_items = models.services.objects.filter(invoice=obj)
        for item in service_items:
            total_price = Decimal(total_price) + \
                Decimal(item.quantity) * Decimal(item.price)
       
        return total_price

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["Contact"] = [response["contact"]]
        # total price = total invoice items selling price
        # payment,bill = total price - invoice discount
        # response["payment"] = Decimal(
        #     response["total_price"]) - Decimal(response["discount"])
        # response["bill"] = response["payment"]
        toplength = 0
        if len(response["invoice_items"]) > len(response["payment_methods"]):
            toplength = len(response["invoice_items"])
        else:
            toplength = len(response["payment_methods"])
        
        
        printarray = []
        for i in range(toplength):
            item = {}
            payment = {}
            if len(response["invoice_items"]) == toplength or len(response["invoice_items"]) > i:
               
                item = response["invoice_items"][i]
            if len(response["payment_methods"]) == toplength or len(response["payment_methods"]) > i:
                
                payment = response["payment_methods"][i]
            printarray.append({**item,**payment})
        response["printarray"] = printarray
        return response


class Refundserializers(serializers.ModelSerializer):
    # data = JSONSerializerField()

    class Meta:
        model = models.Refund
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.invoice:
            response["invoice_number"] = instance.invoice.invoice_number
            response["contact"] = instance.invoice.contact.name
            response["outlet"] = instance.invoice.location.name
        if instance.in_account:
            response["in_method"] = instance.out_account.name
        if instance.out_account:
            response["out_method"] = instance.out_account.name
        return response


class RefundItemserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.Refund_item
        fields = '__all__'