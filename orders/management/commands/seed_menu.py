from decimal import Decimal
from django.core.management.base import BaseCommand
from orders.models import FoodItem
class Command(BaseCommand):
    help = 'Create sample food only; existing items are not overwritten.'
    def handle(self, *args, **options):
        for name, price, category, description in [('Veg Biryani', '149.00', 'meals', 'Aromatic rice with fresh vegetables and gentle spices.'), ('Paneer Wrap', '119.00', 'snacks', 'Soft wrap filled with paneer and crunchy vegetables.'), ('Masala Dosa', '89.00', 'meals', 'Crisp dosa with potato filling and chutney.'), ('Lime Cooler', '49.00', 'drinks', 'A refreshing lime drink.'), ('Chocolate Brownie', '79.00', 'desserts', 'A rich chocolate treat to finish your meal.')]:
            FoodItem.objects.get_or_create(name=name, defaults={'price': Decimal(price), 'category': category, 'description': description})
        self.stdout.write(self.style.SUCCESS('Sample menu ready.'))
