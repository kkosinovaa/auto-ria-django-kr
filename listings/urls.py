from django.urls import path

from .views import (
    ListingListCreateView,
    ListingDetailView,
    MyListingsView,
    ForbiddenWordListCreateView,
    ForbiddenWordDetailView,
    ManagerReviewListingsView,
    ManagerDeleteListingView,
)

urlpatterns = [
    path(
        "",
        ListingListCreateView.as_view(),
        name="listing-list-create"
    ),
    path(
        "my/",
        MyListingsView.as_view(),
        name="my-listings"
    ),
    path(
        "forbidden-words/",
        ForbiddenWordListCreateView.as_view(),
        name="forbidden-word-list-create"
    ),
    path(
        "forbidden-words/<int:pk>/",
        ForbiddenWordDetailView.as_view(),
        name="forbidden-word-detail"
    ),
    path(
        "manager/review/",
        ManagerReviewListingsView.as_view(),
        name="manager-review-listings"
    ),
    path(
        "manager/<int:pk>/delete/",
        ManagerDeleteListingView.as_view(),
        name="manager-delete-listing"
    ),
    path(
        "<int:pk>/",
        ListingDetailView.as_view(),
        name="listing-detail"
    ),
]
