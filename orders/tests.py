import uuid
from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from .models import FoodItem, Order, OrderItem


class WorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', password='TestingPassword!123')
        self.other = User.objects.create_user('bob', password='TestingPassword!123')
        self.food = FoodItem.objects.create(name='Dosa', description='Fresh dosa', price=Decimal('89.25'))
        self.client.force_login(self.user)

    def add(self, quantity=2):
        return self.client.post(reverse('add_cart', args=[self.food.pk]), {'quantity': quantity})

    def place(self):
        self.client.get(reverse('checkout'))
        return self.client.post(reverse('checkout'), {'address': '12 Main Street, Chennai', 'phone': '9876543210', 'token': self.client.session['checkout_token'], 'total': '0.01'})

    def test_public_pages_and_authentication(self):
        self.client.logout()
        for name in ['menu', 'login', 'register']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        for name in ['cart', 'checkout', 'history']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 302)
        self.assertEqual(self.client.get(reverse('food_detail', args=[self.food.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('food_detail', args=[9999])).status_code, 404)

    def test_registration_password_hash_and_invalid_login(self):
        self.client.logout()
        response = self.client.post(reverse('register'), {'username': 'carol', 'password1': 'VeryGoodPassword!321', 'password2': 'VeryGoodPassword!321'})
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='carol')
        self.assertTrue(user.check_password('VeryGoodPassword!321'))
        self.assertNotEqual(user.password, 'VeryGoodPassword!321')
        self.client.logout()
        self.assertContains(self.client.post(reverse('login'), {'username': 'carol', 'password': 'wrong'}), 'Please enter a correct')
        self.assertEqual(self.client.post(reverse('register'), {'username': 'carol', 'password1': 'x', 'password2': 'y'}).status_code, 200)

    def test_cart_updates_remove_and_invalid_quantities(self):
        for quantity in [0, -1, 21, 'bad', '1.5']:
            self.add(quantity)
            self.assertEqual(self.client.session.get('cart', {}), {})
        self.add()
        self.assertContains(self.client.get(reverse('cart')), '178.50')
        self.client.post(reverse('update_cart', args=[self.food.pk]), {'quantity': 3})
        self.assertEqual(self.client.session['cart'][str(self.food.pk)], 3)
        self.client.post(reverse('update_cart', args=[self.food.pk]), {'action': 'remove'})
        self.assertEqual(self.client.session['cart'], {})
        self.assertEqual(self.client.get(reverse('add_cart', args=[self.food.pk])).status_code, 405)

    def test_empty_and_invalid_delivery(self):
        self.assertRedirects(self.client.get(reverse('checkout')), reverse('cart'))
        self.add()
        self.client.get(reverse('checkout'))
        response = self.client.post(reverse('checkout'), {'address': 'short', 'phone': 'bad', 'token': self.client.session['checkout_token']})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())

    def test_prices_history_duplicate_and_ownership(self):
        self.add()
        self.client.get(reverse('checkout'))
        token = self.client.session['checkout_token']
        response = self.place()
        order = Order.objects.get()
        self.assertRedirects(response, reverse('order_detail', args=[order.pk]))
        self.assertEqual(order.total, Decimal('178.50'))
        self.assertEqual(order.items.get().unit_price, Decimal('89.25'))
        self.client.post(reverse('checkout'), {'token': token})
        self.assertEqual(Order.objects.count(), 1)
        self.food.price = Decimal('120.00')
        self.food.name = 'Renamed'
        self.food.save()
        self.assertEqual(order.items.get().food_name, 'Dosa')
        self.assertEqual(order.items.get().subtotal, Decimal('178.50'))
        self.assertContains(self.client.get(reverse('history')), f'#{order.pk}')
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('order_detail', args=[order.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse('history')), f'#{order.pk}')
        self.client.post(reverse('checkout'), {'token': token})
        self.assertEqual(Order.objects.count(), 1)

    def test_unavailable_missing_and_corrupt_session(self):
        self.add()
        self.food.available = False
        self.food.save()
        self.assertRedirects(self.client.get(reverse('checkout')), reverse('cart'))
        self.assertEqual(self.client.session['cart'], {})
        self.assertEqual(self.add().status_code, 404)
        self.assertEqual(self.client.post(reverse('add_cart', args=[9999]), {'quantity': 1}).status_code, 404)
        session = self.client.session
        session['cart'] = {'bad': 1, str(self.food.pk): True, '999': -5, '01': 2, '١': 2}
        session.save()
        self.assertEqual(self.client.get(reverse('cart')).status_code, 200)
        self.assertEqual(self.client.session['cart'], {})

    def test_submit_reads_current_database_price(self):
        self.add()
        self.client.get(reverse('checkout'))
        self.food.price = Decimal('100.10')
        self.food.save()
        self.place()
        self.assertEqual(Order.objects.get().total, Decimal('200.20'))

    def test_token_tampering(self):
        self.add()
        self.client.get(reverse('checkout'))
        response = self.client.post(reverse('checkout'), {'address': '12 Main Street, Chennai', 'phone': '9876543210', 'token': str(uuid.uuid4())})
        self.assertContains(response, 'Checkout expired')
        self.assertFalse(Order.objects.exists())

    def test_transaction_rolls_back(self):
        self.add()
        with patch('orders.views.OrderItem.objects.bulk_create', side_effect=RuntimeError('Simulated failure')):
            with self.assertRaises(RuntimeError):
                self.place()
        self.assertFalse(Order.objects.exists())
        self.assertFalse(OrderItem.objects.exists())
        self.assertTrue(self.client.session['cart'])

    def test_food_deletion_preserves_order_snapshot(self):
        self.add()
        self.place()
        self.food.delete()
        item = OrderItem.objects.get()
        self.assertIsNone(item.food)
        self.assertEqual(item.food_name, 'Dosa')
        self.assertEqual(item.subtotal, Decimal('178.50'))

    def test_csrf_and_admin_permissions(self):
        protected = Client(enforce_csrf_checks=True)
        protected.force_login(self.user)
        self.assertEqual(protected.post(reverse('add_cart', args=[self.food.pk]), {'quantity': 1}).status_code, 403)
        self.assertEqual(self.client.get('/admin/orders/fooditem/').status_code, 302)
        admin = User.objects.create_superuser('staff', password='AdminTesting!123')
        self.client.force_login(admin)
        response = self.client.post('/admin/orders/fooditem/add/', {'name': 'Juice', 'description': 'Fresh juice', 'price': '50.00', 'category': 'drinks', 'image': 'img/food.svg', 'available': 'on', '_save': 'Save'})
        self.assertEqual(response.status_code, 302)
        juice = FoodItem.objects.get(name='Juice')
        self.client.post(f'/admin/orders/fooditem/{juice.pk}/change/', {'name': 'Orange Juice', 'description': 'Fresh', 'price': '55.00', 'category': 'drinks', 'image': 'img/food.svg', 'available': 'on', '_save': 'Save'})
        juice.refresh_from_db()
        self.assertEqual(juice.price, Decimal('55.00'))
        self.client.post(f'/admin/orders/fooditem/{juice.pk}/delete/', {'post': 'yes'})
        self.assertFalse(FoodItem.objects.filter(pk=juice.pk).exists())
        self.client.force_login(self.user)
        self.add()
        self.place()
        order = Order.objects.get()
        self.client.force_login(admin)
        item = order.items.get()
        response = self.client.post(f'/admin/orders/order/{order.pk}/change/', {'status': 'confirmed', 'items-TOTAL_FORMS': '1', 'items-INITIAL_FORMS': '1', 'items-MIN_NUM_FORMS': '0', 'items-MAX_NUM_FORMS': '1000', 'items-0-id': item.pk, 'items-0-order': order.pk, '_save': 'Save'})
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'confirmed')
