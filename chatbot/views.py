from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .serializers import ChatbotInputSerializer
from product.models import ProductDetails, Category, Attribute, AttributeTerm
import openai
from pydantic_ai import Agent

openai.api_key = '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'

class ChatbotViewSet(ViewSet):
    def create(self, request):
        serializer = ChatbotInputSerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            agent = Agent(model="gpt-4", openai_api_key=openai.api_key)
            try:
                response = self.query_database(query)
                ai_response = agent.chat(
                    f"Given this user query: '{query}', here's the response from the database: '{response}'. "
                    "Make the response more user-friendly and helpful."
                )

                return Response({
                    "query": query,
                    "response": ai_response['choices'][0]['message']['content']
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def query_database(self, query):
        products = ProductDetails.objects.filter(
            Q(title__icontains=query) | Q(tags__icontains=query)
        )
        categories = Category.objects.filter(name__icontains=query)
        attributes = Attribute.objects.filter(name__icontains=query)
        attribute_terms = AttributeTerm.objects.filter(name__icontains=query)
        results = {
            "products": list(products.values("title", "Short_description", "min_price", "max_price")),
            "categories": list(categories.values("name")),
            "attributes": list(attributes.values("name")),
            "attribute_terms": list(attribute_terms.values("name")),
        }
        return results
