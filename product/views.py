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
from userlog import models as userlogModel
from order import models as orderModel
from django.utils.text import slugify
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Sum, Max, Min
from decimal import Decimal
from image_optimizer.utils import image_optimizer
from django.contrib.auth import get_user_model
import json



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100000000

class minimumPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
class AttributeView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.AttributeSerilizer
    queryset = models.Attribute.objects.all().order_by('-id')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'slug',)


class TagView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.TagSerilizer
    queryset = models.Tag.objects.all().order_by('-id')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'slug',)


class BrandView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.BrandSerilizer
    queryset = models.Brand.objects.all().order_by('id')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'id',)


class AttributeTermView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.AttributeTermSerilizer
    queryset = models.AttributeTerm.objects.all().order_by('-id')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'slug',)
    
class SingleproductvalutionFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    class Meta:
        model = models.Category
        fields = ['keyward','slug','id']

    def filter_by_keyward(self, queryset, name, value):
        if value != "all":
            return queryset.filter(Q(id=value))
        else:
            return queryset.filter(Q(Category_parent__isnull=True) )

class ShopCategoryView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.CategoryOnlineSerilizer
    queryset = models.Category.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend]
    filter_class = SingleproductvalutionFilter
    

class CategoryView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.CategorySerilizer
    queryset = models.Category.objects.all().filter(
        Category_parent__isnull=True).order_by('id')
    filter_backends = [DjangoFilterBackend]
    filter_class = SingleproductvalutionFilter


class CategoryProductView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # serializer_class = serializers.CategoryProductSerilizer
    serializer_class = serializers.AllCategoryProductSerilizer
    queryset = models.Category.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend]
    filter_class = SingleproductvalutionFilter

# class CategoryProductView(viewsets.ModelViewSet):
#     """Handel creating and updating Attribute"""
#     authentication_classes = (TokenAuthentication,)
#     # serializer_class = serializers.CategoryProductSerilizer
#     serializer_class = serializers.AllCategoryProductSerilizer
#     queryset = models.Category.objects.filter(
#         Category_parent__isnull=True).order_by('id')


class CategoryUpdateView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.CategoryUpdateSerilizer
    queryset = models.Category.objects.all().order_by('id')


class warehouseView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.warehouseSerilizer
    queryset = models.Warehouse.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('is_outlet', 'is_office','id')
    
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        
        if user.is_anonymous:
            return models.Warehouse.objects.all()
        else:
            employee = contactModel.EmployeeProfile.objects.get(employee=user.id)
            # if employee.branch:
            branches = []
            for i in list(employee.branch.all().values('id')):
                branches.append(i["id"])
            # print(branches)
            # return models.Warehouse.objects.filter(pk__in=branches)
            return models.Warehouse.objects.all()


class SingleproductFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    parentCategory = django_filters.NumberFilter(method='filter_by_parent')
    
    attribute = django_filters.CharFilter(method='filter_by_attribute', lookup_expr='contains')
    
    tag = django_filters.CharFilter(method='filter_by_tag', lookup_expr='in')
    
    tagslug = django_filters.CharFilter(method='filter_by_tagslug', lookup_expr='in')
    lowrange = django_filters.NumberFilter(field_name="min_price", lookup_expr='gte')
    heighrange = django_filters.NumberFilter(field_name="max_price", lookup_expr='lte')
    discount = django_filters.NumberFilter(field_name="discount", lookup_expr='gt')
    livestart = django_filters.IsoDateTimeFilter(
        field_name="live_date", lookup_expr='gte')
    liveend = django_filters.IsoDateTimeFilter(
        field_name="live_date", lookup_expr='lte')

    class Meta:
        model = models.ProductDetails
        fields = ['title', 'Category__name',
                  'Merchandiser__name', 'keyward', 'is_active','attribute','tag','tagslug','lowrange',
                  'heighrange','product_code', 'parentCategory','is_sellable','livestart','liveend','discount',]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(title__contains=value) | Q(Category__name__contains=value) | Q(product_code__contains=value))
    
    def filter_by_attribute(self, queryset, name, value):
        array = value.split(',')
        condition = Q(attribute_list__contains=int(array[0]))
        for string in array[1:]:
            condition |= Q(attribute_list__contains=int(string))
        return queryset.filter(condition).distinct()

    def filter_by_tag(self, queryset, name, value):
        array = list(map(int, value.split(',')))
        # print(array)
        return queryset.filter(Tag__in=array).distinct()
    
    def filter_by_tagslug(self, queryset, name, value):
        array = []
        array.append(models.Tag.objects.get(slug=value).id)
        print(array)
        return queryset.filter(Tag__in=array).distinct()

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
        
        if request.data.get("name"):
            check = models.ProductDetails.objects.filter(slug=request.data.get("name"))
            if len(check) > 0:
                request.data['slug'] = slugify(request.data.get("name"))+"-"+slugify(title)
                slug = slugify(request.data.get("name"))+"-"+slugify(title)
            else:
                request.data['slug'] = slugify(request.data.get("name"))
                slug = slugify(request.data.get("name"))
        else:
            request.data['slug'] = slugify(request.data.get("title"))
            slug = slugify(request.data.get("title"))
        
        

        ProductDetails, _ = models.ProductDetails.objects.get_or_create(
            title=title, Category=Category, slug=slug)
        serialized = serializers.singleProductSerilizer(
            instance=ProductDetails, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(Category=Category,
                        Sub_Category=Sub_Category, Merchandiser=Merchandiser)
        # tags insert code
        Tags = request.data.get("Tag")
        ProductDetails_object = get_object_or_404(
            models.ProductDetails, id=serialized.data["id"])
        if Tags is not None:
            # print(Tags)
            # Tags_list = Tags.split(",")
            
            for Tag in Tags:
                ProductDetails_object.Tag.add(Tag)
        ProductDetails_object.save()
        
        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
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
        
        if request.data.get("slug"):
            check = models.ProductDetails.objects.filter(slug=request.data.get("slug"))
            if len(check) > 0:
                if request.data.get("name"):
                    self.slug = slugify(request.data.get("name"))+"-"+slugify(title)
                else:
                    self.slug = slugify(title)
                request.data['slug'] = self.slug
                
            
        
        ProductDetails = models.ProductDetails.objects.filter(id=pk).first()
        serialized = serializers.singleProductSerilizer(
            instance=ProductDetails, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(Category=Category,
                        Sub_Category=Sub_Category, Merchandiser=Merchandiser)

        # tags data update
        previous_tags = []
        for tag in ProductDetails.Tag.all():
            previous_tags.append(tag.id)
        new = set(request.data.get("Tag"))
        old = set(previous_tags)
        add = new.difference(old)
        remove = old.difference(new)
        if new != old:
            for Tag in add:
                ProductDetails.Tag.add(Tag)
            for Tag in remove:
                ProductDetails.Tag.remove(Tag)
        ProductDetails.save()
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
    lowrange = django_filters.NumberFilter(field_name="selling_price", lookup_expr='gte')
    heighrange = django_filters.NumberFilter(field_name="selling_price", lookup_expr='lte')

    class Meta:
        model = models.ProductLocation
        fields = ['barcode', 'ProductDetails__product_code',
                  'ProductDetails__title', 'keyward', 'Warehouse', 'is_outlet',
                  'quantity', 'is_active', 'low_stock', 'parentCategory','Color', 'Size', 'selling_price','lowrange','heighrange']

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


class ProductdetailsView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.ProductDetailsSerilizer
    queryset = models.ProductLocation.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductdetailsFilter
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):

        ProductDetails_id = request.data.get("ProductDetails")
        ProductDetails = get_object_or_404(
            models.ProductDetails, id=ProductDetails_id)
        Size_id = request.data.get("Size")
        Size = get_object_or_404(models.AttributeTerm, id=Size_id)
        Color_id = request.data.get("Color")
        Color = get_object_or_404(models.AttributeTerm, id=Color_id)
        Warehouse_id = request.data.get("Warehouse")
        Warehouse = get_object_or_404(models.Warehouse, id=Warehouse_id)
        product_location, created = models.ProductLocation.objects.get_or_create(ProductDetails=ProductDetails,
                                                                                 Warehouse=Warehouse, Size=Size, Color=Color)
        serialized = serializers.ProductDetailsSerilizer(
            instance=product_location, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(Size=Size, Color=Color,
                        Warehouse=Warehouse)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())

        response.data['total_purchase_price'] = queryset.aggregate(
            Sum('purchase_price'))['purchase_price__sum']
        response.data['total_selling_price'] = queryset.aggregate(Sum('selling_price'))[
            'selling_price__sum']
        response.data['total_quantity'] = queryset.aggregate(Sum('quantity'))[
            'quantity__sum']

        response.data['current_purchase_price'] = sum(
            [Decimal(data.get('purchase_price', 0)) for data in response.data['results']])
        response.data['current_selling_price'] = sum(
            [Decimal(data.get('selling_price', 0)) for data in response.data['results']])
        response.data['current_quantity'] = sum(
            [Decimal(data.get('quantity', 0)) for data in response.data['results']])

        return response


class ShopitemsFilter(django_filters.FilterSet):
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')

    parentCategory = django_filters.CharFilter(method='filter_by_parent')
    
    attribute = django_filters.CharFilter(method='filter_by_attribute', lookup_expr='contains')
    
    tag = django_filters.CharFilter(method='filter_by_tag', lookup_expr='in')
    
    tagslug = django_filters.CharFilter(method='filter_by_tagslug', lookup_expr='in')
    lowrange = django_filters.NumberFilter(field_name="min_price", lookup_expr='gte')
    heighrange = django_filters.NumberFilter(field_name="max_price", lookup_expr='lte')

    class Meta:
        model = models.ProductDetails
        fields = ['title', 'Category__name','slug',
                  'Merchandiser__name', 'keyward', 'is_active', 'product_code', 'parentCategory',
                    'attribute','tag', 'tagslug','lowrange','heighrange',
                  ]

    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(slug__icontains=value) | Q(name__icontains=value) | Q(title__icontains=value) | Q(Category__name__icontains=value)  | Q(product_code__icontains=value))
    
    def filter_by_attribute(self, queryset, name, value):
        array = value.split(',')
        condition = Q(attribute_list__contains=int(array[0]))
        for string in array[1:]:
            condition |= Q(attribute_list__contains=int(string))
        return queryset.filter(condition).distinct()

    def filter_by_tag(self, queryset, name, value):
        array = list(map(int, value.split(',')))
        # print(array)
        return queryset.filter(Tag__in=array).distinct()
    
    def filter_by_tagslug(self, queryset, name, value):
        array = []
        array.append(models.Tag.objects.get(slug=value).id)
        print(array)
        return queryset.filter(Tag__in=array).distinct()
    
    
    def filter_by_parent(self, queryset, name, value):
        category = models.Category.objects.filter(slug=value)
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

