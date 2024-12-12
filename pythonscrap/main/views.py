from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    print("Something")
    return HttpResponse("<h4>Start gomafia scrap project (Checking...)</h4>")
