from rest_framework import serializers
from software_settings import models


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class BusinesseSettingsSerializer(serializers.ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = models.business_settings
        fields = '__all__'

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)

    #     url = None
    #     request = self.context.get('request', None)
    #     if instance.logo.name:
    #         url = request.build_absolute_uri(instance.logo.url)
    #     response["Logo"] = url
    #     url = None
    #     if instance.signature.name:
    #         url = request.build_absolute_uri(instance.signature.url)
    #     response["Signature"] = url
    #     return response


class moduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.module
        fields = '__all__'


class sub_moduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.sub_module
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.module:
            response['Module'] = instance.module.name
        return response
