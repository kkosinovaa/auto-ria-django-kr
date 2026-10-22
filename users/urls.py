from django.urls import path

from .views import (
    RegisterView,
    MeView,
    ManagerCreateView,
    PurchasePremiumView,
    ManagerUserStatusView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("managers/", ManagerCreateView.as_view(), name="manager-create"),
    path(
        "premium/purchase/",
        PurchasePremiumView.as_view(),
        name="premium-purchase"
    ),
    path(
        "manager/users/<int:pk>/status/",
        ManagerUserStatusView.as_view(),
        name="manager-user-status"
    ),
]
