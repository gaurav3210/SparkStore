from django.shortcuts import render
from .models import Book,Author
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