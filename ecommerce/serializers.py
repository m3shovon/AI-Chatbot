from rest_framework import serializers
from ecommerce import models


class pageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.page
        fields = '__all__'
        
    def to_representation(self, instance):
        response = super().to_representation(instance)
        features = models.feature.objects.filter(page=instance.id)
        features_response = []
        for i in features:
            features_response.append(featureSerializer(i).data)
        response["features"] = features_response
        return response

class imageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.image
        fields = '__all__'

class featureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.feature
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        items = models.feature_item.objects.filter(feature=instance.id)
        items_response = []
        for i in items:
            items_response.append(feature_itemSerializer(i).data)
        response["items"] = items_response
        return response
    

class feature_itemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.feature_item
        fields = '__all__'