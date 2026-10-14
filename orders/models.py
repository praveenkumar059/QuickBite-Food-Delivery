from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class FoodItem(models.Model):
    CATEGORY_CHOICES = [('meals', 'Meals'), ('snacks', 'Snacks'), ('drinks', 'Drinks'), ('desserts', 'Desserts')]
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='meals')
    image = models.CharField(max_length=150, default='img/food.svg', help_text='Relative static image path, for example img/food.svg; no uploads.')
    available = models.BooleanField(default=True)
    class Meta:
        ordering = ['name']
        constraints = [models.CheckConstraint(condition=models.Q(price__gt=0), name='food_positive_price')]
    def __str__(self):
        return self.name

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PREPARING = 'preparing', 'Preparing'
        OUT = 'out', 'Out for Delivery'
        DELIVERED = 'delivered', 'Delivered'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    address = models.TextField(max_length=500)
    phone = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    checkout_token = models.UUIDField(unique=True, editable=False)
    class Meta:
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(condition=models.Q(total__gt=0), name='order_positive_total')]
    def __str__(self):
        return f'Order #{self.pk}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True, blank=True)
    food_name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gte=1, quantity__lte=20), name='item_valid_quantity'), models.CheckConstraint(condition=models.Q(unit_price__gt=0), name='item_positive_price')]
    @property
    def subtotal(self):
        return self.unit_price * self.quantity
    def __str__(self):
        return f'{self.food_name} × {self.quantity}'
