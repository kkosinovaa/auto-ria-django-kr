from rest_framework.generics import ListCreateAPIView, CreateAPIView, ListAPIView
from .models import CarBrand, CarModel
from .serializers import CarBrandSerializer, CarModelSerializer, CarCatalogRequestSerializer
from .permissions import IsAdminOrReadOnly
from users.permissions import IsSeller, IsManager
from .models import CarCatalogRequest




class CarBrandListCreateView(ListCreateAPIView):
    queryset = CarBrand.objects.all()
    serializer_class = CarBrandSerializer
    permission_classes = [IsAdminOrReadOnly]


class CarModelListCreateView(ListCreateAPIView):
    queryset = CarModel.objects.select_related("brand").all()
    serializer_class = CarModelSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["brand"]

class CarCatalogRequestCreateView(CreateAPIView):
    serializer_class = CarCatalogRequestSerializer
    permission_classes = [IsSeller]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CarCatalogRequestListView(ListAPIView):
    queryset = CarCatalogRequest.objects.all().order_by("-created_at")
    serializer_class = CarCatalogRequestSerializer
    permission_classes = [IsManager]
