from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return user.is_authenticated and (
            user.is_superuser
            or user.groups.filter(name="Seller").exists()
        )


class IsManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return user.is_authenticated and (
            user.is_superuser
            or user.groups.filter(name="Manager").exists()
        )


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )
