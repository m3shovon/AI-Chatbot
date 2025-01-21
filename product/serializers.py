from rest_framework import serializers
from product import models
from hrm import models as hrmModel
from hrm import serializers as hrmSerializer


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class AttributeTermSerilizer(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.AttributeTerm
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["title"] = instance.name
        response["key"] = instance.id
        response["value"] = instance.id
        return response


class AttributeSerilizer(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.Attribute
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        terms = models.AttributeTerm.objects.filter(Attribute=instance.id)
        terms_response = []
        for i in terms:
            terms_response.append(AttributeTermSerilizer(i).data)
        response["terms"] = terms_response

        return response


class AllCategoryProductSerilizer(serializers.ModelSerializer):
    data = JSONSerializerField()
    children_product = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Category
        fields = '__all__'

    def get_children_product(self, obj):
        category = models.Category.objects.filter(id=obj.id)
        category_list = list((category).values_list('id', flat=True))
        product_list = []
        for obj in category_list:
            products = models.ProductDetails.objects.filter(
                Category__id=obj, is_active=True)
            products_listD = list((products).values_list('id', flat=True))
            product_list.extend(products_listD)
            childs = models.Category.objects.filter(Category_parent__id=obj)
            child_list = list((childs).values_list('id', flat=True))
            category_list.extend(child_list)
        queryset = models.ProductDetails.objects.filter(id__in=product_list)
        return CategorySingleProductSerilizer(queryset, many=True).data

    def to_representation(self, instance):

        response = super().to_representation(instance)
        response['title'] = instance.name
        response['key'] = instance.id
        response['value'] = instance.id
        return response


class CategoryProductSerilizer(serializers.ModelSerializer):
    data = JSONSerializerField()
    children = serializers.SerializerMethodField(read_only=True)
    children_product = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Category
        fields = '__all__'

    def get_children(self, obj):
        category = models.Category.objects.filter(Category_parent=obj)
        if category is not None:
            return CategoryProductSerilizer(category, many=True).data
        else:
            return None

    def get_children_product(self, obj):
        category_product = models.ProductDetails.objects.filter(
            Category=obj, is_active=True)
        if category_product is not None:
            return CategorySingleProductSerilizer(category_product, many=True).data
        else:
            return None

    def to_representation(self, instance):

        response = super().to_representation(instance)
        response['title'] = instance.name
        response['key'] = instance.id
        response['value'] = instance.id
        return response


class CategorySingleProductSerilizer(serializers.ModelSerializer):
    data = JSONSerializerField()
    variations = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.ProductDetails
        fields = '__all__'

    def get_variations(self, obj):
        variation = models.ProductLocation.objects.filter(ProductDetails=obj)
        if variation is not None:
            return ProductDetailsSerilizer(variation, many=True).data
        else:
            return None

    def to_representation(self, instance):

        response = super().to_representation(instance)
        variation = models.ProductLocation.objects.filter(
            ProductDetails=instance)
        total_purchase_price = 0
        for var in variation:
            total_purchase_price = total_purchase_price + \
                (float(var.purchase_price) * float(var.quantity))
        response['total_purchase_price'] = total_purchase_price

        return response


class SingleCategorySerilizer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['title'] = instance.name
        response['key'] = instance.id
        response['value'] = instance.id
        return response


class CategorySerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    data = JSONSerializerField()
    children = serializers.SerializerMethodField(read_only=True)
    # parent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Category
        fields = '__all__'

    def get_children(self, obj):
        # query what your want here.
        # print(obj)
        category = models.Category.objects.filter(Category_parent=obj)
        if category is not None:
            return CategorySerilizer(category, many=True).data
        else:
            return None

    def to_representation(self, instance):

        response = super().to_representation(instance)
        response['title'] = instance.name
        response['key'] = instance.id
        response['value'] = instance.id
        response['immediate_parent'] = SingleCategorySerilizer(
            instance.Category_parent).data
        # response['response'] = response

        return response


class CategoryForProductSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    data = JSONSerializerField()
    # children = serializers.SerializerMethodField(read_only=True)
    parent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Category
        fields = '__all__'

    def get_parent(self, obj):
        # query what your want here.
        # print(obj)
        while obj.Category_parent is not None:
            obj = obj.Category_parent
        return SingleCategorySerilizer(obj).data

    def to_representation(self, instance):

        response = super().to_representation(instance)
        # parent = models.Category.objects.filter(Category_parent=instance.id)
        # parent_response = []
        # for i in parent:
        #     parent_response.append(CategorySerilizer(i).data)
        # response["children"] = parent_response

        response['title'] = instance.name
        response['key'] = instance.id
        response['value'] = instance.id
        response['immediate_parent'] = SingleCategorySerilizer(
            instance.Category_parent).data
        # response['response'] = response

        return response


class CategoryUpdateSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    data = JSONSerializerField()

    class Meta:
        model = models.Category
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for the Product Media object"""

    class Meta:
        model = models.ProductImage
        fields = "__all__"
        
    
class ProductwithalldetailsSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    Category = CategoryForProductSerilizer(read_only=True)

    class Meta:
        model = models.ProductDetails
        fields = '__all__'

    def to_representation(self, instance):

        response = super().to_representation(instance)
        if instance.Category:
            # main parent
            response["parent_category"] = response["Category"]["parent"]["name"]

            if response["Category"]["immediate_parent"]["name"] == "":
                # immideiate parent
                response["main_category"] = response["Category"]["title"]
                response["category_name"] = ""  # own category
            else:
                response["main_category"] = response["Category"]["immediate_parent"]["name"]
                # own category
                response["category_name"] = response["Category"]["title"]
        
        variations_response = []
        variations = models.ProductLocation.objects.filter(
            ProductDetails__id=instance.id)
        for i in variations:
            variations_response.append(ProductDetailsSerilizer(i).data)
        response["variations"] = variations_response

        # images = models.ProductImage.objects.filter(
        #     ProductDetails__id=instance.id)
        # cover_response = []
        # images_response = []
        # for i in images:
        #     if i.Color is None:
        #         cover_response.append(ProductImageSerializer(i).data)
        #     images_response.append(ProductImageSerializer(i).data)
        # response["cover"] = cover_response
        # response["image"] = images_response
        return response

class singleProductSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    Category = CategoryForProductSerilizer(read_only=True)

    class Meta:
        model = models.ProductDetails
        fields = '__all__'

    def to_representation(self, instance):

        response = super().to_representation(instance)
        if instance.Category:
            # main parent
            response["parent_category"] = response["Category"]["parent"]["name"]

            if response["Category"]["immediate_parent"]["name"] == "":
                # immideiate parent
                response["main_category"] = response["Category"]["title"]
                response["category_name"] = ""  # own category
            else:
                response["main_category"] = response["Category"]["immediate_parent"]["name"]
                # own category
                response["category_name"] = response["Category"]["title"] 

        response['merchandiser_name'] = instance.Merchandiser.name if instance.Merchandiser else ""    

        images = models.ProductImage.objects.filter(
            ProductDetails__id=instance.id)
        cover_response = []
        images_response = []
        for i in images:
            if i.Color is None:
                cover_response.append(ProductImageSerializer(i).data)
            images_response.append(ProductImageSerializer(i).data)
        response["cover"] = cover_response
        response["image"] = images_response
        return response


class warehouseSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    data = JSONSerializerField()

    class Meta:
        model = models.Warehouse
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['title'] = instance.name
        response['key'] = instance.id
        response['value'] = instance.id

        return response


class warehouseListSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    data = JSONSerializerField()
    children = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Warehouse
        fields = '__all__'

    def get_children(self, obj):
        # query what your want here.
        # print(obj)
        warehouse = models.Warehouse.objects.filter(Warehouse_parent=obj)
        if warehouse is not None:
            return warehouseListSerilizer(warehouse, many=True).data
        else:
            return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['title'] = instance.name
        response['key'] = instance.id
        response['value'] = instance.id
        response['immediate_parent'] = warehouseSerilizer(
            instance.Warehouse_parent).data

        return response


class ProductDetailsSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    Warehouse = hrmSerializer.OfficeSerializer(read_only=True)
    ProductDetails = singleProductSerilizer(read_only=True)
    Color = AttributeTermSerilizer(read_only=True)
    Size = AttributeTermSerilizer(read_only=True)
    ProductImage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.ProductLocation
        fields = '__all__'

    def get_ProductImage(self, obj):
        images = models.ProductImage.objects.filter(
            ProductDetails__id=obj.ProductDetails.id)
        return ProductImageSerializer(images, many=True).data

    def to_representation(self, instance):

        response = super().to_representation(instance)

        response["Deatils"] = [response["ProductDetails"]]
        response["is_active"] = response["ProductDetails"]['is_active']
        response["title"] = response["ProductDetails"]['title']
        response["product_code"] = response["ProductDetails"]['product_code']
        response["category"] = response["ProductDetails"]['Category']['name']
        response["parent_category"] = response["ProductDetails"]['parent_category']
        # response["ProductDetails"] = response["ProductDetails"]["id"]

        if response["Warehouse"] is not None:
            response["Warehouse_name"] = response["Warehouse"]['name']
            response["Warehouse"] = response["Warehouse"]["id"]

        # res = ""
        # count = 0
        # if response["Attributes"]:
        #     for attribute in instance.Attributes.all():
        #         if attribute.name.isdigit():
        #             response[attribute.Attribute.name.lower()] = int(
        #                 attribute.name)
        #             response[attribute.Attribute.name] = int(attribute.id)
        #         else:
        #             response[attribute.Attribute.name.lower()] = attribute.name
        #             response[attribute.Attribute.name] = attribute.id
        #         # if count == 0:
        #         #     res += str(attribute.name)
        #         # else:
        #         #     res += " / " + str(attribute.name)
                    
        #         if attribute.Attribute.name == "Color":
        #             res =  str(attribute.name) + str(res)
        #         else:
        #             res = str(res) + " / " + str(attribute.name)
        #         count += 1
        # response["Attribute_details"] = res
        res = ""
        count = 0
        if response["Attributes"]:
            for attribute in instance.Attributes.all():
                if attribute.name.isdigit():
                    response[attribute.Attribute.name.lower()] = int(
                        attribute.name)
                    response[attribute.Attribute.name] = int(attribute.id)
                else:
                    response[attribute.Attribute.name.lower()] = attribute.name
                    response[attribute.Attribute.name] = attribute.id
                if count == 0:
                    res += str(attribute.name)
                else:
                    res += " / " + str(attribute.name)
                count += 1
        response["Attribute_details"] = res

        images = response["ProductImage"]
        # if images:
        #     flag = 0
        #     result = []
        #     if instance.Color is not None:
        #         for i in images:
        #             for key, value in i.items():
        #                 if key == "Color":
        #                     if value == instance.Color.id:
        #                         result.append(i)
        #                         response["image"] = result
        #                         flag = 1
        #     if flag == 0:
        #         response["image"] = images
        # else:
        #     response["image"] = ""

        if images:
            flag = 0
            result = []
            if instance.Attributes is not None:
                for i in images:
                    for key, value in i.items():
                        if key == "Color":
                            for attribute in instance.Attributes.all():
                                if value == attribute.id:
                                    result.append(i)
                                    response["image"] = result
                                    flag = 1
            if flag == 0:
                response["image"] = images
        else:
            response["image"] = ""

        return response

class ProductLocationEntrySerilizer(serializers.ModelSerializer):
    ProductLocation = ProductDetailsSerilizer(read_only=True)
    class Meta:
        model = models.ProductLocationEntry
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        product_details = instance.ProductLocation.ProductDetails
        merchandiser = product_details.Merchandiser if product_details else None
        
        if merchandiser:
            response["Merchandiser__name"] = merchandiser.name
        else:
            response["Merchandiser__name"] = None
        
        return response


class ProductDetailsUpdateSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    # data = JSONSerializerField()

    class Meta:
        model = models.ProductLocation
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        res = ""
        count = 0
        if response["Attributes"]:
            for attribute in instance.Attributes.all():
                if attribute.name.isdigit():
                    response[attribute.Attribute.name.lower()] = int(
                        attribute.name)
                    response[attribute.Attribute.name] = int(attribute.id)
                else:
                    response[attribute.Attribute.name.lower()] = attribute.name
                    response[attribute.Attribute.name] = attribute.id
                if count == 0:
                    res += str(attribute.name)
                else:
                    res += " / " + str(attribute.name)
                count += 1
        response["description"] = res

        return response


class ProductSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    Warehouse = hrmSerializer.OfficeSerializer(read_only=True)
    ProductDetails = singleProductSerilizer(read_only=True)
    # Color = AttributeTermSerilizer(read_only=True)
    # Size = AttributeTermSerilizer(read_only=True)
    ProductImage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.ProductLocation
        fields = '__all__'

    def get_ProductImage(self, obj):
        images = models.ProductImage.objects.filter(
            ProductDetails__id=obj.ProductDetails.id)
        return ProductImageSerializer(images, many=True).data

    def to_representation(self, instance):
        response = super().to_representation(instance)

        response["Deatils"] = [response["ProductDetails"]]
        response["is_active"] = response["ProductDetails"]['is_active']
        response["title"] = response["ProductDetails"]['title']
        response["product_code"] = response["ProductDetails"]['product_code']
        response["category"] = response["ProductDetails"]['Category']['name']
        response["parent_category"] = response["ProductDetails"]['parent_category']

        if response["Warehouse"] is not None:
            response["Warehouse_name"] = response["Warehouse"]['name']

        return response


class Transferserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.transfer
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.source:
            source = hrmModel.Office.objects.filter(
                id=instance.source.id)
            source_response = []
            for i in source:
                source_response.append(
                    hrmSerializer.OfficeSerializer(i).data)
            response["Source"] = source_response
        if instance.destance:
            destance = hrmModel.Office.objects.filter(
                id=instance.destance.id)
            destance_response = []
            for i in destance:
                destance_response.append(
                    hrmSerializer.OfficeSerializer(i).data)
            response["Destance"] = destance_response

        return response


class TransferItemserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.transfer_item
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        transfer = models.transfer.objects.filter(
            id=instance.transfer.id)
        transfer_response = []
        for i in transfer:
            transfer_response.append(
                Transferserializers(i).data)
        response["Transfer"] = transfer_response
        product = models.ProductLocation.objects.filter(
            id=instance.product.id)
        product_response = []
        for i in product:
            product_response.append(
                ProductDetailsSerilizer(i).data)
        response["Product"] = product_response
        response["title"] = product_response[0]["title"]
        response["product_code"] = product_response[0]["product_code"]
        response["category"] = product_response[0]["category"]
        response["barcode"] = product_response[0]["barcode"]
        return response


class FloatingTransferItemSerializer(serializers.ModelSerializer):
    transfer_number = serializers.CharField(source='transfer.tansfer_number')
    transfer_reference = serializers.CharField(source='transfer.reference')
    source = serializers.CharField(source='transfer.source.name')
    destance = serializers.CharField(source='transfer.destance.name')
    product_details = serializers.CharField(source='product.ProductDetails.title')
    product_category = serializers.CharField(source='product.ProductDetails.Category.name')
    product_attributes = serializers.SerializerMethodField()
    

    class Meta:
        model = models.transfer_item
        fields = ['id', 'transfer_number', 'transfer_reference', 'source', 'destance', 'product_details', 'product_category', 'product_attributes', 'quantity', 'is_received', 'issue_date']

    def get_product_attributes(self, obj):
        return [attribute.name for attribute in obj.product.Attributes.all()]

class ProductLocationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductLocation
        fields = ['barcode', 'Attribute_details', 'quantity']

class BarcodePrintListSerializers(serializers.ModelSerializer):
    product_location_details = serializers.SerializerMethodField()

    class Meta:
        model = models.BarcodePrintList
        fields = '__all__'

    def get_product_location_details(self, instance):
        product_location = instance.product_locations
        if product_location:
            return ProductLocationDetailSerializer(product_location).data
        return {}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product_location_details'] = self.get_product_location_details(instance)
        return representation

# class BarcodePrintListSerializers(serializers.ModelSerializer):
#     data = JSONSerializerField()

#     class Meta:
#         model = models.BarcodePrintList
#         fields = '__all__'

#     def to_representation(self, instance):
#         response = super().to_representation(instance)
#         if instance.product_location:
#             product_location = models.ProductLocation.objects.filter(
#                 id=instance.product_location.id)
#             product_location_response = []
#             for i in product_location:
#                 product_location_response.append(
#                     ProductDetailsSerilizer(i).data)
#             response["Product_Location"] = product_location_response
#         return response    

# class BarcodePrintListSerializers(serializers.ModelSerializer):
#     product_location = ProductDetailsSerilizer()

#     class Meta:
#         model = models.BarcodePrintList
#         fields = '__all__'

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         product_location_data = representation.pop('product_location')
#         representation.update(product_location_data)
#         return representation
    