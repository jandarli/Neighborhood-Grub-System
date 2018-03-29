from django.shortcuts import get_object_or_404, render, redirect

from dishes.models import *

def index(request):
    context = {}
    return render(request, "ngs/index.html", context)
