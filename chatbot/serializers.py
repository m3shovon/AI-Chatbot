from rest_framework import serializers

class ChatbotInputSerializer(serializers.Serializer):
    query = serializers.CharField()
