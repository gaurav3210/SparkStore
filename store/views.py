from django.shortcuts import render, redirect, reverse
from .models import Book, Author, Cart, BookOrder
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import paypalrestsdk
# Create your views here.

def store(request):
    books = Book.objects.all()
    author = Author.objects.all()
    context = {
        'books': books,
        'author': author,
    }
    return render(request, 'base.html', context)


def book_details(request, book_id):
    context = {
        'book': Book.objects.get(pk=book_id),
    }
    return render(request, 'store/detail.html', context)


def add_to_cart(request, book_id):
    if request.user.is_authenticated:
        try:
            book= Book.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            try:
                cart = Cart.objects.get(user=request.user,active=True)
            except ObjectDoesNotExist:
                cart= Cart.objects.create(
                    user=request.user
                )
                cart.save()
            cart.add_to_cart(book_id)
        return redirect('cart')
    else:
        return redirect('index')


def remove_from_cart(request, book_id):
    if request.user.is_authenticated:
        try:
            book=Book.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            cart = Cart.objects.get(user=request.user, active=True)
            cart.remove_from_cart(book_id)
        return redirect('cart')
    else:
        return  redirect('index')


def cart(request):
    if request.user.is_authenticated:
        orders = BookOrder.objects.filter(cart_id__in=Cart.objects.filter(user=request.user.id, active=True))
        total = 0
        count = 0
        for order in orders:
            total += (order.book.price * order.quantity)
            count += order.quantity
        context = {
            'cart': orders,
            'total': total,
            'count': count,
        }
        return render(request, 'store/cart.html', context)
    else:
        return redirect('index')


def checkout(request,payment_mode):
    if request.user.is_authenticated:
        orders= BookOrder.objects.filter(cart_id__in=Cart.objects.filter(user=request.user.id,active=True))
        if payment_mode == 'paypal':
            redirect_url = checkout_paypal(request,cart,orders)
            return redirect(redirect_url)
    else:
        return redirect('index')

def checkout_paypal(request, cart, orders):
    if request.user.is_authenticated:
        items = []
        total = 0
        for order in orders:
            total += (order.book.price * order.quantity)
            book = order.book
            item = {
                'name':book.title,
                'sku'  :book.id,
                'price':str(book.price),
                'currency':'INR',
                'quantity':order.quantity,
            }
            items.append(item)

            paypalrestsdk.configure(
                {
                    "mode":"sandbox",
                    "client_id":"AV_hD4FYYvqRymxne3f4OeUfXbQ658D1mcu3RJDJFERMzhK8MgTc11NiI0QOx4NlJo19ooCW374qr4za",
                    "client_secret":"EDOSjAm8DCYwfAdNft8u5fq5GayclY1VFU7Ugn7pSUVLQozdpJ8GMM3VG8IhCYyVSG-qzOcA4gqIl0aj"
                })
            payment = paypalrestsdk.Payment(
                {
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "redirect_urls":{
                        "return_url": "http://localhost:8000/store/process/paypal",
                        "cancel_url": "http://localhost:8000/store"
                    },
                    "transactions": [{
                        "item_list": {
                            "items": item
                        },
                        "amount":{
                            "total": str(total),
                            "currency": "INR"
                        },
                        "decription": "Spark Store order."
                    }]
                }
            )
            if payment.create():
                cart_instance = cart.get()
                cart_instance.payment_id = payment.id
                cart_instance.save()
                for link in payment.links:
                    if link.method == "REDIRECT":
                        redirect_url = str(link.href)
                        return redirect_url
            else:
                return reverse("order_error")
    else:
        return redirect('index')

def order_error(request):
    if request.user.is_authenticated:
        return render(request,'store/order_error.html')
    else:
        return redirect('index')


def process_order(request,payment_mode):
    if request.user.is_authenticated:
        if payment_mode == 'paypal':
            payment_id = request.GET.get('paymentId')
            orders = BookOrder.objects.filter(cart_id__in=Cart.objects.filter(payment_id=payment_id))
            total = 0
            for order in orders:
                total += (order.book.price * order.quantity)
            context = {
                'cart':orders,
                'total':total,

            }
            return render(request,'store/process_order.html',context)
    else:
        return redirect('index')


def complete_order(request, payment_mode):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user.id, active=True)
        if payment_mode == 'paypal':
            payment = paypalrestsdk.Payment.find(cart.payment_id)
            if payment.execute({"payer_id": payment.payer.payer_info.payer_id}):
                message = "Success! Your order has been completed, and is being processed. Payment ID: %s" %(payment.id)
                cart.active = False
                cart.order_date = timezone.now()
                cart.save()

            else:
                message = "There was a problem with the transaction. Error: %s" % (payment.error.message)
                context = {
                    'message':message,
                }
                return render(request, 'store/order_complete.html',context)
    else:
        return redirect('index')






