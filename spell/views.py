from re import L
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Word
import csv
from django import forms
from django.core.files.storage import FileSystemStorage
import os
import requests
import json
from os.path import exists

class UploadFileForm(forms.Form):
    csv = forms.FileField()

def is_word(word):
    r = requests.get('https://dictionaryapi.com/api/v3/references/collegiate/json/' + word + '?key=e115f2c9-c50e-4fc0-9711-f5264280ecff')
    info = r.json()

    error = False

    try:
        check = info[0]
        try:
            check = info[0]["meta"]["id"]
        except TypeError:
            error = True
    except IndexError:
        error = True

    there = False

    if not error:
        for stuff in info:
            if (stuff["hwi"]["hw"].replace("*", "")).lower() == word:
                there = True

    if not there:
        error = True

    cool = False

    if not error:
        for stuff in info:
            try:
                check = stuff["hwi"]["prs"]
                cool = True
            except KeyError:
                pass

    if not cool:
        error = True
    
    return not error

def create_word(word):
    r = requests.get('https://dictionaryapi.com/api/v3/references/collegiate/json/' + word + '?key=e115f2c9-c50e-4fc0-9711-f5264280ecff')
    info = r.json()

    replacers = []
    parts = []
    right = []
    origin = []
    audio = []

    final_parts = ""
    final_right = "<ol>"
    final_origin = "<ol>"
    final_audio = ""

    for stuff in info:
        if (stuff["hwi"]["hw"].replace("*", "")) == word:
            parts.append(stuff["fl"].capitalize())
        parts = list(set(parts))

    for stuff in info:
        for thing in stuff["shortdef"]:
            if (stuff["hwi"]["hw"].replace("*", "")) == word:
                right.append(thing.capitalize())

    for stuff in info:
        try:
            stop = stuff["et"][0][1]
            it = False
            ayush = ""
            count = 0
            for i in range(len(stop)):
                if it:
                    ayush += stop[i]
                
                if stop[i] == '{' and it == False:
                    it = True
                    ayush += "{"

                if stop[i] == '}':
                    if count == 0:
                        count = 1
                    else:
                        count = 0
                        it = False
                        replacers.append(ayush)
                        ayush = ""

            for russia in replacers:
                stop = stop.replace(russia, "")
                
            if (stuff["hwi"]["hw"].replace("*", "")) == word:
                origin.append(stop)
        except KeyError:
            pass

    for stuff in info:
        try:
            check = stuff["hwi"]["prs"]
            for thing in check:
                id = thing["sound"]["audio"]

                if id[0] + id[1] + id[2] == "bix":
                    great = "bix"
                elif id[0] + id[1] == "gg":
                    great = "gg"
                elif not id[0].isalpha():
                    great = "number"
                else:
                    great = id[0]
                
                if (stuff["hwi"]["hw"].replace("*", "")) == word:
                    audio.append("https://media.merriam-webster.com/audio/prons/en/us/mp3/" + great + "/" + id + ".mp3")
        except KeyError:
            pass

    for i in range(len(parts)):
        if i != (len(parts) - 1):
            final_parts += (parts[i] + ", ")
        else: 
            final_parts += parts[i]
    
    for i in range(len(origin)):
        final_origin += ("<li>" + origin[i] + "</li>")
    
    final_origin += "</ol>"

    for i in range(len(origin)):
        final_right += ("<li>" + right[i] + "</li>")
    
    final_right += "</ol>"

    for i in range(len(audio)):
        if i != (len(audio) - 1):
            final_audio += (audio[i] + ", ")
        else: 
            final_audio += audio[i]
    
    new = Word(word=word, speech = final_parts, origin = final_origin, definition = final_right, pronounce = final_audio)
    new.save()

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
        words = Word.objects.all()
        return render(request, "spell/words.html", {
            'thing': words
        })

def upload(request):
    nots = []
    already = []
    file = request.FILES["csv"]
    fs = FileSystemStorage()
    fs.save("spell/static/spell/words.csv", file)
    f = open("spell/static/spell/words.csv", "r")
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        new_word = row[0].lower()
        
        if not Word.objects.filter(word=new_word):
            if is_word(new_word):
                create_word(new_word)
            else:
                nots.append(new_word)
        else:
            already.append(new_word)
    f.close()
    os.remove("spell/static/spell/words.csv")

    if len(nots) > 0:
        fields = ['Words', 'Part of Speech', 'Language of Origin', 'Definition']
            
        # writing to csv file 
        with open("spell/static/spell/CustomTemplate.csv", 'w', newline="") as csvfile:
            csvwriter = csv.writer(csvfile) 
            csvwriter.writerow(fields) 
            
            for thingy in nots:
                rows = [thingy, "", "", ""]
                csvwriter.writerow(rows)

    if len(nots) > 0 and not len(already) > 0:
        return render(request, "spell/unadded.html", {
            'nots': nots
        })
    elif len(already) > 0 and not len(nots) > 0:
        return render(request, "spell/unadded.html", {
            'already': already
        })
    elif len(already) > 0 and len(nots) > 0:
        return render(request, "spell/unadded.html", {
            'nots': nots,
            'already': already
        })
    else:
        return HttpResponseRedirect(reverse("admin_panel"))

def upload_custom(request):
    if exists("spell/static/spell/custom.csv"):
        os.remove("spell/static/spell/custom.csv")
    already = []
    new_word = []
    file = request.FILES["custom"]
    fs = FileSystemStorage()
    fs.save("spell/static/spell/custom.csv", file)
    f = open("spell/static/spell/custom.csv", "r")
    reader = csv.reader(f)
    next(reader)
    counter = 0
    for row in reader:
        final = row[0].lower()
        
        if not Word.objects.filter(word=final):
            new_word.append(final)
        else:
            already.append(final)
        
        counter += 1
    f.close()
    return render(request, "spell/custom.html", {
        'words': new_word,
        'already': already
    })

def upload_sounds(request):
    f = open("spell/static/spell/custom.csv", "r")
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        final = row[0].lower()
        
        if not Word.objects.filter(word=final):
            file = request.FILES["file-"+final]
            fs = FileSystemStorage()
            fs.save("spell/static/spell/sounds/" + final + ".mp3", file)
            new_word = row[0].lower()
            new_speech = row[1].lower()
            new_origin = row[2].lower()
            new_def = row[3].lower()

            new = Word(word=new_word, speech = new_speech, origin = new_origin, definition = new_def, pronounce = ("*--*" + new_word))
            new.save()
    return HttpResponseRedirect(reverse("admin_panel"))