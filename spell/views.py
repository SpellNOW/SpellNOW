from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse


# Create your views here.
def index(request):
    if "pin" not in request.session or request.session["pin"] == "" or request.session["pin"] == "CONFIRMED":
        return render(request, "spell/index.html", {
            "message": ""
        })
    else:
        request.session["pin"] = ""
        return render(request, "spell/index.html", {
            "message": "Invalid PIN!"
        })

def confirm(request):
    pin = request.POST["pin"]
    if pin != "6911":
        request.session["pin"] = "UNCONFIRMED"
        return HttpResponseRedirect(reverse("index"))
    else:
        request.session["pin"] = "CONFIRMED"
        return HttpResponseRedirect(reverse("admin_panel"))

def admin_panel(request):
    if "pin" not in request.session or request.session["pin"] == "" or request.session["pin"] == "CONFIRMED":
        return render(request, "spell/words.html", {
            "message": ""
        })
    else:
        request.session["pin"] = ""
        return render(request, "spell/words.html", {
            "message": "Invalid PIN!"
        })