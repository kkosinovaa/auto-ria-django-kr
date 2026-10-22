from django.urls import path

from .views import ExchangeRateListView


urlpatterns = [
    path("rates/", ExchangeRateListView.as_view()),
]