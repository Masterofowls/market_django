from __future__ import annotations

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.serializers import ProductListSerializer
from apps.recommendations.services import recommend_for_user, suggest_products


class SuggestionView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):  # noqa: ANN001
        category = request.query_params.get("category")
        qs = suggest_products(
            query=request.query_params.get("q", ""),
            category_id=int(category) if category else None,
            tag=request.query_params.get("tag", ""),
            limit=int(request.query_params.get("limit", 12)),
        )
        return Response(ProductListSerializer(qs, many=True, context={"request": request}).data)


class PersonalizedRecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):  # noqa: ANN001
        qs = recommend_for_user(request.user)
        return Response(ProductListSerializer(qs, many=True, context={"request": request}).data)