class ShopitemsView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.ShopitemsSerilizer
    queryset = models.ProductDetails.objects.filter(is_sellable=True).order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = ShopitemsFilter
    pagination_class = minimumPagination
    
    # def list(self, request, *args, **kwargs):
    #     self.serializer_class = serializers.ShopitemsSerilizer
    #     response = super().list(request, *args, **kwargs)
    #     queryset = self.filter_queryset(self.get_queryset())
    #     response.data['min'] = queryset.aggregate(Min('max_price'))[
    #         'max_price__min']
    #     response.data['max'] = queryset.aggregate(Max('max_price'))[
    #         'max_price__max']
    #     # response.data['attri'] = queryset.StringAgg('attribute_list', delimiter=', ', distinct=True)
        
        
    #     return response

class ShopfilterView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.ShopfilterSerilizer
    queryset = models.ProductDetails.objects.filter(is_sellable=True).order_by('-id')
    filter_backends = [DjangoFilterBackend]
    filter_class = ShopitemsFilter
    # pagination_class = minimumPagination
    
    def list(self, request, *args, **kwargs):
        self.serializer_class = serializers.ShopfilterSerilizer
        response = super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())
        # print(queryset.aggregate(Min('max_price'))['max_price__min'])
        # print(queryset.aggregate(Max('max_price'))['max_price__max'])
        attributeset = []
        for data in response.data:
            attributeset = (list(set(attributeset) | set(data["attribute_list"])))
        # print(attributeset)
        result = {
            "attributeset": attributeset,
            "min": queryset.aggregate(Min('max_price'))['max_price__min'],
            "max": queryset.aggregate(Max('max_price'))['max_price__max']
        }
        return Response({"result": result, "status": status.HTTP_200_OK})


