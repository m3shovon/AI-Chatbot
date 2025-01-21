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
from django.shortcuts import get_object_or_404

from software_settings import serializers, models

# Create your views here.


class BusinessViewSet(viewsets.ViewSet):
    """
    Example empty viewset demonstrating the standard
    actions that will be handled by a router class.

    If you're using format suffixes, make sure to also include
    the `format=None` keyword argument for each action.
    """
    queryset = models.business_settings.objects.all()
    serializer_class = serializers.BusinesseSettingsSerializer

    def get_permissions(self):
        if self.action in ['update']:
            self.permission_classes = [IsAuthenticatedOrReadOnly, ]
        elif self.action in ['destroy']:
            self.permission_classes = [IsAuthenticatedOrReadOnly, ]
        elif self.action in ['retrieve', 'list']:
            self.permission_classes = [IsAuthenticatedOrReadOnly, ]
        return super().get_permissions()

    def list(self, request):
        queryset = models.business_settings.objects.all()
        serializer_class = serializers.BusinesseSettingsSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer_class.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(models.business_settings, id=pk)
        serializer = serializers.BusinesseSettingsSerializer(
            user, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = get_object_or_404(models.business_settings, id=pk)
        serializer = serializers.BusinesseSettingsSerializer(
            instance=user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def partial_update(self, request, pk=None):
        user = get_object_or_404(models.business_settings, id=pk)
        serializer = serializers.BusinesseSettingsSerializer(
            instance=user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        # pass

    def destroy(self, request, pk=None):
        user = models.business_settings.objects.get(id=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class moduleViewSet(viewsets.ModelViewSet):
    """Handel creating and updating users"""
    serializer_class = serializers.moduleSerializer
    queryset = models.module.objects.all()
    authentication_classes = (TokenAuthentication,)


class sub_moduleViewSet(viewsets.ModelViewSet):
    """Handel creating and updating users"""
    serializer_class = serializers.sub_moduleSerializer
    queryset = models.sub_module.objects.all()
    authentication_classes = (TokenAuthentication,)
