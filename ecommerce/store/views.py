from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime as date
from .models import *
from .utils import cookieCart, cartData, guestOrder
from .forms import UserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .filters import ProductFilter


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()

    filteredProducts = ProductFilter(request.GET, queryset=products)
    products = filteredProducts.qs

    context = {'products': products, 'cartItems': cartItems,
               'filteredProducts': filteredProducts}
    return render(request, 'store/store.html', context)


def productPage(request, pk):
    data = cartData(request)
    cartItems = data['cartItems']
    product = Product.objects.get(id=pk)

    if request.method == 'POST':
        product = Product.objects.get(id=pk)
        try:
            customer = request.user.customer
            print(customer)
        except:
            device = request.COOKIES['device']
            print(device)
            customer, created = Customer.objects.get_or_create(device=device)

        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(
            order=order, product=product)
        orderItem.quantity = request.POST['quantity']
        orderItem.save()

    context = {'cartItems': cartItems,
               'product': product}
    return render(request, 'store/product.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    try:
        customer = request.user.customer
    except:
        device = request.COOKIES['device']
        customer, created = Customer.objects.get_or_create(device=device)

    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    print(data)
    productId = data['productId']
    action = data['action']
    additionalQt = data.get('additionalQt', None)
    print('Action:', action)
    print('Product:', productId)

    try:
        customer = request.user.customer
    except:
        device = request.COOKIES['device']
        customer, created = Customer.objects.get_or_create(device=device)

    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    product = Product.objects.get(id=productId)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        if orderItem.quantity is None:
            if additionalQt is not None:
                orderItem.quantity = additionalQt
            else:
                orderItem.quantity = 1
        else:
            if additionalQt is not None:
                orderItem.quantity += additionalQt
            else:
                orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = date.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted', safe=False)


def loginPage(request):
    data = cartData(request)
    cartItems = data['cartItems']

    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('store')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {'cartItems': cartItems}
        return render(request, 'store/login.html', context)


def registerPage(request):
    data = cartData(request)
    cartItems = data['cartItems']

    if request.user.is_authenticated:
        return redirect('store')
    else:
        form = UserForm()

        if request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, f'Account created for {user}.')
                return redirect('login')

        context = {'cartItems': cartItems, 'form': form}
        return render(request, 'store/register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')
