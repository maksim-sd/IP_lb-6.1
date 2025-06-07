from base64 import b64encode
from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from .models import Category, Product, WishList, Order, OrderProduct
from .api import CategoryIn, ProductIn, UserRegistration, WishListIn


def get_http_authorization(username, password):
    credentials = f"{username}:{password}".encode("utf-8")
    return {"HTTP_AUTHORIZATION": f"Basic {b64encode(credentials).decode("utf-8")}"}


class APITest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="testuser", 
            password="user1234",
        )
        self.admin = User.objects.create_superuser(
            username="testadmin", 
            password="admin1234",
        )
        
        self.user_auth = get_http_authorization("testuser", "user1234")
        self.admin_auth = get_http_authorization("testadmin", "admin1234")

        self.category = Category.objects.create(
            title="Тестовая категория",
            slug="test-category"
        )
        
        self.product = Product.objects.create(
            title="Тестовый продукт",
            category=self.category,
            price=1000,
            description="Тестовое описание"
        )
        
        self.wishlist_item = WishList.objects.create(
            user=self.user,
            product=self.product,
            count=1
        )
        
        self.order = Order.objects.create(
            user=self.user,
            status="Новый",
            total=1000
        )
        
        self.order_product = OrderProduct.objects.create(
            order=self.order,
            product=self.product,
            count=1,
            price=1000
        )

    def test_post_category_admin(self):
        payload = CategoryIn(title="Новая категория", slug="new-category").dict()
        response = self.client.post("/api/category", data=payload, content_type="application/json", **self.admin_auth)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Категория успешно добавлена", response.json()["message"])

    def test_post_category_no_permission(self):
        payload = CategoryIn(title="Новая категория", slug="new-category").dict()
        response = self.client.post("/api/category", data=payload, content_type="application/json", **self.user_auth)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Не достаточно прав")

    def test_get_categories(self):
        response = self.client.get("/api/categories")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_category(self):
        response = self.client.get(f"/api/category/{self.category.slug}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Тестовая категория")

    def test_delete_category_admin(self):
        response = self.client.delete(f"/api/category/{self.category.slug}", **self.admin_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Категория успешно удалена")

    def test_get_category_products(self):
        response = self.client.get(f"/api/category/{self.category.slug}/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_post_product_admin(self):
        payload = ProductIn(
            title="Новый продукт",
            category_id=self.category.id,
            price=2000,
            description="Новое описание"
        ).dict()
        response = self.client.post("/api/product", data=payload, content_type="application/json", **self.admin_auth)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Продукт успешно добавлен", response.json()["message"])

    def test_get_products(self):
        response = self.client.get("/api/products")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_product(self):
        response = self.client.get(f"/api/product/{self.product.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Тестовый продукт")

    def test_patch_product_admin(self):
        payload = ProductIn(
            title="Обновленный продукт",
            category_id=self.category.id,
            price=1500,
            description="Обновленное описание"
        ).dict()
        response = self.client.patch(f"/api/product/{self.product.id}", data=payload, content_type="application/json", **self.admin_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Продукт успешно обновлен")

    def test_delete_product_admin(self):
        response = self.client.delete(f"/api/product/{self.product.id}", **self.admin_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Продукт успешно удален")

    def test_post_registration(self):
        payload = UserRegistration(
            username="newuser",
            password="newpass123",
            first_name="New",
            last_name="User"
        ).dict()
        response = self.client.post("/api/auth/registration", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Пользователь успешно зарегистрирован")

    def test_post_registration_existing_user(self):
        payload = UserRegistration(
            username="testuser",
            password="newpass123",
            first_name="New",
            last_name="User"
        ).dict()
        response = self.client.post("/api/auth/registration", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["detail"], "Пользователь уже зарегистрирован")

    def test_get_auth_check(self):
        response = self.client.get("/api/auth/check", **self.user_auth)
        self.assertEqual(response.status_code, 200)
        self.assertIn("testuser", response.json()["message"])

    def test_get_users_admin(self):
        response = self.client.get("/api/users", **self.admin_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_get_products_filter(self):
        response = self.client.get("/api/products/filter?title=Тест")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_products_filter_price(self):
        response = self.client.get("/api/products/filter?min_price=500&max_price=1500")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_wishlist(self):
        response = self.client.get("/api/wishlist", **self.user_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_post_wishlist_product(self):
        payload = WishListIn(product_id=self.product.id, count=2).dict()
        response = self.client.post("/api/wishlist/product", data=payload, content_type="application/json", **self.user_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Товар успешно добавлен в корзину")

    def test_delete_wishlist(self):
        response = self.client.delete("/api/wishlist", **self.user_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Корзина успешно очищена")

    def test_get_orders(self):
        response = self.client.get("/api/orders", **self.user_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_order(self):
        response = self.client.get(f"/api/order/{self.order.id}", **self.user_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_post_order(self):
        response = self.client.post("/api/order", **self.user_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Заказ успешно создан")

    def test_put_order_status_admin(self):
        response = self.client.put(f"/api/order/{self.order.id}/status/В обработке", **self.admin_auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Статус успешно изменен")