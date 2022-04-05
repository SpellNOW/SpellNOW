from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Word
import csv
from django import forms
from django.core.files.storage import FileSystemStorage
import os

class UploadFileForm(forms.Form):
    csv = forms.FileField()

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
    if "pin" not in request.session or request.session["pin"] != "CONFIRMED":
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "spell/words.html", {
            'form': UploadFileForm
        })

def upload(request):
    file = request.FILES["csv"]
    fs = FileSystemStorage()
    fs.save("spell/static/spell/words.csv", file)
    f = open("spell/static/spell/words.csv", "r")
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        new_word = row[0]
        print(new_word)
        new = Word(word=new_word)
        new.save()
    f.close()
    os.remove("spell/static/spell/words.csv")
    return HttpResponseRedirect(reverse("admin_panel"))