class LowProductdetailsView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.Profilepermission,IsAuthenticatedOrReadOnly)
    serializer_class = serializers.LowProductDetailsSerilizer
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


def get_serializer_context(self):
    context = super(ProductdetailsView, self).get_serializer_context()
    context.update({"request": self.request})
    return context


class BulkProductView(viewsets.ModelViewSet):
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

        # Size_name = request.data.get("Size")
        # Type = get_object_or_404(models.Attribute, name="Size")
        # Size, created = models.AttributeTerm.objects.get_or_create(
        #     name=Size_name, Attribute=Type)
        # Size = get_object_or_404(models.AttributeTerm, id=request.data.get("Size"))
        # Color_name = request.data.get("Color")
        # Type = get_object_or_404(models.Attribute, name="Color")
        # Color, created = models.AttributeTerm.objects.get_or_create(
        #     name=Color_name, Attribute=Type)
        Color = get_object_or_404(models.AttributeTerm, id=request.data.get("Color"))

        Warehouse_id = request.data.get("Warehouse")
        Warehouse = get_object_or_404(models.Warehouse, id=Warehouse_id)
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

        # print(product_details)
        product_location, created = models.ProductLocation.objects.get_or_create(ProductDetails=product_details,
                                                                                 Warehouse=Warehouse, 
                                                                                #  Size=Size, 
                                                                                 Color=Color)
        serialized = serializers.ProductSerilizer(
            instance=product_location, data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save(Category=Category, 
                        # Size=Size, 
                        Color=Color,
                        Warehouse=Warehouse)
        return Response(serialized.data, status=status.HTTP_201_CREATED)


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
        Size_id = request.data.get("Size")
        Size = get_object_or_404(models.AttributeTerm, id=Size_id)
        Color_id = request.data.get("Color")
        Color = get_object_or_404(models.AttributeTerm, id=Color_id)
        Warehouse_id = request.data.get("Warehouse")
        Warehouse = get_object_or_404(models.Warehouse, id=Warehouse_id)
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

        # print(product_details)
        product_location, created = models.ProductLocation.objects.get_or_create(ProductDetails=product_details,
                                                                                 Warehouse=Warehouse, Size=Size, Color=Color)
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
        queryset = models.ProductLocation.objects.filter(
            ProductDetails__id=pk).order_by('-id')
        result = serializers.ProductDetailsSerilizer(
            queryset, many=True, context={'request': self.request, 'view': self})
        return Response(result.data)


class VariationAllVIew(APIView):
    "get variation of a specific product"

    def get(self, request):
        "return data"
        queryset = models.ProductLocation.objects.all().order_by('-id')
        result = serializers.ProductDetailsUpdateSerilizer(
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
    
    
    def create(self, request, *args, **kwargs):
        
        # ProductLocation_id = request.data.get("ProductLocation")
        ProductDetails_id = request.data.get("ProductDetails")
        Color_id = request.data.get("Color")
        is_active = request.data.get("is_active")
        photo = request.data.get("photo")
        thumbnail = request.data.get("thumbnail")
        
        ProductDetails = get_object_or_404(models.ProductDetails, id=ProductDetails_id)
        # ProductLocation = get_object_or_404(models.ProductLocation, id=ProductLocation_id)
        Color = ""
        if Color_id:
            Color = get_object_or_404(models.AttributeTerm, id=Color_id)
        
        image_data = image_optimizer(image_data=thumbnail,
                                 output_size=(600, 900),
                                 resize_method='thumbnail')
    
        ProductImage = models.ProductImage.objects.create(ProductDetails=ProductDetails, photo=photo,thumbnail=image_data)
        if Color != "":
            ProductImage.Color = Color
            ProductImage.save()
        # serialized = serializers.ProductImageSerializer(instance=ProductImage, data=request.data)
        # serialized.is_valid(raise_exception=True)
        
        # serialized.save()
        return Response({"message": "Successfully updated", "status": status.HTTP_201_CREATED})
        


class TransferViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoices"""
    serializer_class = serializers.Transferserializers
    queryset = models.transfer.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('status',)
#     permission_classes = (permissions.UpdateOwnProfile,)

class TransferPViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    serializer_class = serializers.Transferserializers
    queryset = models.transfer.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('status',)
    pagination_class = StandardResultsSetPagination


class TransferItemViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Invoice Items"""
    serializer_class = serializers.TransferItemserializers
    queryset = models.transfer_item.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('transfer__id', 'is_received')
#     permission_classes = (permissions.UpdateOwnProfile,)


class CustomQueryView(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    serializer_class = serializers.ProductSerilizer
    queryset = models.ProductDetails.objects.all().order_by('-id')
    
    
    def list(self, request, *args, **kwargs):
        message = []
        products = models.ProductDetails.objects.all()
        for product in products:
            userlogs = userlogModel.UserLog.objects.filter(content_type=20, object_id=product.id)
            initial = 0
            added = 0
            removed = 0
            current = 0
            sold = 0
            for userlog in userlogs:
                if userlog.action_type == "create":
                    if eval(userlog.action_data).get("quantity") is not None:
                        initial = int(eval(userlog.action_data)["quantity"])
                        current = initial
                else:
                    if eval(userlog.action_data).get("quantity") is not None:
                        # print(userlog.action_type)
                        # print(userlog.action_data)
                        if current > int(eval(userlog.action_data)["quantity"]):
                            temp = current - int(eval(userlog.action_data)["quantity"])
                            removed = removed + temp
                        else:
                            temp = int(eval(userlog.action_data)["quantity"]) - current
                            added = added + temp
            invoicesold = 0
            soldItems = orderModel.invoice_item.objects.filter(product_id=product.id)
            for soldItem in soldItems:
                invoicesold = invoicesold + int(soldItem.quantity)
            rest = current+added-removed
            if (initial-rest) != (initial-invoicesold):
                print("initial: " + str(initial), "current: " + str(rest), "added: " + str(added), "removed: " + str(removed))
                print("Sold Items: " + str(invoicesold))
                print("---------")
        # message.append()
        return Response({"message": message})
    
    
    # check product transfers
    # def list(self, request, *args, **kwargs):
    #     message = []
    #     products = models.ProductDetails.objects.all().order_by('-id')
    #     challan_items = models.transfer_item.objects.filter(transfer=107)
    #     for item in challan_items:
            
    #         # print("--------------------------------------------------------")
    #         # print(item.product.ProductDetails)
    #         if item.product.Color:
    #             variations = models.ProductLocation.objects.filter(ProductDetails = item.product.ProductDetails.id, Color = item.product.Color.id)
    #         else:
    #             variations = models.ProductLocation.objec)ts.filter(ProductDetails = item.product.ProductDetails.id)
    #         for variation in variations:
    #             # print(variation)
    #             if variation.Warehouse.id != 1:
    #                 # print(variation.id)
    #                 userlogs = userlogModel.UserLog.objects.filter(content_type=20, object_id=variation.id)
    #                 # userlogs = userlogModel.UserLog.objects.filter(content_type=20, object_id=6976)
    #                 # print(userlogs)
    #                 if userlogs.count() > 1:
    #                     for index, log in enumerate(userlogs):
    #                         if index == 0:
    #                             prev = userlogs[0].timestamp
    #                         else:
    #                             prev = userlogs[index - 1].timestamp
    #                             difference = userlogs[index].timestamp - prev
    #                             if difference.total_seconds() < 60:
    #                                 message.append({"name": variation.ProductDetails.title, "Color": variation.Color.name,"Location": variation.Warehouse.name,"By":  log.user.name, "Time": log.timestamp, "log": log.action_data})
    #                                 print({"name": variation.ProductDetails.title, "Color": variation.Color.name,"Location": variation.Warehouse.name,"By":  log.user.name, "Time": log.timestamp, "log": log.action_data})
    #     return Response({"message": message})
