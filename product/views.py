from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django.db.models import Q, F
from django.shortcuts import render, get_object_or_404
from product import serializers, models, permissions
from contact import models as contactModel
from contact import serializers as contactSerializer
from hrm import models as hrmModels
from django.utils.text import slugify
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Sum
from decimal import Decimal
from rest_framework.filters import SearchFilter

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000


class AttributeView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.AttributeSerilizer
    queryset = models.Attribute.objects.all().order_by('-id')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'slug',)


class AttributeTermView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.AttributeTermSerilizer
    queryset = models.AttributeTerm.objects.all().order_by('-id')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'slug',)


class CategoryView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.CategorySerilizer
    queryset = models.Category.objects.all().filter(
        Category_parent__isnull=True).order_by('id')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'id')


class CategoryProductView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # serializer_class = serializers.CategoryProductSerilizer
    serializer_class = serializers.AllCategoryProductSerilizer
    queryset = models.Category.objects.filter(
        Category_parent__isnull=True).order_by('id')


class CategoryUpdateView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.CategoryUpdateSerilizer
    queryset = models.Category.objects.all().order_by('id')


class treewarehouseView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.warehouseListSerilizer
    queryset = models.Warehouse.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('is_outlet', 'is_office',)

    # def get_queryset(self):
    #     queryset = self.queryset
    #     # print(self.request.user.branch)
    #     query_set = queryset.filter(id=self.request.user.branch.id)
    #     return query_set


class warehouseView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.warehouseSerilizer
    queryset = models.Warehouse.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('is_outlet', 'is_office',)


class SingleproductFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    parentCategory = django_filters.NumberFilter(method='filter_by_parent')

    class Meta:
        model = models.ProductDetails
        fields = ['title', 'Category__name',
                  'Merchandiser__name', 'keyward', 'is_active', 'product_code', 'parentCategory']

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(Category__name__icontains=value) | Q(product_code__icontains=value))

    def filter_by_parent(self, queryset, name, value):
        category = models.Category.objects.filter(id=value)
        category_list = list((category).values_list('id', flat=True))
        product_list = []
        for obj in category_list:
            products = models.ProductDetails.objects.filter(Category__id=obj)
            products_listD = list((products).values_list('id', flat=True))
            product_list.extend(products_listD)
            childs = models.Category.objects.filter(Category_parent__id=obj)
            child_list = list((childs).values_list('id', flat=True))
            category_list.extend(child_list)
        return queryset.filter(id__in=product_list)

class ProductLocationEntryFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    start = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="created", lookup_expr='lte')
    
    class Meta:
        model = models.ProductLocationEntry
        fields = ['created','start','end','ProductLocation__Warehouse__id','ProductLocation__ProductDetails__Merchandiser__id','ProductLocation__ProductDetails__Category__id',
         'ProductLocation__ProductDetails__title']
        
    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(ProductLocation__ProductDetails__title__contains=value))
    
class ProductLocationEntryView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.ProductLocationEntrySerilizer
    # queryset = models.ProductLocationEntry.objects.all().order_by('-id')
    queryset = models.ProductLocationEntry.objects.select_related(
        'ProductLocation__Warehouse',
        'ProductLocation__ProductDetails__Merchandiser',
        'ProductLocation__ProductDetails__Category'
    ).all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductLocationEntryFilter
    pagination_class = StandardResultsSetPagination
    
    
