from django.test import TestCase
from django.contrib.auth import authenticate
from .models import Category
from django.shortcuts import get_object_or_404


class CategoryTest(TestCase):
    fixtures = ['data.json']

    def test_category_add(self):
        data = {
            "title": "Мебель",
            "slug": "mebel"
        }
        response = self.client.post("/api/category/add/", content_type="application/json", data=data)
        self.assertEqual(response.status_code, 200)

    def test_categories_view(self):
        response = self.client.get("/api/categories/view/")
        self.assertEqual(response.status_code, 200)

    def test_category_view(self):
        slug = "mebel"
        response = self.client.get(f"/api/category/view/?slug={slug}")
        self.assertEqual(response.status_code, 200)

    def test_not_category_view(self):
        slug = "not"
        response = self.client.get(f"/api/category/view/?slug={slug}")
        self.assertEqual(response.status_code, 404)

    def test_category_delete(self):
        slug = "mebel"
        data = {"success": True, "message": "Категория успешно удалена"}
        response = self.client.delete(f"/api/category/delete/?slug={slug}")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), data)

    def test_not_category_delete(self):
        slug = "not"
        response = self.client.delete(f"/api/category/delete/?slug={slug}")
        self.assertEqual(response.status_code, 404)

    def test_category_products(self):
        slug = "mebel"
        response = self.client.get(f"/api/category/products/?slug={slug}")
        self.assertEqual(response.status_code, 200)

    def test_not_category_products(self):
        slug = "not"
        response = self.client.get(f"/api/category/products/?slug={slug}")
        self.assertEqual(response.status_code, 404)


class ProductTest(TestCase):
    fixtures = ["data.json"]

    def test_products(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)

    def test_product_add(self):
        data = {
            "title": "Стол",
            "category_id": 8,
            "price": 100,
            "description": "Нет"
        }
        response = self.client.post("/api/product/add/", content_type="application/json", data=data)
        self.assertEqual(response.status_code, 200)

    def test_product(self):
        id = 10
        response = self.client.get(f"/api/product/?id={id}")
        self.assertEqual(response.status_code, 200)

    def test_not_product(self):
        id = 404
        response = self.client.get(f"/api/product/?id={id}")
        self.assertEqual(response.status_code, 404)

    def test_product_delete(self):
        id = 10
        data = {"success": True, "message": "Продукт успешно удален"}
        response = self.client.delete(f"/api/product/delete/?id={id}")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), data)

    def test_not_product_delete(self):
        id = 404
        response = self.client.delete(f"/api/product/delete/?id={id}")
        self.assertEqual(response.status_code, 404)

    def test_product_update(self):
        id = 10
        data = {
            "title": "Не стол",
            "category_id": 8,
            "description": "Снова нет описания",
            "price": 150
        }
        data_response = {"success": True, "message": "Продукт успешно обновлен"}
        response = self.client.patch(f"/api/product/update/?id={id}", content_type="application/json", data=data)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), data)

    def test_product_update(self):
        id = 404
        data = {
            "title": "Не стол",
            "category_id": 8,
            "description": "Снова нет описания",
            "price": 150
        }
        data_response = {"success": True, "message": "Продукт успешно обновлен"}
        response = self.client.patch(f"/api/product/update/?id={id}", content_type="application/json", data=data)
        self.assertEqual(response.status_code, 404)

    def test_products_search_name(self):
        title = "Ст"
        response = self.client.get(f"/api/products/search/name/?title={title}")
        self.assertEqual(response.status_code, 200)

    def test_products_search_description(self):
        description = "нет"
        response = self.client.get(f"/api/products/search/description/?description={description}")
        self.assertEqual(response.status_code, 200)

    def test_products_search_price(self):
        min_price = 0
        max_price = 100
        response = self.client.get(f"/api/products/search/price/?min_price={min_price}&max_price={max_price}")
        self.assertEqual(response.status_code, 200)


class AuthTest(TestCase):
    fixtures = ["data.json"]

    def test_registration(self):
        data_response = {
            "username": "test",
            "password": "test1234",
            "first_name": "test",
            "last_name": "test"
        }
        data = {"succes": True, "message": "Пользователь успешно зарегистрирован"}
        response = self.client.post(f"/api/auth/registration/", content_type="application/json", data=data_response)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), data)

    def test_not_registration(self):
        data_response = {
            "username": "maksim",
            "password": "maskim234",
            "first_name": "",
            "last_name": ""
        }
        data = {"message": "Пользователь уже зарегистрирован!"}
        response = self.client.post(f"/api/auth/registration/", content_type="application/json", data=data_response)
        self.assertEqual(response.status_code, 409)
        self.assertDictEqual(response.json(), data)
    

class OrderTest(TestCase):
    def test_orders(self):
        response = self.client.get(f"/api/orders/")
        self.assertEqual(response.status_code, 200)

    def test_order(self):
        id = 6
        response = self.client.get(f"/api/order/?id={6}")
        self.assertEqual(response.status_code, 200)

    def test_not_order(self):
        id = 404
        response = self.client.get(f"/api/order/?id={id}")
        self.assertEqual(response.status_code, 404)

    def test_order_status_update(self):
        id = 8
        status = "Оплачен"
        data = {"succes": True, "message": "Статус успешно изменен"}
        response = self.client.put(f"/api/order/status/update/?id={id}&status={status}", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), data)

    def test_not_order_status_update(self):
        id = 404
        status = "Оплачен"
        response = self.client.put(f"/api/order/status/update/?id={id}&status={status}")
        self.assertEqual(response.status_code, 404)

    