from ninja import NinjaAPI, Schema
from .models import Category, Product, WishList, Order, OrderProduct
from typing import List
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import permission_required
from ninja.errors import HttpError
from ninja import Query
from datetime import datetime
from ninja.security import HttpBasicAuth


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
   
    
class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = authenticate(username=username, password=password)
        return user


@api.post("category", auth=BasicAuth(), summary="Добавить категорию", tags=["Категория"])
def post_category(request, playload: CategoryIn):
    if not request.auth.has_perm('category.add_category'):
        raise HttpError(403, "Не достаточно прав")
    if Category.objects.filter(slug=playload.slug).exists():
        raise HttpError(400, "Категория с указанным slug уже существует")
    category = Category.objects.create(**playload.dict())
    return {"message": f"Категория успешно добавлена. Код категории: {category.id}"}

@api.get("categories", response=List[CategoryOut], summary="Показать категории", tags=["Категория"])
def get_categories(request):
    categories = Category.objects.all()
    return categories

@api.get("category/{slug}", response=CategoryOut, summary="Показать категорию", tags=["Категория"])
def get_category(request, slug:str):
    category = get_object_or_404(Category, slug=slug)
    return category

@api.delete("category/{slug}", auth=BasicAuth(), summary="Удалить категорию", tags=["Категория"])
def delete_category(request, slug:str):
    if not request.auth.has_perm('category.delete_category'):
        raise HttpError(403, "Не достаточно прав")
    category = get_object_or_404(Category, slug=slug)
    category.delete()
    return {"message": "Категория успешно удалена"}

