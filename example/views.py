# example/views.py
from datetime import datetime
from django.shortcuts import render

def index(request):
    context = {
        'now': datetime.now()
    }
    return render(request, 'index.html', context)