from ninja import NinjaAPI, Schema
from .models import Category, Product
from typing import List
from django.shortcuts import get_object_or_404

api = NinjaAPI()

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

@api.post("categories/")
def create_category(request, playload: CategoryIn):
    category = Category.objects.create(**playload.dict())
    return f"id: {category.id}"

@api.get("categories/", response=List[CategoryOut])
def get_categories(request):
    categories = Category.objects.all()
    return categories

@api.get("categories/{slug}", response=CategoryOut)
def get_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    return category

@api.delete("categories/{slug}")
def delete_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    category.delete()
    return {"success": True}

@api.get("categories/{slug}/products", response=List[ProductOut])
def get_category_products(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return products

@api.get("products/", response=List[ProductOut])
def get_products(request):
    products = Product.objects.all()
    return products

@api.post("products/")
def create_product(request, playload: ProductIn):
    product = Product.objects.create(**playload.dict())
    return f"id: {product.id}"

@api.get("products/{id}", response=ProductOut)
def get_product(request, id: int):
    product = get_object_or_404(Product, id=id)
    return product

@api.delete("products/{id}")
def delete_product(request, id: int):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return {"success": True}

@api.patch("products/{id}")
def patch_product(request, id: int, playload: ProductIn):
    product = get_object_or_404(Product, id=id)
    for attr, value in playload.dict().items():
        setattr(product, attr, value)
    product.save()
    return {"success": True}
