
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Order, OrderItem
from .serializers import ProductSerializer, OrderSerializer, RegisterSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .permissions import IsAdminRole
from django.http import HttpResponse
import csv
from io import StringIO

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category"]
    search_fields = ["name", "slug", "category", "description"]
    ordering_fields = ["price", "created_at"]
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return super().get_permissions()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", "") == "admin":
            qs = Order.objects.all().order_by("-created_at")
            status_q = self.request.query_params.get("status")
            if status_q:
                qs = qs.filter(status=status_q)
            return qs
        return Order.objects.filter(user=user).order_by("-created_at")
    def perform_create(self, serializer):
        serializer.context["request"] = self.request
        return serializer.save()

class AdminProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category"]
    search_fields = ["name", "slug", "category"]
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated, IsAdminRole])
    def import_products(self, request):
        items = request.data.get("items")
        if not items:
            return Response({"detail": "items key missing"}, status=400)
        created = []
        for it in items:
            serializer = ProductSerializer(data=it)
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
        return Response({"created": created}, status=201)

class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["id", "user__email"]
    filterset_fields = ["status", "created_at"]
    @action(detail=True, methods=["put"], permission_classes=[IsAuthenticated, IsAdminRole])
    def status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"detail": "Invalid status"}, status=400)
        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)
    @action(detail=True, methods=["put"], permission_classes=[IsAuthenticated, IsAdminRole])
    def notes(self, request, pk=None):
        order = self.get_object()
        notes = request.data.get("admin_notes", "")
        order.admin_notes = notes
        order.save()
        return Response(OrderSerializer(order).data)
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated, IsAdminRole])
    def export(self, request):
        order_ids = request.data.get("order_ids", [])
        if not order_ids:
            return Response({"detail": "order_ids required"}, status=400)
        orders = Order.objects.filter(id__in=order_ids)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["order_id", "user_email", "status", "total", "created_at", "shipping_address", "items"])
        for o in orders:
            items_str = "; ".join([f"{it.product.name} x{it.qty}" for it in o.items.all()])
            writer.writerow([o.id, o.user.email if o.user else "", o.status, o.total, o.created_at.isoformat(), str(o.shipping_address), items_str])
        resp = HttpResponse(output.getvalue(), content_type="text/csv")
        resp["Content-Disposition"] = "attachment; filename=orders_export.csv"
        return resp

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_profile(request):
    user = request.user
    if getattr(user, "role", "") != "admin":
        return Response({"detail": "Forbidden"}, status=403)
    return Response(UserSerializer(user).data)
