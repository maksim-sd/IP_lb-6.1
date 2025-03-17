from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()

    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()
    description = models.CharField(max_length=100)
    image = models.ImageField()