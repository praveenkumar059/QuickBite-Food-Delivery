from decimal import Decimal
from .models import FoodItem

def cart_data(request):
    """Session stores IDs and quantities only. Read current prices from SQLite."""
    raw = request.session.get('cart', {})
    if not isinstance(raw, dict):
        raw = {}
    valid = {}
    for key, quantity in raw.items():
        if isinstance(key, str) and key.isascii() and key.isdigit() and len(key) < 19 and str(int(key)) == key and type(quantity) is int and 1 <= quantity <= 20:
            valid[key] = quantity
    foods = FoodItem.objects.filter(pk__in=valid, available=True)
    rows, cleaned = [], {}
    for food in foods:
        quantity = valid[str(food.pk)]
        cleaned[str(food.pk)] = quantity
        rows.append({'food': food, 'quantity': quantity, 'subtotal': food.price * quantity})
    changed = cleaned != raw
    if changed:
        request.session['cart'] = cleaned
    return rows, sum((row['subtotal'] for row in rows), Decimal('0.00')), changed
