from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, PremiumPurchase
from .permissions import IsAdministrator, IsManager
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ManagerCreateSerializer,
)


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ManagerCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ManagerCreateSerializer
    permission_classes = [IsAdministrator]


class PurchasePremiumView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        with transaction.atomic():
            user = User.objects.select_for_update().get(
                pk=request.user.pk
            )

            if user.account_type == "premium":
                return Response({
                    "detail": "You already have Premium."
                }, status=400)

            purchase = PremiumPurchase.objects.create(
                user=user
            )

            user.account_type = "premium"
            user.save(update_fields=["account_type"])

        return Response({
            "message": "Premium activated successfully.",
            "account_type": user.account_type,
            "purchase_id": purchase.id,
            "payment_status": purchase.payment_status
        }, status=201)


class ManagerUserStatusView(APIView):
    permission_classes = [IsManager]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        is_active = request.data.get("is_active")

        if type(is_active) is not bool:
            raise ValidationError({
                "is_active": "Use true or false."
            })

        if user.pk == request.user.pk:
            raise PermissionDenied(
                "You cannot change your own status."
            )

        if user.is_superuser:
            raise PermissionDenied(
                "You cannot block an administrator."
            )

        if user.groups.filter(name="Manager").exists():
            if not request.user.is_superuser:
                raise PermissionDenied(
                    "Only administrators can manage other managers."
                )

        user.is_active = is_active
        user.save(update_fields=["is_active"])

        return Response({
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active
        })
