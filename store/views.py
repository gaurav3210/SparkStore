from django.shortcuts import render
#from .models import Book
# Create your views here.
def store(request):
    return render(request,'store.html')
'''
def store(request):
    count = Book.objects.all().count()
    context = {
        'count':count,
        'page': 'welcome to the bookkeeper bookstore'
    }
    request.session['location'] = "unknown"
    if request.user.is_authenticated:
        request.session['location'] = "Earth"
    return render(request, 'base.html', context)
'''