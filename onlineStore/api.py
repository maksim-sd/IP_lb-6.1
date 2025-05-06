from ninja import NinjaAPI, Schema, FilterSchema
from .models import Category, Product
from typing import List
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from ninja.security import django_auth
from ninja.errors import HttpError
from ninja import Query


api = NinjaAPI(csrf=True)

# Категории и продукты

class CategoryIn(Schema):
    title: str
    slug: str

class CategoryOut(Schema):
    id: int
    title: str
    slug: str

class ProductIn(Schema):
    title: str
    category_id: int
    price: int
    description: str

class ProductOut(Schema):
    id: int
    title: str
    category_id: int
    price: int
    description: str

@api.post("categories/", summary="Добавить категорию")
def create_category(request, playload: CategoryIn):
    Category.objects.create(**playload.dict())
    return {"success": True, "message": "Категория успешно добавлена"}

@api.get("categories/", response=List[CategoryOut], summary="Показать категории")
def get_categories(request):
    categories = Category.objects.all()
    return categories

@api.get("categories/{slug}", response=CategoryOut, summary="Показать категорию")
def get_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    return category

@api.delete("categories/{slug}", summary="Удалить категорию")
def delete_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    category.delete()
    return {"success": True, "message": "Категория успешно удалена"}

@api.get("categories/{slug}/products", response=List[ProductOut], summary="Показать продукты категории")
def get_category_products(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return products

@api.get("products/", response=List[ProductOut], summary="Показать продукты")
def get_products(request):
    products = Product.objects.all()
    return products

@api.post("products/", summary="Добавить продукт")
def create_product(request, playload: ProductIn):
    product = Product.objects.create(**playload.dict())
    return "Продукт успешно добавлен"

@api.get("products/{id}", response=ProductOut, summary="Показать продукт")
def get_product(request, id: int):
    product = get_object_or_404(Product, id=id)
    return product

@api.delete("products/{id}", summary="Удалить продукт")
def delete_product(request, id: int):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return {"success": True, "message": "Продукт успешно удален"}

@api.patch("products/{id}", summary="Обновить продукт")
def patch_product(request, id: int, playload: ProductIn):
    product = get_object_or_404(Product, id=id)
    for attr, value in playload.dict().items():
        setattr(product, attr, value)
    product.save()
    return {"success": True, "message": "Продукт успешно обновлен"}

# Пользователи и фильтры

class UserLogin(Schema):
    username: str
    password: str


class UserRegistration(Schema):
    username: str
    password: str
    first_name: str
    last_name: str


class UserOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str


@api.post("login/", summary="Вход")
def login_system(request, playload: UserLogin):
    user = authenticate(username=playload.username, password=playload.password)
    if user is not None:
        login(request, user)
        return {"succes": True, "message": "Успешный вход"}
    return{"succes": False, "message": "Вход не выполнен"}

@api.post("logout/", summary="Выход", auth=django_auth)
def logout_system(request):
    logout(request)
    return {"succes": True, "message": "Успешный выход"}

@api.post("cheak_login/", summary="Проверка входа", auth=django_auth)
def cheak_login_system(request):
    if request.user.is_authenticated:
        return {"succes": True, "message": f"Вход выполнен username - {request.user.username}"}

@api.post("registration/", summary="Регистрация")
def registration_system(request, playload: UserRegistration):
    if User.objects.filter(username=playload.username).exists():
        return {"succes": False, "message": "Пользователь уже зарегистрирован"}
    User.objects.create(**playload.dict())
    return {"succes": True, "message": "Пользователь успешно зарегистрирован"}

@api.get("users/", summary="Показать пользователей", response=List[UserOut], auth=django_auth)
def get_users(request):
    if request.user.has_perm('auth.view_user'):
        users = User.objects.all()
        return users
    raise HttpError(501, "Не достаточно прав")

@api.get("search_name_product/", response=List[ProductOut], summary="Поиск продуктов по названию")
def get_search_name_product(request, title: str = Query(description = "Название продукта")):
    return Product.objects.filter(title__icontains = title)

@api.get("search_description_product/", response=List[ProductOut], summary="Поиск продуктов по описанию")
def get_search_description_product(request, description: str = Query(description = "Описание")):
    return Product.objects.filter(description__icontains = description)

@api.get("search_price_product/", response=List[ProductOut], summary="Поиск продуктов по цене")
def get_search_price_product(request, min_price: int = Query(description = "Минимальная цена"), max_price: int = Query(description = "Максимальная цена")):
    return Product.objects.filter(price__gte = min_price).filter(price__lte = max_price)


