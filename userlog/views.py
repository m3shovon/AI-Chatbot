from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserLog
from rest_framework import viewsets
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from userlog import serializers, models
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.db import connection
# Create your views here.

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100000000
    


class LogsFilter(django_filters.FilterSet):
    start = django_filters.IsoDateTimeFilter(
        field_name="timestamp", lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(
        field_name="timestamp", lookup_expr='lte')
    keyward = django_filters.CharFilter(
        method='filter_by_keyward', lookup_expr='icontains')
    class Meta:
        model = models.UserLog
        fields = ['start','end','content_type', 'object_id','user','action_type', 'keyward']
        
    def filter_by_keyward(self, queryset, name, value):
        return queryset.filter(Q(action__icontains=value) | Q(action_data__icontains=value) | Q(user__name__icontains=value)  | Q(user__email__icontains=value))
    

class LogsViewSet(viewsets.ModelViewSet):
    """Handel creating and updating users"""
    serializer_class = serializers.LogsSerializer
    queryset = models.UserLog.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = [DjangoFilterBackend]
    filter_class = LogsFilter
    pagination_class = StandardResultsSetPagination


class LogsImportViewSet(viewsets.ModelViewSet):
    """Handel creating and updating Attribute"""
    serializer_class = serializers.LogsSerializer
    queryset = models.UserLog.objects.all().order_by('-id')
    
    def create(self, request, *args, **kwargs):
        # print(request.data["data"])
        with connection.cursor() as cursor:
            for data in request.data["data"][::-1]:
                try:
                    cursor.execute(data["sql"])
                    row = cursor.fetchone()
                except: 
                    print(data["sql"])
            # return row
        return Response({"message": "Successfully updated"})