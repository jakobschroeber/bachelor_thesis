from django.shortcuts import render
from django.http import HttpResponse

from data_sink.views import users


def home_view(request,*args,**kwargs):
    my_context = {
        "my_text": "This is my text.",
        "my_number": 13579,
        "my_list": [4,5,18]
    }
    return render(request, "home.html", my_context)

def users_view(*args, **kwargs):
    return HttpResponse(users())

