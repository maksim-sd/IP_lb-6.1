from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return HttpResponse("<a href='api/docs'><button>api docs</button></a><a href='admin/'><button>admin</button></a>")
