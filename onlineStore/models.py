from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название")
    slug = models.SlugField(verbose_name="Slug")

    def __str__(self):
        return self.title
    
    class Meta:
        unique_together = (('slug'),)
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    title = models.CharField(max_length=50, verbose_name="Название")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    price = models.IntegerField(verbose_name="Цена")
    description = models.CharField(max_length=100, verbose_name="Описание")
    image = models.ImageField(blank=True, null=True, verbose_name="Фото")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    count = models.IntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    datetime = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    status = models.CharField(max_length=50, verbose_name="Статус")
    total = models.IntegerField( null=True, verbose_name="Полная стоимость")

    def __str__(self):
        return str(self.id)
    
    def get_total_sum(self):
        return sum(item.get_sum() for item in self.products.all())

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ", related_name="products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    count = models.IntegerField(verbose_name="Количество")
    price = models.IntegerField(verbose_name="Цена")

    def get_sum(self):
        return self.count * self.product.price

    class Meta:
        verbose_name = "Детали заказа"
        verbose_name_plural = "Детали заказов"