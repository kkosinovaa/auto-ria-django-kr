from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import ExchangeRate
from .serializers import ExchangeRateSerializer


class ExchangeRateListView(ListAPIView):
    queryset = ExchangeRate.objects.all().order_by("currency")
    serializer_class = ExchangeRateSerializer
    permission_classes = [AllowAny]