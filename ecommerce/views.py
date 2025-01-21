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
from django.shortcuts import get_object_or_404

from ecommerce import serializers, models

# Create your views here.

class pageFilter(django_filters.FilterSet):
    class Meta:
        model = models.page
        fields = ['is_campaign_page', 'slug']

class pageViewSet(viewsets.ModelViewSet):
    """Handel creating and updating users"""
    serializer_class = serializers.pageSerializer
    queryset = models.page.objects.all()
    authentication_classes = (TokenAuthentication,)
    filter_backends = [DjangoFilterBackend]
    filter_class = pageFilter

class imageViewSet(viewsets.ModelViewSet):
    """Handel creating and updating users"""
    serializer_class = serializers.imageSerializer
    queryset = models.image.objects.all().order_by('-id')
    authentication_classes = (TokenAuthentication,)

class featureViewSet(viewsets.ModelViewSet):
    """Handel creating and updating users"""
    serializer_class = serializers.featureSerializer
    queryset = models.feature.objects.all()
    authentication_classes = (TokenAuthentication,)

class feature_itemViewSet(viewsets.ModelViewSet):
    """Handel creating and updating users"""
    serializer_class = serializers.feature_itemSerializer
    queryset = models.feature_item.objects.all()
    authentication_classes = (TokenAuthentication,)