class Productwithalldetails(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.ProductwithalldetailsSerilizer
    queryset = models.ProductDetails.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = SingleproductFilter
    pagination_class = StandardResultsSetPagination
    
    
class SingleProductView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.singleProductSerilizer
    queryset = models.ProductDetails.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = SingleproductFilter
    pagination_class = StandardResultsSetPagination

    def get_serializer_context(self):
        context = super(SingleProductView, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        # print("Creating")
        Category_id = request.data.get("Category")
        Category = get_object_or_404(models.Category, id=Category_id)
        Sub_Category = None
        Merchandiser = None
        if request.data.get("Sub_Category"):
            Sub_Category_id = request.data.get("Sub_Category")
            Sub_Category = get_object_or_404(
                models.Category, id=Sub_Category_id)
        if request.data.get("Merchandiser"):
            Merchandiser_id = request.data.get("Merchandiser")
            Merchandiser = get_object_or_404(
                contactModel.contact, id=Merchandiser_id)
        title = request.data.get("title")
        slug = slugify(title)
        ProductDetails, _ = models.ProductDetails.objects.get_or_create(
            title=title, Category=Category)
        serialized = serializers.singleProductSerilizer(
            instance=ProductDetails, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(Category=Category,
                        Sub_Category=Sub_Category, Merchandiser=Merchandiser)
        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        # print("Updating")
        Category_id = request.data.get("Category")
        Category = get_object_or_404(models.Category, id=Category_id)
        Sub_Category = None
        Merchandiser = None
        if request.data.get("Sub_Category"):
            Sub_Category_id = request.data.get("Sub_Category")
            Sub_Category = get_object_or_404(
                models.Category, id=Sub_Category_id)
        if request.data.get("Merchandiser"):
            Merchandiser_id = request.data.get("Merchandiser")
            Merchandiser = get_object_or_404(
                contactModel.contact, id=Merchandiser_id)
        title = request.data.get("title")
        slug = slugify(title)

        ProductDetails = models.ProductDetails.objects.filter(id=pk).first()
        serialized = serializers.singleProductSerilizer(
            instance=ProductDetails, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(Category=Category,
                        Sub_Category=Sub_Category, Merchandiser=Merchandiser)
        return Response(serialized.data, status=status.HTTP_200_OK)


class ProductdetailsFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    is_outlet = django_filters.CharFilter(
        method='filter_by_is_outlet', lookup_expr='icontains')
    quantity = django_filters.NumberFilter(
        field_name="quantity", lookup_expr='gt')
    is_active = django_filters.BooleanFilter(
        method='filter_by_is_active', lookup_expr='icontains')
    low_stock = django_filters.BooleanFilter(
        method='filter_by_low_stock', lookup_expr='icontains')
    parentCategory = django_filters.NumberFilter(method='filter_by_parent')
    Attributes = django_filters.CharFilter(
        method='filter_by_attributes', lookup_expr='icontains')

    class Meta:
        model = models.ProductLocation
        fields = ['barcode', 'ProductDetails__product_code',
                  'ProductDetails__title', 'keyward', 'Warehouse', 'is_outlet',
                  'quantity', 'is_active', 'low_stock', 'parentCategory', 'Attributes']

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(barcode__contains=value) | Q(ProductDetails__product_code__contains=value) | Q(ProductDetails__title__contains=value))

    def filter_by_is_outlet(self, queryset, name, value):
        return queryset.filter(Q(Warehouse__is_outlet=value))

    def filter_by_is_active(self, queryset, name, value):
        return queryset.filter(Q(ProductDetails__is_active=value))

    def filter_by_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(quantity__lte=stock_alart_amount)
        else:
            return queryset.filter(Q(ProductDetails__is_active=value))

    def filter_by_parent(self, queryset, name, value):
        category = models.Category.objects.filter(id=value)
        category_list = list((category).values_list('id', flat=True))
        product_list = []
        for obj in category_list:
            products = models.ProductLocation.objects.filter(
                ProductDetails__Category__id=obj)
            products_listD = list((products).values_list('id', flat=True))
            product_list.extend(products_listD)
            childs = models.Category.objects.filter(Category_parent__id=obj)
            child_list = list((childs).values_list('id', flat=True))
            category_list.extend(child_list)
        return queryset.filter(id__in=product_list)
    
    def filter_by_attributes(self, queryset, name, value):
        attribute_terms = models.AttributeTerm.objects.filter(id=value)
        return queryset.filter(Attributes__in=attribute_terms)


class ProductdetailsView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.ProductDetailsSerilizer
    queryset = models.ProductLocation.objects.all().order_by( "-ProductDetails__id", )

    # # If attribute based on Only Size
    # queryset = models.ProductLocation.objects.all().order_by( "-ProductDetails__id","Attributes__id", )
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductdetailsFilter
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        ProductDetails_id = request.data.get("ProductDetails")
        ProductDetails = get_object_or_404(
            models.ProductDetails, id=ProductDetails_id)
        # Size_id = request.data.get("Size")
        # Size = get_object_or_404(models.AttributeTerm, id=Size_id)
        # Color_id = request.data.get("Color")
        # Color = get_object_or_404(models.AttributeTerm, id=Color_id)
        # AttributeTerm_id = request.data.get("AttributeTerm")
        # AttributeTerm = get_object_or_404(models.AttributeTerm, id=AttributeTerm_id)
        # Attribute_id = request.data.get("Attribute")
        # Attribute = get_object_or_404(models.Attribute, id=Attribute_id)
        Warehouse_id = request.data.get("Warehouse")
        Warehouse = get_object_or_404(hrmModels.Office, id=Warehouse_id)
        product_location, created = models.ProductLocation.objects.get_or_create(ProductDetails=ProductDetails,
                                                                                 Warehouse=Warehouse)
        serialized = serializers.ProductDetailsSerilizer(
            instance=product_location, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(Size=Size, Color=Color,
                        Warehouse=Warehouse)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())
        
        response.data['total_purchase_price'] = queryset.annotate(total_purchase_price=F('purchase_price') * F('quantity')).aggregate(Sum('total_purchase_price'))['total_purchase_price__sum']
        
        response.data['total_selling_price'] = queryset.annotate(total_selling_price=F('selling_price') * F('quantity')).aggregate(Sum('total_selling_price'))['total_selling_price__sum']
        
        response.data['total_quantity'] = queryset.aggregate(Sum('quantity'))[
            'quantity__sum']
        
        response.data['current_purchase_price'] = sum(
            Decimal(data.get('purchase_price', 0)) * Decimal(data.get('quantity', 0))
            for data in response.data['results']
        )
        response.data['current_selling_price'] = sum(
            Decimal(data.get('selling_price', 0)) * Decimal(data.get('quantity', 0))
            for data in response.data['results']
        )
        response.data['current_quantity'] = sum(
            [Decimal(data.get('quantity', 0)) for data in response.data['results']])

        return response


class ProductdetailsUpdateCustomView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.ProductDetailsUpdateSerilizer
    queryset = models.ProductLocation.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductdetailsFilter
    pagination_class = StandardResultsSetPagination
    


class ProductdetailsUpdateView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.ProductDetailsUpdateSerilizer
    queryset = models.ProductLocation.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductdetailsFilter
    pagination_class = StandardResultsSetPagination

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # def create(self, request, *args, **kwargs):
    #     ProductDetails_id = request.data.get("ProductDetails")
    #     Warehouse_id = request.data.get("Warehouse")
    #     Attributes = request.data.get("Attribute")
    #     Attributes_list = []
    #     if Attributes != "" or Attributes != None:
    #         # print(type(Attributes))
    #         if isinstance(Attributes, list):
    #             Attributes_list = Attributes
    #         elif isinstance(Attributes, str):
    #             # print("String")
    #             # Attributes_list = list([int(i) for i in Attributes.split(',')])
    #             Attributes_list = list(map(int, Attributes.split(",")))
    #     # print("+++++++++++++++++++")
    #     # print(Attributes_list)
    #     productlocations = models.ProductLocation.objects.filter(Warehouse=Warehouse_id, ProductDetails=ProductDetails_id, Attributes__in=Attributes_list).distinct()
    #     # print(productlocations)
    #     for variation in productlocations:
    #         # print("--------------------------------------------------------")
    #         variationlist = [attribute.id for attribute in variation.Attributes.all()]
    #         # print(variationlist)
    #         if Attributes_list == variationlist:
    #             variation.quantity = int(variation.quantity) + int(request.data.get("quantity"))
    #             # print(variation.quantity)
    #             try:
    #                 print("Update")
    #                 models.ProductLocationEntry.objects.create(ProductLocation=variation, quantity=int(request.data.get("quantity")), remarks="update")
    #                 variation.save()
    #             except Exception:
    #                 print(Exception)
    #             return Response({"message": "Transferd Successfully"})

    #     # print("--------------------------------------------------------")
    #     ProductDetails_id = request.data.get("ProductDetails")
    #     ProductDetails = get_object_or_404(
    #         models.ProductDetails, id=ProductDetails_id)

    #     serialized = serializers.ProductDetailsUpdateSerilizer(
    #         data=request.data)
    #     serialized.is_valid(raise_exception=True)
    #     self.perform_create(serialized)
    #     headers = self.get_success_headers(serialized.data)
    #     Attributes = request.data.get("Attribute")
    #     location_object = get_object_or_404(
    #         models.ProductLocation, id=serialized.data["id"])
    #     if Attributes != "" or Attributes != None:
    #         # print(type(Attributes))
    #         Attributes_list = []
    #         if isinstance(Attributes, list):
    #             Attributes_list = Attributes
    #         elif isinstance(Attributes, str):
    #             Attributes_list = Attributes.split(",")
    #         for attribute in Attributes_list:
    #             location_object.Attributes.add(attribute)
    #     print("create")
    #     models.ProductLocationEntry.objects.create(ProductLocation=location_object, quantity=int(request.data.get("quantity")),remarks="create")
    #     location_object.save()
    #     return Response(
    #         serialized.data, status=status.HTTP_201_CREATED, headers=headers
    #     )

    
    #     # product_location, created = models.ProductLocation.objects.get_or_create(ProductDetails=ProductDetails,
    #     #                                                                          Warehouse=Warehouse,Attributes=Attributes_list)
    #     # serialized = serializers.ProductDetailsSerilizer(
    #     #     instance=product_location, data=request.data)
    #     # serialized.is_valid(raise_exception=True)
    #     # serialized.save()
        
    #     # return Response(serialized.data, status=status.HTTP_201_CREATED)
    
    ############# OLDER Version ####################
    def create(self, request, *args, **kwargs):
        ProductDetails_id = request.data.get("ProductDetails")
        ProductDetails = get_object_or_404(
            models.ProductDetails, id=ProductDetails_id)

        serialized = serializers.ProductDetailsUpdateSerilizer(
            data=request.data)
        serialized.is_valid(raise_exception=True)
        self.perform_create(serialized)
        headers = self.get_success_headers(serialized.data)
        Attributes = request.data.get("Attribute")
        location_object = get_object_or_404(
            models.ProductLocation, id=serialized.data["id"])
        if Attributes != "" or Attributes != None:
            # print(type(Attributes))
            Attributes_list = []
            if isinstance(Attributes, list):
                Attributes_list = Attributes
            elif isinstance(Attributes, str):
                Attributes_list = Attributes.split(",")
            print("==============",Attributes_list,"=================")
            for attribute in Attributes_list:
                location_object.Attributes.add(attribute)
        models.ProductLocationEntry.objects.create(ProductLocation=location_object, quantity=int(request.data.get("quantity")))
        location_object.save()
        return Response(
            serialized.data, status=status.HTTP_201_CREATED, headers=headers
        )    
   

    def update(self, request, pk=None, *args, **kwargs):
        # print("Updating")
        # print(self)
        ProductDetails = None
        Warehouse = None
        Attributes = None

        ProductLocation = models.ProductLocation.objects.filter(id=pk).first()

        if request.data.get("ProductDetails"):
            ProductDetails_id = request.data.get("ProductDetails")
            ProductDetails = get_object_or_404(
                models.ProductDetails, id=ProductDetails_id)
        else:
            ProductDetails = get_object_or_404(
                models.ProductDetails, id=ProductLocation.ProductDetails.id)

        if request.data.get("Warehouse"):
            Warehouse_id = request.data.get("Warehouse")
            Warehouse = get_object_or_404(
                hrmModels.Office, id=Warehouse_id)
        else:
            Warehouse = get_object_or_404(
                hrmModels.Office, id=ProductLocation.Warehouse.id)
            request.data._mutable = True
            request.data['Warehouse'] = str(ProductLocation.Warehouse.id)

        previous_attribute = []
        for attribute in ProductLocation.Attributes.all():
            previous_attribute.append(attribute.id)

        serialized = serializers.ProductDetailsUpdateSerilizer(
            instance=ProductLocation, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(ProductDetails=ProductDetails,
                        Warehouse=Warehouse, Attributes=previous_attribute)
        # serialized.save()

        if request.data.get("Attribute"):
            new = set(request.data.get("Attribute"))
            old = set(previous_attribute)
            add = new.difference(old)
            remove = old.difference(new)
            if new != old:
                for attribute in add:
                    ProductLocation.Attributes.add(attribute)
                for attribute in remove:
                    ProductLocation.Attributes.remove(attribute)
        # Update the ProductLocationEntry
        try:
            location_entry = models.ProductLocationEntry.objects.get(ProductLocation=ProductLocation)
            if request.data.get("quantity"):
                location_entry.quantity = int(request.data.get("quantity"))
                location_entry.save()
        except models.ProductLocationEntry.DoesNotExist:
            models.ProductLocationEntry.objects.create(
                ProductLocation=ProductLocation,
                quantity=int(request.data.get("quantity"))
            )
        ProductLocation.save()

        return Response(serialized.data, status=status.HTTP_200_OK)


def get_serializer_context(self):
    context = super(ProductdetailsView, self).get_serializer_context()
    context.update({"request": self.request})
    return context


class ProductView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.ProductSerilizer
    queryset = models.ProductLocation.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductdetailsFilter
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        title = request.data.get("title")
        Category_id = request.data.get("Category")
        Category = get_object_or_404(models.Category, id=Category_id)
        # Size_id = request.data.get("Size")
        # Size = get_object_or_404(models.AttributeTerm, id=Size_id)
        # Color_id = request.data.get("Color")
        # Color = get_object_or_404(models.AttributeTerm, id=Color_id)
        Warehouse_id = request.data.get("Warehouse")
        Warehouse = get_object_or_404(hrmModels.Office, id=Warehouse_id)
        Sub_Category = None
        Merchandiser = None
        if request.data.get("Sub_Category"):
            Sub_Category_id = request.data.get("Sub_Category")
            Sub_Category = get_object_or_404(
                models.Category, id=Sub_Category_id)
        if request.data.get("Merchandiser"):
            Merchandiser_id = request.data.get("Merchandiser")
            Merchandiser = get_object_or_404(
                contactModel.contact, id=Merchandiser_id)

        product_details, created = models.ProductDetails.objects.get_or_create(
            title=title, Category=Category)
        serialized = serializers.singleProductSerilizer(
            instance=product_details, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(Category=Category,
                        Sub_Category=Sub_Category, Merchandiser=Merchandiser)

        product_location, created = models.ProductLocation.objects.get_or_create(ProductDetails=product_details,
                                                                                 Warehouse=Warehouse)
        serialized = serializers.ProductSerilizer(
            instance=product_location, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(Category=Category, Size=Size, Color=Color,
                        Warehouse=Warehouse)
        return Response(serialized.data, status=status.HTTP_201_CREATED)


# class ProductcvariationView(viewsets.ModelViewSet):
#     """Handel creating and updating Attribute"""
#     authentication_classes = (TokenAuthentication,)
#     # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
#     serializer_class = serializers.variationProductSerilizer
#     queryset = models.ProductVariation.objects.all().order_by('-id')
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('title',)


class VariationVIew(APIView):
    "get variation of a specific product"

    def get(self, request, pk):
        "return data"
        # # If attribute based on Only Size
        # queryset = models.ProductLocation.objects.filter(
        #     ProductDetails__id=pk).order_by('Attributes__id')
        
        # If attribute based on multiple terms
        queryset = models.ProductLocation.objects.filter(
            ProductDetails__id=pk).order_by('-id')
        
        result = serializers.ProductDetailsSerilizer(
            queryset, many=True, context={'request': self.request, 'view': self})
        return Response(result.data)


class ProductImageView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.ProductImageSerializer
    queryset = models.ProductImage.objects.all().order_by('-id')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('ProductDetails', 'ProductLocation', 'Color')


class TransferViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Transferserializers
    queryset = models.transfer.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('status',)
#     permission_classes = (permissions.UpdateOwnProfile,)

class TransferPViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Transferserializers
    queryset = models.transfer.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('status',)
    pagination_class = StandardResultsSetPagination
    
class TransferItemViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.TransferItemserializers
    queryset = models.transfer_item.objects.all().order_by('-product__ProductDetails',)
    # # If attribute based on Only Size
    # queryset = models.transfer_item.objects.all().order_by('-product__ProductDetails','product__Attributes')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('transfer__id', 'is_received', 'product__id')
#     permission_classes = (permissions.UpdateOwnProfile,)

class FloatingTransferItemViewFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    class Meta:
        model = models.transfer_item
        fields = ['transfer__tansfer_number','product__ProductDetails__title']
    
    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(transfer__tansfer_number__contains=value) | Q(product__ProductDetails__title__contains=value))


class FloatingTransferItemView(viewsets.ModelViewSet):
    serializer_class = serializers.FloatingTransferItemSerializer
    queryset = models.transfer_item.objects.filter(is_received=False,is_returned=False).order_by('-issue_date')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filter_class = FloatingTransferItemViewFilter
    filterset_fields = ['transfer__tansfer_number', 'product__ProductDetails__Category__name']
    search_fields = ['product__ProductDetails__title', 'transfer__tansfer_number']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return super().get_queryset().select_related('transfer', 'product', 'product__ProductDetails', 'product__ProductDetails__Category').prefetch_related('product__Attributes')
    
    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.FloatingTransferItemSerializer
        response = super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())

        response.data['total_quantity'] = queryset.aggregate(Sum('quantity'))[
            'quantity__sum']
        
        return response


class BarcodePrintListViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.BarcodePrintListSerializers
    queryset = models.BarcodePrintList.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('product_locations__id', 'challan_number')
#     permission_classes = (permissions.UpdateOwnProfile,)