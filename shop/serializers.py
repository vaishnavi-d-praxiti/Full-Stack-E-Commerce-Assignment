from rest_framework import serializers
from .models import User, Product, Order, OrderItem
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "username", "password", "first_name", "last_name"]

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            username=validated_data.get("username", validated_data["email"]),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role="user",
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "weight",
            "price",
            "stock",
            "image",
            "description",
            "created_at",
        ]


# ✅ Fix 1: define OrderItemSerializer before OrderSerializer
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_id", "qty", "price"]


# ✅ Fix 2: Correct handling of item creation + total computation
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "items",
            "total",
            "status",
            "created_at",
            "shipping_address",
            "admin_notes",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        user = self.context["request"].user if self.context.get("request") else None

        # Create order
        order = Order.objects.create(user=user, **validated_data)
        total = 0

        for it in items_data:
            product = it["product"]
            qty = it["qty"]
            price = product.price
            OrderItem.objects.create(order=order, product=product, qty=qty, price=price)
            total += price * qty

            # Optional: reduce stock
            if product.stock >= qty:
                product.stock -= qty
                product.save()

        order.total = total
        order.save()
        return order