@api.get("category/{slug}/products/", response=List[ProductOut], summary="Показать продукты категории", tags=["Категория"])
def get_category_products(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return products

@api.get("products", response=List[ProductOut], summary="Показать продукты", tags=["Продукт"])
def get_products(request):
    products = Product.objects.all()
    return products

@api.post("product", auth=BasicAuth(), summary="Добавить продукт", tags=["Продукт"])
def post_product(request, playload: ProductIn):
    if not request.auth.has_perm('product.add_product'):
        raise HttpError(403, "Не достаточно прав")
    product = Product.objects.create(**playload.dict())
    return {"message": f"Продукт успешно добавлен. Код продукта: {product.id}"}

@api.get("product/{id}", response=ProductOut, summary="Показать продукт", tags=["Продукт"])
def get_product(request, id:int):
    product = get_object_or_404(Product, id=id)
    return product

@api.delete("product/{id}", auth=BasicAuth(), summary="Удалить продукт", tags=["Продукт"])
def delete_product(request, id:int):
    if not request.auth.has_perm('product.delete_product'):
        raise HttpError(403, "Не достаточно прав")
    product = get_object_or_404(Product, id=id)
    product.delete()
    return {"message": "Продукт успешно удален"}

@api.patch("product/{id}", auth=BasicAuth(), summary="Обновить продукт", tags=["Продукт"])
def patch_product(request, id: int, playload: ProductIn):
    if not request.auth.has_perm('product.change_product'):
        raise HttpError(403, "Не достаточно прав")
    product = get_object_or_404(Product, id=id)
    for attr, value in playload.dict().items():
        setattr(product, attr, value)
    product.save()
    return {"message": "Продукт успешно обновлен"}

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


@api.get("auth/check", summary="Проверка входа", auth=BasicAuth(), tags=["Пользователь"])
def get_auth_check(request):
    if request.auth:
        return {"message": f"Вход выполнен username - {request.auth.username}"}

@api.post("auth/registration", summary="Регистрация", tags=["Пользователь"])
def post_auth_registration(request, playload:UserRegistration):
    if User.objects.filter(username=playload.username).exists():
        raise HttpError(409, "Пользователь уже зарегистрирован")
    User.objects.create(**playload.dict())
    return {"message": "Пользователь успешно зарегистрирован"}

@api.get("users", summary="Показать пользователей", response=List[UserOut], auth=BasicAuth(), tags=["Пользователь"])
def get_users(request):
    if request.auth.has_perm('auth.view_user'):
        return User.objects.all()
    raise HttpError(403, "Не достаточно прав")

@api.get("products/filter", response=List[ProductOut], summary="Отфильтровать продукты", tags=["Продукт"])
def get_products_filter(request, title: str = Query(None, description = "Название продукта"),
                            description: str = Query(None, description = "Описание"),
                            min_price: int = Query(None, description = "Минимальная цена"),
                            max_price: int = Query(None, description = "Максимальная цена")):
    products = Product.objects.all()
    if title is not None:
        products = products.filter(title__iregex = title)
    if description is not None:
        products = products.filter(description__iregex = description)
    if min_price is not None:
        products = products.filter(price__gte = min_price)
    if max_price is not None:
        products = products.filter(price__lte = max_price)
    return products

# Заказы и корзины


class WishListOut(Schema):
    id: int
    product: ProductOut
    count: int


class WishListIn(Schema):
    product_id: int
    count: int


class OrderOut(Schema):
    id: int
    user: UserOut
    datetime: datetime
    status: str
    total: int


class OrderProductOut(Schema):
    order_id: int
    product: ProductOut
    count: int
    price: int


@api.get("wishlist", auth=BasicAuth(), response=List[WishListOut], summary="Показать корзину", tags=["Корзина"])
def get_wishlist(request):
    wishlists = WishList.objects.filter(user=request.auth)
    return wishlists

@api.post("wishlist/product", auth=BasicAuth(), summary="Добавить товар в корзину", tags=["Корзина"])
def post_wishlist_product(request, playload: WishListIn):
    user = request.auth
    product = get_object_or_404(Product, id=playload.product_id)
    if WishList.objects.filter(user=user, product=product):
        wishlist = get_object_or_404(WishList, user=user, product=product)
        wishlist.count = wishlist.count + playload.count
        wishlist.save()
    else:
        count = playload.count
        WishList.objects.create(user=user, product=product, count = count)
    return {"message": "Товар успешно добавлен в корзину"}

@api.delete("wishlist", auth=BasicAuth(), summary="Очистить корзину", tags=["Корзина"])
def delete_wishlist(request):
    wishlist = WishList.objects.filter(user=request.auth)
    for i in wishlist:
        i.delete()
    return {"message": "Корзина успешно очищена"}

@api.get("orders", auth=BasicAuth(), response=List[OrderOut], summary="Показать заказы", tags=["Заказ"])
def get_orders(request):
    return Order.objects.filter(user=request.auth)

@api.get("order/{id}", auth=BasicAuth(), response=List[OrderProductOut], summary="Показать детали заказа", tags=["Заказ"])
def get_order(request, id:int):
    order = get_object_or_404(Order, id=id, user=request.auth)
    return order.products.all()

@api.post("order", auth=BasicAuth(), summary="Создать заказ", tags=["Заказ"])
def post_order(request):
    if not WishList.objects.filter(user=request.auth).exists():
        raise HttpError('400', "Корзина пустая")
    wishlist = WishList.objects.filter(user=request.auth)
    order = Order.objects.create(user=request.auth, status="Новый")
    for i in wishlist:
        OrderProduct.objects.create(order=order, product=i.product, count=i.count, price=i.product.price)
        i.delete()
    order.total = order.get_total_sum()
    order.save()
    return {"message": "Заказ успешно создан"}

@api.put("order/{id}/status/{status}", auth=BasicAuth(), summary="Изменить статус заказа", tags=["Заказ"])
def put_order_status(request, id:int, status:str):
    if not request.auth.has_perm('order.change_order'):
        raise HttpError('403', "Не достаточно прав")
    order = get_object_or_404(Order, id=id)
    order.status = status
    order.save()
    return {"message": "Статус успешно изменен"}
