from django.urls import path

from .views import ListingAnalyticsView


urlpatterns = [
    path("listings/<int:pk>/", ListingAnalyticsView.as_view()),
]
