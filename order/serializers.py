from tokenize import Double
from rest_framework import serializers
from order import models
from accounting import models as accountModel
from accounting import serializers as accountSerializer
from product import models as productModel
from product import serializers as productSerializer
from contact import models as contactModel
from contact import serializers as contactSerializer
from hrm import models as hrmModel
from hrm import serializers as hrmSerializer
from django.contrib.admin.models import LogEntry
from decimal import Decimal


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


class DeliveryypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeliveryType
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
            employe = hrmModel.Employee.objects.filter(
                id=instance.employe.id)
            employe_response = []
            for i in employe:
                employe_response.append(
                    hrmSerializer.EmployeeSerializer(i).data)
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
            location = hrmModel.Office.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    hrmSerializer.OfficeSerializer(i).data)
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
    employe = hrmSerializer.EmployeeSerializer(
        read_only=True)
    contact = contactSerializer.contactSerializer(read_only=True)
    account = accountSerializer.accountSerilizer(read_only=True)
    location = hrmSerializer.OfficeSerializer(read_only=True)
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
                        transections.append(
                            {"method": account.name, "amount": item.amount, "is_increase": item.increase})
        unique_methods = {transection['method']
                          for transection in transections}

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

        return response
    
class InvoicePaymentserializers(serializers.ModelSerializer):
    class Meta:
        model = models.invoice_payment
        fields = '__all__'


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

        if instance.invoice:
            invoice = models.invoice.objects.filter(
                id=instance.invoice.id
            ).first()
            if invoice:
                response["Invoice"] = Invoiceserializers(invoice).data


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
            response["Discount"] = instance.invoice.discount
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
            response["Discount"] = instance.invoice.discount
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
            response["invoice_id"] = instance.invoice.id
            response["invoice_number"] = instance.invoice.invoice_number
            response["order_number"] = instance.invoice.order_number
            # response["invoice"] = [response["invoice"]]
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
        # contact = contactModel.contact.objects.filter(
        #     id=instance.contact.id)
        # contact_response = []
        # for i in contact:
        #     contact_response.append(
        #         contactSerializer.contactSerializer(i).data)
        # response["Contact"] = contact_response

        if instance.location:
            location = hrmModel.Office.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    hrmSerializer.OfficeSerializer(i).data)
            response["Location"] = location_response

        # if instance.employe:
        #     employe = hrmModel.Employee.objects.filter(
        #         id=instance.employe.id)
        #     employe_response = []
        #     for i in employe:
        #         employe_response.append(
        #             hrmSerializer.EmployeeSerializer(i).data)
        #     response["Employee"] = employe_response

        # if instance.account:
        #     account = accountModel.account.objects.filter(
        #         id=instance.account.id)
        #     account_response = []
        #     for i in account:
        #         account_response.append(
        #             accountSerializer.accountSerilizer(i).data)
        #     response["Account"] = account_response

        return response


class PurchaseseReadrializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    contact = contactSerializer.contactSerializer(read_only=True)
    location = hrmSerializer.OfficeSerializer(read_only=True)
    account = accountSerializer.accountSerilizer(read_only=True)
    employe = hrmSerializer.EmployeeSerializer(
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
            location = hrmModel.Office.objects.filter(
                id=instance.location.id)
            location_response = []
            for i in location:
                location_response.append(
                    hrmSerializer.OfficeSerializer(i).data)
            response["Location"] = location_response
            response["Location_name"] = location_response[0]['name']

        return response


class WordrobeReadserializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    contact = contactSerializer.contactSerializer(read_only=True)
    location = hrmSerializer.OfficeSerializer(read_only=True)

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
    location = hrmSerializer.OfficeSerializer(read_only=True)
    account = accountSerializer.accountSerilizer(read_only=True)
    employe = hrmSerializer.EmployeeSerializer(read_only=True)
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


class InvoiceVatSerializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    contact = contactSerializer.contactSerializer(read_only=True)
    cupon = Cuponserializers(read_only=True)
    location = hrmSerializer.OfficeSerializer(read_only=True)
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
                        transections.append(
                            {"method": account.name, "amount": item.amount, "is_increase": item.increase})
        unique_methods = {transection['method']
                          for transection in transections}

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
            printarray.append({**item, **payment})
        response["printarray"] = printarray
        return response


# Draft Order Serializers==============================


# class DraftCostSheetSerializer(serializers.ModelSerializer):
#     orders = DraftOrderSerializer(many=True, read_only=True)
#     image = DraftImageSerializer(read_only=True)
#     # data = JSONSerializerField()

#     class Meta:
#         model = models.DraftCostSheet
#         fields = ('id', 'style_name', 'client_name', 'style_code',
#                   'designer_name', 'description', 'quantity', 'date',
#                   'net_total_cost', 'profit_percentage', 'net_selling_price',
#                   'orders', 'image')
#         read_only_fields = ('net_total_cost', 'net_selling_price')

#         def to_representation(self, instance):
#             response = super().to_representation(instance)
#             response["id"] = instance.id
#             response["style_name"] = instance.style_name
#             response["style_code"] = instance.style_code
#             response["client_name"] = instance.client_name
#             response["designer_name"] = instance.designer_name
#             response["description"] = instance.description
#             response["quantity"] = instance.quantity
#             response["date"] = instance.date
#             response["product_image"] = instance.image.product_image
#             response["cost_sheet"] = instance.orders.cost_sheet
#             response["cost_sheet_items"] = instance.orders.cost_sheet_items
#             response["unit_quantity"] = instance.orders.unit_quantity
#             response["unit_name"] = instance.orders.unit_name
#             response["unit_price"] = instance.orders.unit_price
#             response["amount"] = instance.orders.amount
#             # response["date"] = instance.date
#             # response["quantity"] = instance.quantity
#             response["net_total_cost"] = instance.net_total_cost
#             response["profit_percentage"] = instance.profit_percentage
#             response["net_selling_price"] = instance.net_selling_price
#             return response


class DraftCostSheetSerializer(serializers.ModelSerializer):
    data = JSONSerializerField()
    
    class Meta:
        model = models.DraftCostSheet
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["id"] = instance.id
        response["style_name"] = instance.style_name
        response["style_code"] = instance.style_code
        response["client_name"] = instance.client_name
        response["designer_name"] = instance.designer_name
        response["description"] = instance.description
        response["quantity"] = instance.quantity
        response["date"] = instance.date
        # DraftOrder start
        draftOrder = models.DraftOrder.objects.filter(cost_sheet=instance.id)
        draftOrder_response = []
        for i in draftOrder:
            # draftOrder_response.append(get_draft_order_response(i, instance.cost_sheet_items))
            draftOrder_response.append(DraftOrderSerializer(i).data)
        response["draftOrder"] = draftOrder_response
        # DraftOrder end
        draftImage = models.DraftImage.objects.filter(cost_sheet=instance.id)
        draftImage_response = []
        for i in draftImage:
            draftImage_response.append(DraftImageSerializer(i).data)
        response["draftImage"] = draftImage_response
        return response

def get_draft_order_response(draft_order, cost_sheet_items):
    response = {}
    if cost_sheet_items is not None:
        response["cost_sheet_items"] = cost_sheet_items
        if cost_sheet_items == "Fabrics":
            response["draft_name"] = draft_order.draft_name
            response["unit_quantity"] = draft_order.unit_quantity
            response["unit_name"] = draft_order.unit_name
            response["unit_price"] = draft_order.unit_price
            response["amount"] = draft_order.amount
        elif cost_sheet_items == "Trims/Accessories":
            response["draft_name"] = draft_order.draft_name
            response["unit_quantity"] = draft_order.unit_quantity
            response["unit_name"] = draft_order.unit_name
            response["unit_price"] = draft_order.unit_price
            response["amount"] = draft_order.amount
        elif cost_sheet_items == "Labor Cost":
            response["draft_name"] = draft_order.draft_name
            response["unit_quantity"] = draft_order.unit_quantity
            response["unit_name"] = draft_order.unit_name
            response["unit_price"] = draft_order.unit_price
            response["amount"] = draft_order.amount
        else:
            response["cost_sheet_items"] = []

    return response

class DraftImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DraftImage
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        cost_sheet = instance.cost_sheet  
        if cost_sheet is not None:
            response["cost_sheet"] = cost_sheet.id
        else:
            response["cost_sheet"] = None
        # response["product_image"] = instance.product_image
        return response      

class DraftOrderSerializer(serializers.ModelSerializer):
    draft_cost_sheet = DraftCostSheetSerializer(read_only=True)

    class Meta:
        model = models.DraftOrder
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        cost_sheet = instance.cost_sheet
        if cost_sheet is not None:
            response["cost_sheet"] = cost_sheet.id
        else:
            response["cost_sheet"] = None
        response["cost_sheet_items"] = instance.cost_sheet_items

        response["draft_name"] = instance.draft_name
        response["unit_quantity"] = instance.unit_quantity
        response["unit_name"] = instance.unit_name
        response["unit_price"] = instance.unit_price
        response["amount"] = instance.amount
        return response

# class DraftOrderSerializer(serializers.ModelSerializer):
#     draft_cost_sheet = DraftCostSheetSerializer(read_only=True)

#     class Meta:
#         model = models.DraftOrder
#         fields = '__all__'

#     def to_representation(self, instance):
#         response = super().to_representation(instance)
#         cost_sheet_items = []
#         for item_name, _ in models.DraftOrder.COST_SHEET_ITEMS_CHOICES:
#             item_data = {
#                 "item_name": item_name,
#                 item_name: {
#                     "draft_name": response.get("draft_name"),
#                     "unit_quantity": response.get("unit_quantity"),
#                     "unit_name": response.get("unit_name"),
#                     "amount": response.get("amount"),
#                 }
#             }
#             cost_sheet_items.append(item_data)
#         response["cost_sheet_items"] = cost_sheet_items
#         return response

       
def get_serializer(request):
    if request.method == 'GET':
        return DraftCostSheetSerializer
    else:
        raise serializers.ValidationError('Method not allowed')

# Nested Version
class DraftCostSheetNestedSerializer(serializers.ModelSerializer):
    draft_orders = DraftOrderSerializer(many=True, read_only=True, source='draftorder_set')
    draft_images = DraftImageSerializer(many=True, read_only=True, source='draftimage_set')

    class Meta:
        model = models.DraftCostSheet
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['draft_orders'] = DraftOrderSerializer(instance.draftorder_set.all(), many=True).data
        representation['draft_images'] = DraftImageSerializer(instance.draftimage_set.all(), many=True).data
        return representation


class InvoiceItemOnlySerializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    class Meta:
        model = models.invoice_item
        fields = '__all__'

#  Invoice_Item_Copy 
class InvoiceItemCopySerializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    class Meta:
        model = models.invoice_item_copy
        fields = '__all__'
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     if instance.product:
    #         product = productModel.ProductLocation.objects.filter(
    #             id=instance.product.id)
    #         product_response = []
    #         for i in product:
    #             product_response.append(
    #                 productSerializer.ProductDetailsSerilizer(i).data)
    #         response["Product"] = product_response
    #     return response
    
class InvoiceExchangeSerializers(serializers.ModelSerializer):
    data = JSONSerializerField()
    item = InvoiceItemOnlySerializers(many=True, read_only=True, source='invoice_item_set')
    item_copy = InvoiceItemCopySerializers(many=True, read_only=True, source='invoice_item_copy_set')
    location = hrmSerializer.OfficeSerializer(read_only=True)
    # invoice_items = serializers.SerializerMethodField(read_only=True)
    # total_price = serializers.SerializerMethodField(read_only=True)
    # payment_methods = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.invoice
        fields = '__all__'