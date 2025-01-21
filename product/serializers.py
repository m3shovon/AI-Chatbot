from rest_framework import serializers
from product import models
from django.db.models import Q, F


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
        response['name'] = instance.name
        response['label'] = instance.name
        response["key"] = instance.id   
        response["value"] = instance.id
        response["type"] = instance.Attribute.name
        count = models.ProductLocation.objects.filter((Q(Color=instance.id) | Q(Size=instance.id)) & Q(quantity__gt=0) & Q(ProductDetails__is_sellable=True))
        response["quantity"] = len(count)
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

class TagSerilizer(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.Tag
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["title"] = instance.name
        response['name'] = instance.name
        response['label'] = instance.name
        response["key"] = instance.id
        response["value"] = instance.id
        response["type"] = "Collection"
        response["url"] = "/collection/" + instance.slug
        return response


class BrandSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.Brand
        fields = '__all__'
        

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
        # return CategorySingleProductSerilizer(queryset, many=True).data
        # return singleProductSerilizer(queryset, many=True).data
        return CategoryproductforvaluationSerilizer(queryset, many=True).data

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
        total_selling_price = 0
        total_quantity = 0
        if instance.Brand:
            response["brand"] = instance.Brand.name
        else:
            response["brand"] = "ANZARA BANGLADESH LTD."
        for var in variation:
            total_purchase_price = total_purchase_price + \
                (float(var.purchase_price) * float(var.quantity))
            total_selling_price = total_selling_price + \
                (float(var.selling_price) * float(var.quantity))
            total_quantity = total_quantity + float(var.quantity)
        response['total_purchase_price'] = total_purchase_price
        response['total_selling_price'] = total_selling_price
        response['total_quantity'] = total_quantity
        # response['variations'] = variation

        return response


class CategoryproductforvaluationSerilizer(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.ProductDetails
        fields = '__all__'

    def to_representation(self, instance):

        response = super().to_representation(instance)
        variation = models.ProductLocation.objects.filter(
            ProductDetails=instance)
        total_purchase_price = 0
        total_selling_price = 0
        total_quantity = 0
        for var in variation:
            total_purchase_price = total_purchase_price + \
                (float(var.purchase_price) * float(var.quantity))
            total_selling_price = total_selling_price + \
                (float(var.selling_price) * float(var.quantity))
            total_quantity = total_quantity + float(var.quantity)
        response['total_purchase_price'] = total_purchase_price
        response['total_selling_price'] = total_selling_price
        response['total_quantity'] = total_quantity
        if instance.Category:
            response['category_name'] = instance.Category.name
            if instance.Category.Category_parent:
                response['main_category'] = instance.Category.Category_parent.name
        # response['variations'] = variation

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

    # def get_parent(self, obj):
    #     # query what your want here.
    #     # print(obj)
    #     while obj.Category_parent is not None:
    #         obj = obj.Category_parent
    #     return SingleCategorySerilizer(obj).data

    def to_representation(self, instance):

        response = super().to_representation(instance)
        # parent = models.Category.objects.filter(Category_parent=instance.id)
        # parent_response = []
        # for i in parent:
        #     parent_response.append(CategorySerilizer(i).data)
        # response["children"] = parent_response

        response['title'] = instance.name
        response['name'] = instance.name
        response['label'] = instance.name
        response['key'] = instance.id
        response['value'] = instance.id
        response['url'] = "/category/" + instance.slug
        response['immediate_parent'] = SingleCategorySerilizer(
            instance.Category_parent).data
        # response['response'] = response

        return response


class CategoryOnlineSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    data = JSONSerializerField()
    children = serializers.SerializerMethodField(read_only=True)
    

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

    def get_breadcrumbs(self, Category, breadcrumbs): 
        if Category.online_visible:   
            breadcrumbs.insert(0 ,{"id": Category.id, "name": Category.name, "slug" : Category.slug, "url": Category.url})
        if Category.Category_parent:
            self.get_breadcrumbs(Category.Category_parent, breadcrumbs)
        else:
            return {"id": Category.id, "name": Category.name, "slug" : Category.slug, "url": Category.url}

    def to_representation(self, instance):

        response = super().to_representation(instance)
        breadcrumbs = []
        self.get_breadcrumbs(instance, breadcrumbs)
        response["breadcrumbs"] = breadcrumbs
        # parent_response = []
        # for i in parent:
        #     parent_response.append(CategorySerilizer(i).data)
        # response["children"] = parent_response

        response['title'] = instance.name
        response['name'] = instance.name
        response['label'] = instance.name
        response['key'] = instance.id
        response['value'] = instance.id
        response['url'] = "/category/" + instance.slug
        response['immediate_parent'] = SingleCategorySerilizer(
            instance.Category_parent).data
        # print(instance.id)
        # products = models.ProductDetails.objects.filter(Category=instance.id)
        # print(products)

        return response

class CategoryForProductSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    data = JSONSerializerField()
    # children = serializers.SerializerMethodField(read_only=True)
    parent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Category
        fields = '__all__'

    # def get_children(self, obj):
    #     # query what your want here.
    #     # print(obj)
    #     category = models.Category.objects.filter(Category_parent=obj)
    #     if category is not None:
    #         return CategorySerilizer(category, many=True).data
    #     else:
    #         return None

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

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if not instance.thumbnail:
            if instance.photo:
                response["thumbnail"] = instance.photo.url
        return response


class singleProductSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    Category = CategoryForProductSerilizer(read_only=True)

    class Meta:
        model = models.ProductDetails
        fields = '__all__'

    def to_representation(self, instance):

        response = super().to_representation(instance)
        if instance.Brand:
            response["brand"] = instance.Brand.name
        else:
            response["brand"] = "ANZARA BANGLADESH LTD."
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
        variations = models.ProductLocation.objects.filter(
            ProductDetails__id=instance.id)
        variations_response = []
        for variation in variations:
            variations_response.append(ShopProductDetailsSerilizer(variation).data)
        response["variations"] = variations_response
        return response

class SingleCategorySerilizer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = '__all__'

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
        # response['response'] = response

        return response

class ShopProductDetailsSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    # Warehouse = warehouseSerilizer(read_only=True)
    # ProductDetails = singleProductSerilizer(read_only=True)
    # Color = AttributeTermSerilizer(read_only=True)
    # Size = AttributeTermSerilizer(read_only=True)
    ProductImage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.ProductLocation
        # fields = '__all__'
        exclude = ('purchase_price','price','Warehouse','Custom_one','Custom_two','BulkProduct','ref_type',)

    def get_ProductImage(self, obj):
        images = models.ProductImage.objects.filter(
            ProductDetails__id=obj.ProductDetails.id)
        return ProductImageSerializer(images, many=True).data

    def to_representation(self, instance):

        response = super().to_representation(instance)
        
        # response["Deatils"] = [response["ProductDetails"]]
        # response["is_active"] = response["ProductDetails"]['is_active']
        # response["title"] = response["ProductDetails"]['title']
        # response["parent_category"] = response["ProductDetails"]['parent_category']
        # response["ProductDetails"] = response["ProductDetails"]["id"]

        # if response["Warehouse"] is not None:
        #     # Warehouse = models.Warehouse.objects.get(
        #     #     id=instance.Warehouse.id)
        #     # Warehouse_response = []
        #     # Warehouse_response.append(warehouseSerilizer(Warehouse).data)
        #     # response["Warehouse_details"] = Warehouse_response
        #     response["Warehouse_name"] = response["Warehouse"]['name']
        #     response["Warehouse"] = response["Warehouse"]["id"]

        if instance.Color:
            response["color"] = instance.Color.name

        if instance.Size:
            response["size"] = instance.Size.name
        
        # response["selling_price"] = instance.discounted_price
        

        # images

        images = response["ProductImage"]
        if images:
            flag = 0
            result = []
            if instance.Color is not None:
                for i in images:
                    for key, value in i.items():
                        if key == "Color":
                            if value == instance.Color.id:
                                result.append(i)
                                response["image"] = result
                                flag = 1
            if flag == 0:
                response["image"] = images
        else:
            response["image"] = ""

        return response

class ShopfilterSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductDetails
        fields = ('attribute_list', 'max_price', 'min_price')

class ShopitemsSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    # Category = CategoryForProductSerilizer(read_only=True)

    class Meta:
        model = models.ProductDetails
        fields = '__all__'
        
        
    def get_breadcrumbs(self, Category, breadcrumbs): 
        if Category.online_visible:   
            breadcrumbs.insert(0 ,{"id": Category.id, "name": Category.name, "slug" : Category.slug, "url": Category.url})
        if Category.Category_parent:
            self.get_breadcrumbs(Category.Category_parent, breadcrumbs)
        else:
            return {"id": Category.id, "name": Category.name, "slug" : Category.slug, "url": Category.url}

    def to_representation(self, instance):

        response = super().to_representation(instance)
        
        breadcrumbs = []
        self.get_breadcrumbs(instance.Category, breadcrumbs)
        response["breadcrumbs"] = breadcrumbs
        response["main_category"] = instance.Category.name
        # if instance.Category:
        #     # main parent
        #     response["parent_category"] = response["Category"]["parent"]["name"]

        #     if response["Category"]["immediate_parent"]["name"] == "":
        #         # immideiate parent
        #         response["main_category"] = response["Category"]["title"]
        #         response["category_name"] = ""  # own category
        #     else:
        #         response["main_category"] = response["Category"]["immediate_parent"]["name"]
        #         # own category
        #         response["category_name"] = response["Category"]["title"]

        # images
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
        
        # variations
        colors = []
        sizes = []
        variations = models.ProductLocation.objects.filter(
            ProductDetails__id=instance.id)
        variations_response = []
        for variation in variations:
            variations_response.append(ShopProductDetailsSerilizer(variation).data)
        response["variations"] = variations_response
        response["colors"] = colors
        response["sizes"] = sizes
        
        if instance.discount:
            if instance.discount > 0:
                if instance.discount_type == "%":
                    response["discounted_price"] = instance.max_price - (instance.max_price * (instance.discount / 100))
                else:
                    response["discounted_price"] = instance.max_price - instance.discount
        else:
            response["discounted_price"] = 0
   
        
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
        # response['response'] = response

        return response


class ProductDetailsSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    Warehouse = warehouseSerilizer(read_only=True)
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
        # print(response)
        # ProductDetails_response = []
        # response["Deatils"] = ProductDetails_response
        # if response["ProductDetails"] != "":
        #     # ProductDetails = models.ProductDetails.objects.get(
        #     #     id=instance.ProductDetails.id)
        #     # ProductDetails_response.append(
        #     #     singleProductSerilizer(ProductDetails).data)
        #     # # for i in ProductDetails:
        #     # #     ProductDetails_response.append(singleProductSerilizer(i).data)
        #     # # response["title"] = ProductDetails_response[0]['title']
        #     # # response["category"] = ProductDetails_response[0]['category'][0]['name']
        #     # # response["parent_category"] = ProductDetails_response[0]['parent_category']["name"]
        #     # response["Deatils"] = ProductDetails_response
        #     # response["is_active"] = ProductDetails_response[0]['is_active']
        #     # response["title"] = ProductDetails_response[0]['title']
        #     # response["category"] = ProductDetails_response[0]['category']['name']
        #     # response["parent_category"] = ProductDetails_response[0]['parent_category']
        response["Deatils"] = [response["ProductDetails"]]
        response["is_active"] = response["ProductDetails"]['is_active']
        response["title"] = response["ProductDetails"]['title']
        response["category"] = response["ProductDetails"]['Category']['name']
        response["parent_category"] = response["ProductDetails"]['parent_category']
        # response["ProductDetails"] = response["ProductDetails"]["id"]

        if response["Warehouse"] is not None:
            # Warehouse = models.Warehouse.objects.get(
            #     id=instance.Warehouse.id)
            # Warehouse_response = []
            # Warehouse_response.append(warehouseSerilizer(Warehouse).data)
            # response["Warehouse_details"] = Warehouse_response
            response["Warehouse_name"] = response["Warehouse"]['name']
            response["Warehouse"] = response["Warehouse"]["id"]

        if response["Color"] is not None:
            # Color = models.AttributeTerm.objects.get(id=instance.Color.id)
            # Color_response = []
            # Color_response.append(AttributeTermSerilizer(Color).data)

            response["color"] = response["Color"]['name']
            response["Color"] = response["Color"]["id"]

        if response["Size"] is not None:
            # Size = models.AttributeTerm.objects.get(id=instance.Size.id)
            # Size_response = []
            # Size_response.append(AttributeTermSerilizer(Size).data)
            response["size"] = response["Size"]['name']
            response["Size"] = response["Size"]["id"]

        # images

        images = response["ProductImage"]
        if images:
            flag = 0
            result = []
            if instance.Color is not None:
                for i in images:
                    for key, value in i.items():
                        if key == "Color":
                            if value == instance.Color.id:
                                result.append(i)
                                response["image"] = result
                                flag = 1
            if flag == 0:
                response["image"] = images
        else:
            response["image"] = ""

        return response



    
class LowProductDetailsSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    Warehouse = warehouseSerilizer(read_only=True)
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
        response["category"] = response["ProductDetails"]['Category']['name']
        response["parent_category"] = response["ProductDetails"]['parent_category']

        if response["Warehouse"] is not None:

            response["Warehouse_name"] = response["Warehouse"]['name']
            response["Warehouse"] = response["Warehouse"]["id"]

        if response["Color"] is not None:

            response["color"] = response["Color"]['name']
            response["Color"] = response["Color"]["id"]

        if response["Size"] is not None:

            response["size"] = response["Size"]['name']
            response["Size"] = response["Size"]["id"]

        # images

        images = response["ProductImage"]
        if images:
            flag = 0
            result = []
            if instance.Color is not None:
                for i in images:
                    for key, value in i.items():
                        if key == "Color":
                            if value == instance.Color.id:
                                result.append(i)
                                response["image"] = result
                                flag = 1
            if flag == 0:
                response["image"] = images
        else:
            response["image"] = ""

        if response["ProductDetails"]['stock_alart_amount'] <= response["quantity"]:
            return response


class ProductDetailsUpdateSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    data = JSONSerializerField()

    class Meta:
        model = models.ProductLocation
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["title"] = instance.ProductDetails.title
        response["stock_alart_amount"] = instance.ProductDetails.stock_alart_amount
        if instance.ProductDetails.Category:
            if instance.ProductDetails.Category.Category_parent:
                response["main_category"] = instance.ProductDetails.Category.Category_parent.name
                response["category_name"] = instance.ProductDetails.Category.name
            else:
                response["main_category"] = instance.ProductDetails.Category.name
                response["category_name"] = ""
        if instance.Color:
            response["Color"] = instance.Color.name
        if instance.Size: 
            response["Size"] = instance.Size.name
        if instance.Warehouse: 
            response["Location"] = instance.Warehouse.name
        
        return response


class ProductSerilizer(serializers.ModelSerializer):
    # your_conditional_field = serializers.SerializerMethodField()
    Warehouse = warehouseSerilizer(read_only=True)
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
        response["category"] = response["ProductDetails"]['Category']['name']
        response["parent_category"] = response["ProductDetails"]['parent_category']

        if response["Warehouse"] is not None:
            response["Warehouse_name"] = response["Warehouse"]['name']

        if response["Color"] is not None:
            response["color"] = response["Color"]['name']

        if response["Size"] is not None:
            response["size"] = response["Size"]['name']

        return response


class Transferserializers(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.transfer
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.source:
            source = models.Warehouse.objects.filter(
                id=instance.source.id)
            source_response = []
            for i in source:
                source_response.append(
                    warehouseSerilizer(i).data)
            response["Source"] = source_response
        if instance.destance:
            destance = models.Warehouse.objects.filter(
                id=instance.destance.id)
            destance_response = []
            for i in destance:
                destance_response.append(
                    warehouseSerilizer(i).data)
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
        response["category"] = product_response[0]["category"]
        response["barcode"] = product_response[0]["barcode"]
        return response
