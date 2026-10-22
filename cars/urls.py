from django.urls import path

from .views import (
    CarBrandListCreateView,
    CarModelListCreateView,
    CarCatalogRequestCreateView,
    CarCatalogRequestListView,
)


urlpatterns = [
    path("brands/", CarBrandListCreateView.as_view()),
    path("models/", CarModelListCreateView.as_view()),
    path("requests/", CarCatalogRequestCreateView.as_view()),
    path("requests/pending/", CarCatalogRequestListView.as_view()),
]
