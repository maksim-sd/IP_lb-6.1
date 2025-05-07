from django.contrib import admin
from .models import Category, Product, WishList, Order, OrderProduct


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "slug"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "category"]


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "product", "count"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "datetime", "status", "total"]


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "count", "price"]
