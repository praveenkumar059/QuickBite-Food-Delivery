import uuid
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .cart import cart_data
from .forms import CheckoutForm, QuantityForm, RegisterForm
from .models import FoodItem, Order, OrderItem

def menu(request):
    return render(request, 'orders/menu.html', {'foods': FoodItem.objects.filter(available=True)})
def food_detail(request, pk):
    return render(request, 'orders/food_detail.html', {'food': get_object_or_404(FoodItem, pk=pk, available=True)})
def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        messages.success(request, 'Welcome to QuickBite!')
        return redirect('menu')
    return render(request, 'orders/register.html', {'form': form})
@login_required
def cart(request):
    rows, total, changed = cart_data(request)
    if changed:
        messages.warning(request, 'Invalid or unavailable cart items were removed. Please review your cart.')
    return render(request, 'orders/cart.html', {'rows': rows, 'total': total})
@login_required
@require_POST
def add_cart(request, pk):
    food = get_object_or_404(FoodItem, pk=pk, available=True)
    cart_data(request)
    form = QuantityForm(request.POST)
    if form.is_valid():
        contents = request.session.get('cart', {}).copy()
        quantity = contents.get(str(food.pk), 0) + form.cleaned_data['quantity']
        if quantity <= 20:
            contents[str(food.pk)] = quantity
            request.session['cart'] = contents
            messages.success(request, 'Food added to cart.')
        else:
            messages.error(request, 'Maximum quantity is 20 per food item.')
    else:
        messages.error(request, 'Quantity must be a whole number from 1 to 20.')
    return redirect('cart')
@login_required
@require_POST
def update_cart(request, pk):
    cart_data(request)
    contents = request.session.get('cart', {}).copy()
    key = str(pk)
    if key not in contents:
        messages.error(request, 'This item is not in your cart.')
    elif request.POST.get('action') == 'remove':
        del contents[key]
        request.session['cart'] = contents
        messages.success(request, 'Item removed.')
    else:
        form = QuantityForm(request.POST)
        if form.is_valid():
            contents[key] = form.cleaned_data['quantity']
            request.session['cart'] = contents
            messages.success(request, 'Quantity updated.')
        else:
            messages.error(request, 'Quantity must be a whole number from 1 to 20.')
    return redirect('cart')
@login_required
def checkout(request):
    # A unique token makes repeated submissions return the original order.
    if request.method == 'POST':
        try:
            token = uuid.UUID(request.POST.get('token', ''))
        except (ValueError, TypeError, AttributeError):
            token = None
        existing = Order.objects.filter(user=request.user, checkout_token=token).first() if token else None
        if existing:
            return redirect('order_detail', pk=existing.pk)
    rows, total, changed = cart_data(request)
    if changed:
        messages.warning(request, 'Your cart changed. Review it before checking out.')
        return redirect('cart')
    if not rows:
        messages.error(request, 'Add food before checking out.')
        return redirect('cart')
    if 'checkout_token' not in request.session:
        request.session['checkout_token'] = str(uuid.uuid4())
    form = CheckoutForm(request.POST if request.method == 'POST' else None, initial={'token': request.session['checkout_token']})
    if request.method == 'POST' and form.is_valid():
        if str(form.cleaned_data['token']) != request.session['checkout_token']:
            form.add_error(None, 'Checkout expired. Reload this page and try again.')
        else:
            with transaction.atomic():
                # Re-read availability and prices inside the write transaction.
                rows, total, changed = cart_data(request)
                if changed or not rows:
                    messages.error(request, 'Your cart changed. Please review it.')
                    return redirect('cart')
                order, created = Order.objects.get_or_create(checkout_token=form.cleaned_data['token'], defaults={'user': request.user, 'address': form.cleaned_data['address'], 'phone': form.cleaned_data['phone'], 'total': total})
                if order.user_id != request.user.pk:
                    form.add_error(None, 'Invalid checkout token.')
                    return render(request, 'orders/checkout.html', {'form': form, 'rows': rows, 'total': total})
                if created:
                    OrderItem.objects.bulk_create([OrderItem(order=order, food=row['food'], food_name=row['food'].name, unit_price=row['food'].price, quantity=row['quantity']) for row in rows])
            request.session['cart'] = {}
            request.session.pop('checkout_token', None)
            messages.success(request, 'Order placed successfully! Payment is cash on delivery.')
            return redirect('order_detail', pk=order.pk)
    return render(request, 'orders/checkout.html', {'form': form, 'rows': rows, 'total': total})
@login_required
def history(request):
    return render(request, 'orders/history.html', {'orders': Order.objects.filter(user=request.user)})
@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})
