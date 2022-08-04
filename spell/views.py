
from importlib.metadata import distribution
from operator import ilshift
from re import L
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Account, Word, Tag, Report, Root, ReportDetail, EmailValidate
import csv
from django import forms
from django.core.files.storage import FileSystemStorage
import os
import stripe
import requests
import json
from os.path import exists
from django.db.models import Q
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import smtplib
from django.contrib.auth.decorators import login_required, user_passes_test
from captcha.fields import CaptchaField
import datetime
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class MyForm(forms.Form):
   captcha=CaptchaField()

def is_word(word):
    error = False
    info = ""

    r = requests.get('https://dictionaryapi.com/api/v3/references/collegiate/json/' + word + '?key=e115f2c9-c50e-4fc0-9711-f5264280ecff')

    try:
        info = r.json()
    except:
        error = True
    
    if not error:
        try:
            check = info[0]
            try:
                check = info[0]["meta"]["id"]
            except:
                error = True
        except:
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
            except:
                pass

    if not cool:
        error = True
    
    if not error:
        for stuff in info:
            if (stuff["hwi"]["hw"].replace("*", "")).lower() == word:
                try:
                    stuff["fl"].capitalize()
                except:
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
    final_right = ["No definition given."]
    final_origin = ["No origin given."]
    final_audio = "["

    for stuff in info:
        if (stuff["hwi"]["hw"].replace("*", "")).lower() == word:
            parts.append(stuff["fl"].capitalize())
        parts = list(set(parts))

    for stuff in info:
        for thing in stuff["shortdef"]:
            if (stuff["hwi"]["hw"].replace("*", "")).lower() == word:
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
                
            if (stuff["hwi"]["hw"].replace("*", "")).lower() == word:
                origin.append(stop)
        except:
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
                
                if (stuff["hwi"]["hw"].replace("*", "")).lower() == word:
                    audio.append("https://media.merriam-webster.com/audio/prons/en/us/mp3/" + great + "/" + id + ".mp3")
        except:
            pass

    for i in range(len(parts)):
        if i != (len(parts) - 1):
            final_parts += (parts[i] + ", ")
        else: 
            final_parts += parts[i]
    
    final_origin.append(None)
    final_origin.append(None)
    for i in range(len(origin)):
        if not i >= 3:
            final_origin[i] = origin[i]

    final_right.append(None)
    final_right.append(None)
    for i in range(len(right)):
        if not i >= 3:
            final_right[i] = right[i]

    for i in range(len(audio)):
        if i != (len(audio) - 1):
            final_audio += ("'" + audio[i] + "', ")
        else: 
            final_audio += ("'" + audio[i] + "']")
    
    new = Word(word=word, speech = final_parts, origin1 = final_origin[0], origin2 = final_origin[1], origin3 = final_origin[2], definition1 = final_right[0], definition2 = final_right[1], definition3 = final_right[2], pronounce = final_audio, tagged = False)
    new.save()

def locked(user):
    if not user.is_superuser:
        account = Account.objects.get(username=user.username)
        gen = str(account.date_joined).split("+")[0]
        day = gen.split(" ")[0]
        time = gen.split(" ")[1]
        opyear = int(day.split("-")[0])
        opmonth = int(day.split("-")[1])
        opday = int(day.split("-")[2])
        ophour = int(time.split(":")[0])
        opmin = int(time.split(":")[1])
        opsec = int((time.split(":")[2]).split(".")[0])
        tv = datetime.datetime(opyear, opmonth, opday, ophour, opmin, opsec)
        if (account.subscribed == False) and ((datetime.datetime.now() - tv) > datetime.timedelta(days=30)):
            account.locked = True
            account.save()
        elif account.subscribed == False:
            account.daysleft = 30 - ((datetime.datetime.now() - tv).days)
            account.save()

    if user.is_superuser:
        return True
    elif Account.objects.get(username=user.username).locked == True:
        return False
    else:
        return True

# Create your views here.

def error_404(request, exception):
    return render(request, "spell/error_404.html", {})

# Homepage
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("admin_panel"))
    else:
        return render(request, "spell/index.html")

def contact(request):
    msg = MIMEMultipart()
    msg['Subject'] = 'SpellNOW! Contact Notification'
    msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
    msg["To"] = "support@spellnow.org"
    body_text = """Hello!\n\nThis is an official SpellNOW! Notification. The following details a contact request from a user.\n\n""" + "Name: " + request.POST["name"] + "\nEmail: " + request.POST["email"] + "\nSubject: " + request.POST["subject"] + "\n\nMessage:\n\n" + request.POST["message"] + """\n\nBe sure to contact them back, and have a great day!\n\nSincerely,\nSpellNOW! Support Team"""

    body_part = MIMEText(body_text, 'plain')
    msg.attach(body_part)
    with smtplib.SMTP(host="smtp.ionos.com", port=587) as smtp_obj:
        smtp_obj.ehlo()
        smtp_obj.starttls()
        smtp_obj.ehlo()
        smtp_obj.login("support@spellnow.org", "3BGV6@7*X-2Yi/e")
        smtp_obj.sendmail(msg['From'], [msg['To'],], msg.as_string())
    
    return HttpResponseRedirect(reverse("index"))

def contactus(request):
    msg = MIMEMultipart()
    msg['Subject'] = 'SpellNOW! Contact Notification'
    msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
    msg["To"] = "support@spellnow.org"
    body_text = """Hello!\n\nThis is an official SpellNOW! Notification. The following details a contact request from a user.\n\n""" + "Name: " + request.POST["name"] + "\nEmail: " + request.POST["email"] + "\nSubject: " + request.POST["subject"] + "\n\nMessage:\n\n" + request.POST["message"] + """\n\nBe sure to contact them back, and have a great day!\n\nSincerely,\nSpellNOW! Support Team"""

    body_part = MIMEText(body_text, 'plain')
    msg.attach(body_part)
    with smtplib.SMTP(host="smtp.ionos.com", port=587) as smtp_obj:
        smtp_obj.ehlo()
        smtp_obj.starttls()
        smtp_obj.ehlo()
        smtp_obj.login("support@spellnow.org", "3BGV6@7*X-2Yi/e")
        smtp_obj.sendmail(msg['From'], [msg['To'],], msg.as_string())
    
    return HttpResponseRedirect(reverse("contactrender"))

def contactrender(request):
    return render(request, "spell/contact.html", {
        "bar": "",
        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
        "active": "contactus"
    })

# Authorization pages
def login(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        
        if user is None:
            return render(request, "spell/login.html", {
                "form": MyForm(),
                "message": "Invalid username and/or password."
            })
        else:
            auth_login(request, user)
            return HttpResponseRedirect(reverse("admin_panel"))
    else:
        form=MyForm()
        return render(request, "spell/login.html", {"form": form})

def register(request):
    if request.method == "POST":
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        # Attempt to create new user
        try:
            user = Account.objects.create_user(username, email, password, subscribed=False, locked=False)
            user.first_name = fname
            user.last_name = lname
            user.save()
        except IntegrityError:
            return render(request, "spell/register.html", {
                "form": MyForm(),
                "message": "Username already taken."
            })
        
        auth_login(request, user)
        return HttpResponseRedirect(reverse("admin_panel"))
    else:
        form=MyForm()
        return render(request, "spell/register.html", {"form": form})

@login_required(login_url='/login')
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse("login"))

# Dashboard
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def admin_panel(request):
    if not request.user.is_superuser:
        userusing = Account.objects.get(username=request.user.username)

        totalwords = 0
        for report in Report.objects.filter(user=userusing, specific=False, finished__gt=datetime.date.today()):
            totalwords += report.total
        
        lastwords = 0
        start = datetime.date.today() - datetime.timedelta(days = 1)
        end = datetime.date.today()

        for report in Report.objects.filter(user=userusing, specific=False, finished__range=(start, end)):
            lastwords += report.total
        
        word_conc = ""
        wordsperc = 0
        if lastwords < totalwords:
            word_conc = "increase"
            if lastwords != 0:
                wordsperc = int((totalwords / lastwords) * 100) - 100
            else:
                wordsperc = 0
        elif lastwords > totalwords:
            word_conc = "decrease"
            if lastwords != 0:
                wordsperc = 100 - int((totalwords / lastwords) * 100)
            else:
                wordsperc = 0
        
        correctwords = 0
        for report in Report.objects.filter(user=userusing, specific=False, finished__gt=datetime.date.today()):
            correctwords += report.correct
        
        lastcorrs = 0
        start = datetime.date.today() - datetime.timedelta(days = 1)
        end = datetime.date.today()

        for report in Report.objects.filter(user=userusing, specific=False, finished__range=(start, end)):
            lastcorrs += report.correct
        
        corrs_conc = ""
        corrsperc = 0
        if lastcorrs < correctwords:
            corrs_conc = "increase"
            if lastcorrs != 0:
                corrsperc = int((correctwords / lastcorrs) * 100) - 100
            else:
                corrsperc = 0
        elif lastcorrs > correctwords:
            corrs_conc = "decrease"
            if lastcorrs != 0:
                corrsperc = 100 - int((correctwords / lastcorrs) * 100)
            else:
                corrsperc = 0
        
        tagcount = []
        for report in Report.objects.filter(user=userusing, specific=False, finished__gt=datetime.date.today()):
            cool = (report.used).split(", ")
            tagcount.extend(cool)
        tagcount = list(dict.fromkeys(tagcount))
        alltags = tagcount
        tagcount = len(tagcount)

        prevtags = []
        start = datetime.date.today() - datetime.timedelta(days = 1)
        end = datetime.date.today()

        for report in Report.objects.filter(user=userusing, specific=False, finished__gt=datetime.date.today()):
            cool = (report.used).split(", ")
            prevtags.extend(cool)
        
        prevtags = list(dict.fromkeys(prevtags))
        prevtags = len(prevtags)
        
        tags_conc = ""
        tagsperc = 0
        if prevtags < tagcount:
            tags_conc = "increase"
            if prevtags != 0:
                tagsperc = int((tagcount / prevtags) * 100) - 100
            else:
                tagsperc = 0
        elif prevtags > tagcount:
            tags_conc = "decrease"
            if prevtags != 0:
                tagsperc = 100 - int((tagcount / prevtags) * 100)
            else:
                tagsperc = 0
        
        tagrep = []
        for tag in alltags:
            reports = Report.objects.filter(user=userusing, specific=True, finished__gt=datetime.date.today(), used=tag)
            correct = 0
            total = 0
            
            for report in reports:
                correct += report.correct
                total += report.total
            
            tagrep.append([{'tag': tag, 'correct': correct, 'total': total, 'percent': int((correct / total) * 100)}])
        
        toppers = sorted(tagrep, key=lambda d: d['percent'])[:5]
        
        if userusing.trigger:
            userusing.trigger = False
            userusing.save()
            return render(request, "spell/dashboard.html", {
                "bar": "",
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "active": "home",
                "trigger": True,
                "totalwords": totalwords,
                "wordsconc": word_conc,
                "wordsperc": wordsperc,
                "correctwords": correctwords,
                "corrsconc": corrs_conc,
                "corrsperc": corrsperc,
                "tagcount": tagcount,
                "tagsconc": tags_conc,
                "tagsperc": tagsperc,
                "tagsrep": tagrep,
                "toppers": toppers
            })
        else:
            return render(request, "spell/dashboard.html", {
                "bar": "",
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "active": "home",
                "totalwords": totalwords,
                "wordsconc": word_conc,
                "wordsperc": wordsperc,
                "correctwords": correctwords,
                "corrsconc": corrs_conc,
                "corrsperc": corrsperc,
                "tagcount": tagcount,
                "tagsconc": tags_conc,
                "tagsperc": tagsperc,
                "tagsrep": tagrep,
                "toppers": toppers
            })
    else:
        return render(request, "spell/dashboard.html", {
            "bar": "",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "home",
            "totalwords": totalwords,
            "wordsconc": word_conc,
            "wordsperc": wordsperc,
            "correctwords": correctwords,
            "corrsconc": corrs_conc,
            "corrsperc": corrsperc,
            "tagcount": tagcount,
            "tagsconc": tags_conc,
            "tagsperc": tagsperc,
            "tagsrep": tagrep,
            "toppers": toppers
        })

# Libraries
@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def word_library(request):
    if request.method == "POST":
        exact = False
        try:
            temp = request.POST["exact"]
            exact = True
        except:
            pass
        
        word = request.POST["word"]
        tag_list = request.POST.getlist('*..*tags*..*')
        which = request.POST["which"]

        if not word == "":
            if exact:
                try:
                    cool = word
                    fun = Word.objects.get(word=cool)
                    results = []
                    results.append(fun)

                    return render(request, "spell/word_library.html", {
                        "bar": "libraries",
                        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                        "active": "coolwords",
                        "tags": Tag.objects.all(),
                        "roots": Root.objects.all(),
                        "results": results
                    })
                except:
                    return render(request, "spell/word_library.html", {
                        "bar": "libraries",
                        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                        "active": "coolwords",
                        "tags": Tag.objects.all(),
                        "roots": Root.objects.all(),
                        "message": True
                    })
            else:
                if len(tag_list) > 0:
                    if which == "ALL":
                        results = []
                        fun = []
                        for id in tag_list:
                            if id == "*..*":
                                fun.append(Word.objects.filter(tagged=False))
                            else:
                                fun.append(Word.objects.filter(word__contains=word, tags__id=int(id)))
                        
                        for i in range(len(fun)):
                            if not i == 0:
                                fun[0] = set(fun[0]).intersection(set(fun[i]))
                        
                        for i in fun[0]:
                            results.append(i)
                        
                        if len(results) > 0:
                            return render(request, "spell/word_library.html", {
                                "bar": "libraries",
                                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                                "active": "coolwords",
                                "tags": Tag.objects.all(),
                                "roots": Root.objects.all(),
                                "results": results
                            })
                        else:
                            return render(request, "spell/word_library.html", {
                                "bar": "libraries",
                                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                                "active": "coolwords",
                                "tags": Tag.objects.all(),
                                "roots": Root.objects.all(),
                                "message": True
                            })
                    else:
                        stuff = []
                        for id in tag_list:
                            if id == "*..*":
                                stuff.append(Word.objects.filter(tagged=False))
                            else:
                                stuff.append(Word.objects.filter(word__contains=word, tags__id=int(id)))
                        
                            results = []
                            for thingy in stuff:
                                for i in thingy:
                                    results.append(i)
                            
                            if len(results) > 0:
                                return render(request, "spell/word_library.html", {
                                    "bar": "libraries",
                                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                                    "active": "coolwords",
                                    "tags": Tag.objects.all(),
                                    "roots": Root.objects.all(),
                                    "results": set(results)
                                })
                            else:
                                return render(request, "spell/word_library.html", {
                                    "bar": "libraries",
                                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                                    "active": "coolwords",
                                    "tags": Tag.objects.all(),
                                    "roots": Root.objects.all(),
                                    "message": True
                                })
                        results = []
                    
                        fun = []
                        for i in tag_list:
                            if not i == "*..*":
                                fun.append(int(i))
                        
                        if "*..*" in tag_list:
                            results.extend(list((Word.objects.filter((Q(tags__id__in=fun) | Q(tagged=False)) & Q(word__contains=word))).distinct()))
                        else:
                            results.extend(list((Word.objects.filter(tags__id__in=fun, word__contains=word)).distinct()))
                        
                        if len(results) > 0:
                            return render(request, "spell/word_library.html", {
                                "bar": "libraries",
                                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                                "active": "coolwords",
                                "tags": Tag.objects.all(),
                                "roots": Root.objects.all(),
                                "results": results
                            })
                        else:
                            return render(request, "spell/word_library.html", {
                                "bar": "libraries",
                                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                                "active": "coolwords",
                                "tags": Tag.objects.all(),
                                "roots": Root.objects.all(),
                                "message": True
                            })
                else:
                    results = Word.objects.filter(word__contains=word)
                    
                    if len(results) > 0:
                        return render(request, "spell/word_library.html", {
                            "bar": "libraries",
                            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                            "active": "coolwords",
                            "tags": Tag.objects.all(),
                            "roots": Root.objects.all(),
                            "results": results
                        })
                    else:
                        return render(request, "spell/word_library.html", {
                            "bar": "libraries",
                            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                            "active": "coolwords",
                            "tags": Tag.objects.all(),
                            "roots": Root.objects.all(),
                            "message": True
                        })
        else:
            if len(tag_list) > 0:
                if which == "ALL":
                    results = []
                    fun = []
                    for id in tag_list:
                        if id == "*..*":
                            fun.append(Word.objects.filter(tagged=False))
                        else:
                            fun.append(Word.objects.filter(tags__id=int(id)))
                    
                    for i in range(len(fun)):
                        if not i == 0:
                            fun[0] = set(fun[0]).intersection(set(fun[i]))
                    
                    for i in fun[0]:
                        results.append(i)
                    
                    if len(results) > 0:
                        return render(request, "spell/word_library.html", {
                            "bar": "libraries",
                            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                            "active": "coolwords",
                            "tags": Tag.objects.all(),
                            "roots": Root.objects.all(),
                            "results": results
                        })
                    else:
                        return render(request, "spell/word_library.html", {
                            "bar": "libraries",
                            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                            "active": "coolwords",
                            "tags": Tag.objects.all(),
                            "roots": Root.objects.all(),
                            "message": True
                        })
                else:
                    results = []
                    
                    fun = []
                    for i in tag_list:
                        if not i == "*..*":
                            fun.append(int(i))
                    
                    if "*..*" in tag_list:
                        results.extend(list((Word.objects.filter(Q(tags__id__in=fun) | Q(tagged=False))).distinct()))
                    else:
                        results.extend(list((Word.objects.filter(tags__id__in=fun)).distinct()))
                    
                    if len(results) > 0:
                        return render(request, "spell/word_library.html", {
                            "bar": "libraries",
                            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                            "active": "coolwords",
                            "tags": Tag.objects.all(),
                            "roots": Root.objects.all(),
                            "results": results
                        })
                    else:
                        return render(request, "spell/word_library.html", {
                            "bar": "libraries",
                            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                            "active": "coolwords",
                            "tags": Tag.objects.all(),
                            "roots": Root.objects.all(),
                            "message": True
                        })
            else:
                results = Word.objects.all()
                
                if len(results) > 0:
                    return render(request, "spell/word_library.html", {
                        "bar": "libraries",
                        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                        "active": "coolwords",
                        "tags": Tag.objects.all(),
                        "roots": Root.objects.all(),
                        "results": results
                    })
                else:
                    return render(request, "spell/word_library.html", {
                        "bar": "libraries",
                        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                        "active": "coolwords",
                        "tags": Tag.objects.all(),
                        "roots": Root.objects.all(),
                        "message": True
                    })
    else:
        return render(request, "spell/word_library.html", {
            "bar": "libraries",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "coolwords",
            "tags": Tag.objects.all(),
            "roots": Root.objects.all()
        })

@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def tag_library(request):
    if request.method == "POST":
        try:
            thing = request.POST["tag"]
            if not (("---" in thing) or ('"' in thing) or ("'" in thing) or ("*..*" in thing) or (", " in thing)):
                new = Tag(name=thing)
                new.save()
                return render(request, "spell/tag_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "taags",
                    "tags": Tag.objects.all()
                })
            else:
                return render(request, "spell/tag_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "taags",
                    "tags": Tag.objects.all(),
                    "error": True
                })
        except:
            thing = request.POST["rentag"]
            if not (("---" in thing) or ('"' in thing) or ("'" in thing) or ("*..*" in thing) or (", " in thing)):
                new = Tag.objects.get(pk=int(request.POST["tagid"]))
                new.name = thing
                new.save()
                return render(request, "spell/tag_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "taags",
                    "tags": Tag.objects.all()
                })
            else:
                return render(request, "spell/tag_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "taags",
                    "tags": Tag.objects.all(),
                    "namerror": int(request.POST["tagid"])
                })
    else:
        return render(request, "spell/tag_library.html", {
            "bar": "libraries",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "taags",
            "tags": Tag.objects.all()
        })

@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def root_library(request):
    if request.method == "POST":
        try:
            thing = request.POST["root"]
            if not (("---" in thing) or ('"' in thing) or ("'" in thing) or ("*..*" in thing) or (", " in thing)):
                new = Root(name=thing)
                new.save()
                return render(request, "spell/root_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "rootslib",
                    "roots": Root.objects.all()
                })
            else:
                return render(request, "spell/root_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "rootslib",
                    "roots": Root.objects.all(),
                    "error": True
                })
        except:
            thing = request.POST["renroot"]
            if not (("---" in thing) or ('"' in thing) or ("'" in thing) or ("*..*" in thing) or (", " in thing)):
                new = Root.objects.get(pk=int(request.POST["rootid"]))
                new.name = thing
                new.save()
                return render(request, "spell/root_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "rootslib",
                    "roots": Root.objects.all()
                })
            else:
                return render(request, "spell/root_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "rootslib",
                    "roots": Root.objects.all(),
                    "namerror": int(request.POST["rootid"])
                })
    else:
        return render(request, "spell/root_library.html", {
            "bar": "libraries",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "rootslib",
            "roots": Root.objects.all()
        })

# Word Changes
@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def update_words(request):
    updates = request.POST["changes"]
    updates = updates.split("|||")
    updates.remove("")

    for update in updates:
        thing = update.split("*..*")
        question = thing[0].split("-")
        id = question[2]
        changer = question[1]
        time = Word.objects.get(pk=int(id))

        if changer == "def1":
            time.definition1 = thing[1]
            time.save()
        elif changer == "def2":
            time.definition2 = thing[1]
            time.save()
        elif changer == "def3":
            time.definition3 = thing[1]
            time.save()
        elif changer == "spec":
            time.speech = thing[1]
            time.save()
        elif changer == "origin1":
            time.origin1 = thing[1]
            time.save()
        elif changer == "origin2":
            time.origin2 = thing[1]
            time.save()
        elif changer == "origin3":
            time.origin3 = thing[1]
            time.save()
        elif changer == "remtag":
            bad = Tag.objects.get(pk=int(thing[1]))
            time.tags.remove(bad)
            if len(time.tags.all()) == 0:
                time.tagged = False
            time.save()
        elif changer == "addroot":
            good = Root.objects.get(pk=int(thing[1]))
            time.roots.add(good)
            time.rooted = True
            time.save()
        elif changer == "remroot":
            good = Root.objects.get(pk=int(thing[1]))
            time.roots.remove(good)
            if len(time.roots.all()) == 0:
                time.rooted = False
            time.save()
        else:
            bad = Tag.objects.get(pk=int(thing[1]))
            time.tags.add(bad)
            time.save()
    
    return HttpResponseRedirect(reverse("word_library"))

# Tag Changes
@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def delete_tag(request, id):
    tag = Tag.objects.get(pk=id)
    tag.delete()
    return HttpResponseRedirect(reverse("tag_library"))

# Root Changes
@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def update_root(request):
    root = Root.objects.get(pk=int(request.POST["id"]))
    
    if request.POST["def"] != "None":
        root.definition = request.POST["def"]
        root.save()
    
    if request.POST["origin"] != "None":
        root.origin = request.POST["origin"]
        root.save()
    
    root.pp = request.POST["presuf"]
    root.save()
    return HttpResponseRedirect(reverse("root_library"))

@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def delete_root(request, id):
    root = Root.objects.get(pk=id)
    root.delete()
    return HttpResponseRedirect(reverse("root_library"))

# Import
@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def word_import(request):
    if request.method == "POST":
        request_id = request.POST["request-id"]

        if request_id == "new-words":
            if exists("spell/static/spell/words.csv"):
                os.remove("spell/static/spell/words.csv")
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
                fields = ['Words']
                
                with open("spell/static/spell/CustomTemplate.csv", 'w', newline="") as csvfile:
                    csvwriter = csv.writer(csvfile) 
                    csvwriter.writerow(fields) 
                    
                    for thingy in nots:
                        rows = [thingy]
                        csvwriter.writerow(rows)

            if len(nots) > 0 and not len(already) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'nots': nots,
                    'message1': "SpellNOW!&trade; was unable to add these words to your list:",
                    "download": True
                })
            elif len(already) > 0 and not len(nots) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'already': already,
                    'message2': "SpellNOW!&trade; found these words already in your list:"
                })
            elif len(already) > 0 and len(nots) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'nots': nots,
                    'already': already,
                    'message1': "SpellNOW!&trade; was unable to add these words to your list:",
                    'message2': "SpellNOW!&trade; found these words already in your list:",
                    "download": True
                })
            else:
                return HttpResponseRedirect(reverse("word_library"))
        elif request_id == "custom-words":
            if exists("spell/static/spell/custom.csv"):
                os.remove("spell/static/spell/custom.csv")
            already = []
            new_word = []
            file = request.FILES["csv"]
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
            if len(already) > 0:
                return render(request, "spell/custom.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'words': new_word,
                    'already': already,
                    "error": True,
                    'message2': "SpellNOW!&trade; found these words already in your list:",
                })
            else:
                return render(request, "spell/custom.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'words': new_word,
                })
        elif request_id == "del-words":
            if exists("spell/static/spell/delete-words.csv"):
                os.remove("spell/static/spell/delete-words.csv")
            nots = []
            file = request.FILES["csv"]
            fs = FileSystemStorage()
            fs.save("spell/static/spell/delete-words.csv", file)
            f = open("spell/static/spell/delete-words.csv", "r")
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                final = row[0].lower()
                
                if not Word.objects.filter(word=final):
                    nots.append(final)
                else:
                    word = Word.objects.get(word=final)
                    word.delete()

                    if exists("spell/static/spell/sounds/" + final + ".mp3"):
                        os.remove("spell/static/spell/sounds/" + final + ".mp3")
            f.close()
            os.remove("spell/static/spell/delete-words.csv")

            if len(nots) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'nots': nots,
                    "message1": "SpellNOW!&trade; was unable to delete these words because they do not exist:"
                })
            else:
                return HttpResponseRedirect(reverse("word_library"))
        elif "add-tag" in request_id:
            if exists("spell/static/spell/insert-tags.csv"):
                os.remove("spell/static/spell/insert-tags.csv")
            nots = []
            already = []
            file = request.FILES["csv"]
            fs = FileSystemStorage()
            fs.save("spell/static/spell/insert-tags.csv", file)
            f = open("spell/static/spell/insert-tags.csv", "r")
            reader = csv.reader(f)
            next(reader)
            tag = Tag.objects.get(pk=(request_id.split("-"))[2])
            for row in reader:
                final = row[0].lower()
                
                if Word.objects.filter(word=final, tags__in=[tag]):
                    already.append(final)
                if not Word.objects.filter(word=final):
                    nots.append(final)
                else:
                    word = Word.objects.get(word=final)
                    word.tags.add(tag)
                    word.tagged = True
                    word.save()
            f.close()
            os.remove("spell/static/spell/insert-tags.csv")

            if len(nots) > 0:
                fields = ['Words']
                    
                # writing to csv file 
                with open("spell/static/spell/CustomTemplate.csv", 'w', newline="") as csvfile:
                    csvwriter = csv.writer(csvfile) 
                    csvwriter.writerow(fields)
                    
                    for thingy in nots:
                        rows = [thingy]
                        csvwriter.writerow(rows)

            if len(nots) > 0 and len(already) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'already': already,
                    'nots': nots,
                    "message1": "SpellNOW!&trade; was unable to tag these words because they do not exist:",
                    "message2": "SpellNOW!&trade; was unable to tag these words because they are already tagged:",
                    "download": True
                })
            elif len(nots) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'nots': nots,
                    "message1": "SpellNOW!&trade; was unable to tag these words because they do not exist:",
                    "download": True
                })
            elif len(already) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'already': already,
                    "message2": "SpellNOW!&trade; was unable to tag these words because they are already tagged:",
                })
            else:
                return HttpResponseRedirect(reverse("tag_library"))
        elif "del-tag" in request_id:
            if exists("spell/static/spell/delete-tags.csv"):
                os.remove("spell/static/spell/delete-tags.csv")
            nots = []
            file = request.FILES["csv"]
            fs = FileSystemStorage()
            fs.save("spell/static/spell/delete-tags.csv", file)
            f = open("spell/static/spell/delete-tags.csv", "r")
            reader = csv.reader(f)
            next(reader)
            tag = Tag.objects.get(pk=(request_id.split("-"))[2])
            for row in reader:
                final = row[0].lower()
                
                if not Word.objects.filter(word=final, tags__in=[tag]):
                    nots.append(final)
                else:
                    word = Word.objects.get(word=final)
                    word.tags.remove(tag)
                    word.save()
                    if len(word.tags.all()) == 0:
                        word.tagged = False
                        word.save()
            f.close()
            os.remove("spell/static/spell/delete-tags.csv")

            if len(nots) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'nots': nots,
                    "message1": "SpellNOW!&trade; was unable to untag these words because they are not tagged:",
                })
            else:
                return HttpResponseRedirect(reverse("tag_library"))
        elif "add-root" in request_id:
            if exists("spell/static/spell/add-roots.csv"):
                os.remove("spell/static/spell/add-roots.csv")
            nots = []
            already = []
            file = request.FILES["csv"]
            fs = FileSystemStorage()
            fs.save("spell/static/spell/add-roots.csv", file)
            f = open("spell/static/spell/add-roots.csv", "r")
            reader = csv.reader(f)
            next(reader)
            roots = Root.objects.get(pk=(request_id.split("-"))[2])
            for row in reader:
                final = row[0].lower()
                
                if Word.objects.filter(word=final, roots__in=[roots]):
                    already.append(final)
                if not Word.objects.filter(word=final):
                    nots.append(final)
                else:
                    word = Word.objects.get(word=final)
                    word.roots.add(roots)
                    word.rooted = True
                    word.save()
            f.close()
            os.remove("spell/static/spell/add-roots.csv")

            if len(nots) > 0:
                fields = ['Words']
                    
                # writing to csv file
                with open("spell/static/spell/CustomTemplate.csv", 'w', newline="") as csvfile:
                    csvwriter = csv.writer(csvfile) 
                    csvwriter.writerow(fields)
                    
                    for thingy in nots:
                        rows = [thingy]
                        csvwriter.writerow(rows)

            if len(nots) > 0 and len(already) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'already': already,
                    'nots': nots,
                    "message1": "SpellNOW!&trade; was unable to add a root to these words because they do not exist:",
                    "message2": "SpellNOW!&trade; was unable to add a root to these words because they have already been added under the respective root:",
                    "download": True
                })
            elif len(nots) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'nots': nots,
                    "message1": "SpellNOW!&trade; was unable to add a root to these words because they do not exist:",
                    "download": True
                })
            elif len(already) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'already': already,
                    "message2": "SpellNOW!&trade; was unable to add a root to these words because they have already been added under the respective root:",
                })
            else:
                return HttpResponseRedirect(reverse("root_library"))
        elif "del-root" in request_id:
            if exists("spell/static/spell/del-roots.csv"):
                os.remove("spell/static/spell/del-roots.csv")
            nots = []
            file = request.FILES["csv"]
            fs = FileSystemStorage()
            fs.save("spell/static/spell/del-roots.csv", file)
            f = open("spell/static/spell/del-roots.csv", "r")
            reader = csv.reader(f)
            next(reader)
            root = Root.objects.get(pk=(request_id.split("-"))[2])
            for row in reader:
                final = row[0].lower()
                
                if not Word.objects.filter(word=final, roots__in=[root]):
                    nots.append(final)
                else:
                    word = Word.objects.get(word=final)
                    word.roots.remove(root)
                    if len(word.roots.all()) == 0:
                        word.rooted = False
                    word.save()
            
            f.close()
            os.remove("spell/static/spell/del-roots.csv")

            if len(nots) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'nots': nots,
                    "message1": "SpellNOW!&trade; was unable to add a root to these words because they have not been added under the respective root:",
                })
            else:
                return HttpResponseRedirect(reverse("root_library"))
    else:
        return render(request, "spell/import.html", {
            "bar": "libraries",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "import",
            "tags": Tag.objects.all(),
            "roots": Root.objects.all()
        })

@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
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
            new_speech = request.POST["speech-"+final]
            new_origin = request.POST["origin-"+final]
            new_def = request.POST["origin-"+final]

            new = Word(word=new_word, speech = new_speech, origin1 = new_origin, origin2 = None, origin3 = None, definition1 = new_def, definition2 = None, definition3 = None, pronounce = ("*--*" + new_word), tagged=False)
            new.save()
    
    return HttpResponseRedirect(reverse("word_library"))

# Activities

# Spelling
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def start(request):
    return render(request, "spell/spelling_start.html", {
        "bar": "activities",
        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
        "active": "spellit",
        "tags": Tag.objects.all(),
        "roots": Root.objects.all(),
        "number": len(Word.objects.all())
    })

@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def spell(request):
    if request.method == "POST":
        tags = request.POST.getlist('*..*tags*..*')
        roots = request.POST.getlist('*..*root*..*')
        fullcall = []
        fullcall.extend(tags)
        fullcall.extend(roots)

        print("========================Verifying word amount========================")
        results = []
        fun = []
        for i in tags:
            if not i == "*..*":
                fun.append(i)
        
        cool = []
        for i in roots:
            if not i == "*..*":
                cool.append(i)

        if "*..*" in tags and "*..*" in roots:
            results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(tagged=False) | Q(roots__name__in=cool) | Q(rooted=False))).distinct()))
        elif "*..*" in tags:
            results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(tagged=False) )).distinct()))
        elif "*..*" in roots:
            results.extend(list((Word.objects.filter(Q(roots__name__in=cool) | Q(rooted=False) )).distinct()))
        else:
            results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(roots__name__in=cool))).distinct()))
        
        if (int(len(results)) < int(request.POST["numwords"])) or (int(len(tags)) > int(request.POST["numwords"])):
            return render(request, "spell/spelling_start.html", {
                "bar": "activities",
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "active": "spellit",
                "tags": Tag.objects.all(),
                "roots": Root.objects.all(),
                "number": len(Word.objects.all()),
                "message": "Invalid word count, the maximum number of words you may have under this configuration is " + str(int(len(results))),
            })
        else:
            fines = []
            allspeechs = []
            alldefs = ""
            allorigins = ""
            allprons = ""
            order = ""
            final_last_total = 0
            final_tags = ""
            final_roots = ""
            hllg = []
            ids_used = ""
            rightio = ""
            wrongio = ""

            for cooolio in Tag.objects.all():
                rightio += cooolio.name + "*..*"
            
            for cooolio in Root.objects.all():
                wrongio += cooolio.name + "*..*"

            print("========================Choosing Words========================")
            lengths = []
            didi = []
            results = []
            jeff = 0
            for ite in fullcall:
                if ite == "*..*":
                    didi.append(list(Word.objects.filter(tagged=False).exclude(id__in = results).values_list('pk', flat=True)))
                    results.extend(list(Word.objects.filter(tagged=False).exclude(id__in = results).values_list('pk', flat=True)))
                    use = len(didi[jeff])
                    lengths.append(use)
                elif ite == "|--|*..*":
                    didi.append(list(Word.objects.filter(rooted=False).exclude(id__in = results).values_list('pk', flat=True)))
                    results.extend(list(Word.objects.filter(rooted=False).exclude(id__in = results).values_list('pk', flat=True)))
                    use = len(didi[jeff])
                    lengths.append(use)
                elif "|--|" in ite:
                    didi.append(list(Word.objects.filter(roots__name=ite.replace("|--|", "")).exclude(id__in = results).values_list('pk', flat=True)))
                    results.extend(list(Word.objects.filter(roots__name=ite.replace("|--|", "")).exclude(id__in = results).values_list('pk', flat=True)))
                    use = len(didi[jeff])
                    lengths.append(use)
                else:
                    didi.append(list(Word.objects.filter(tags__name=ite).exclude(id__in = results).values_list('pk', flat=True)))
                    results.extend(list((Word.objects.filter(tags__name=ite).exclude(id__in = results)).values_list('pk', flat=True)))
                    use = len(didi[jeff])
                    lengths.append(use)
                
                jeff += 1
            
            globalmin = int(int(request.POST["numwords"])/int(len(lengths)))
            last = int(request.POST["numwords"]) - (globalmin * (int(len(lengths)) - 1))
            better = []
            surplus = []

            for i in range(int(len(lengths))):
                if i == int(len(lengths)) - 1:
                    if lengths[i] < last:
                        surplus.append(lengths[i] - last)
                        better.append(lengths[i])
                    elif lengths[i] == last:
                        surplus.append(0)
                        better.append(lengths[i])
                    else:
                        surplus.append(lengths[i] - last)
                        better.append(last)
                else:
                    if lengths[i] < globalmin:
                        surplus.append(lengths[i] - globalmin)
                        better.append(lengths[i])
                    elif lengths[i] == globalmin:
                        surplus.append(0)
                        better.append(lengths[i])
                    else:
                        surplus.append(lengths[i] - globalmin)
                        better.append(globalmin)
            
            for i in range(int(len(lengths))):
                if surplus[i] < 0:
                    j = 0
                    k = 0
                    while j < surplus[i] * -1:
                        if surplus[k % int(len(lengths))] > 0:
                            better[k % int(len(lengths))] += 1
                            surplus[k % int(len(lengths))] -= 1
                            j += 1
                        k += 1
            
            for i in range(len(didi)):
                random.shuffle(didi[i])
                didi[i] = didi[i][:better[i]]

            i = 0
            print("========================Getting Words========================")
            for lemmon in range(int(len(better))):
                for pkg in didi[lemmon]:
                    word = Word.objects.get(pk=pkg)

                    order += (fullcall[lemmon] + ", ")
                    
                    if not fullcall[lemmon] in hllg:
                        hllg.append(fullcall[lemmon])
                        ids_used += (fullcall[lemmon] + ", ")

                    fines.append(word.word)

                    allspeechs.append(word.speech)

                    ori1 = word.origin1 if not word.origin1 == None else "-||-"
                    ori2 = word.origin2 if not word.origin2 == None else "-||-"
                    ori3 = word.origin2 if not word.origin3 == None else "-||-"

                    allorigins += (ori1 + '--++--' + ori2 + '--++--' + ori3 + "|=[]=|")

                    def1 = word.definition1 if not word.definition1 == None else "-||-"
                    def2 = word.definition2 if not word.definition2 == None else "-||-"
                    def3 = word.definition3 if not word.definition3 == None else "-||-"

                    alldefs += (def1 + '--++--' + def2 + '--++--' + def3 + "|=[]=|")

                    if (i + 1) == int(request.POST["numwords"]):
                        allprons += word.pronounce
                    else:
                        allprons += (word.pronounce + " || ")
                    
                    final_last_total += 1
                    print("Got word " + str(final_last_total) + " of " + request.POST["numwords"])
                            
                    usage = word.tags.all()

                    badder = 0
                    for bad in usage:
                        if badder == (len(usage) - 1):
                            final_tags += bad.name
                        else:
                            final_tags += (bad.name + "<>")
                        badder += 1
                        
                    if not final_last_total == int(request.POST["numwords"]):
                        final_tags += "><"
                    
                    usage = word.roots.all()

                    badder = 0
                    for bad in usage:
                        if badder == (len(usage) - 1):
                            final_roots += bad.name
                        else:
                            final_roots += (bad.name + "<>")
                        badder += 1
                        
                    if not final_last_total == int(request.POST["numwords"]):
                        final_roots += "><"
                    
                    i += 1
            
            return render(request, "spell/spelling_spell.html", {
                "bar": "activities",
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "active": "spellit",
                "words": fines,
                "speech": allspeechs,
                "origin": allorigins,
                "definition": alldefs,
                "prons": allprons,
                "tags": Tag.objects.all(),
                "roots": Root.objects.all(),
                "order": order,
                "final_tags": final_tags,
                "ids_used": ids_used,
                "alltags": rightio,
                "final_roots": final_roots,
                "allroots": wrongio,
            })

@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def finish(request):
    if request.user.is_staff:
        tags_rep = request.POST["new_tags"]
        tags = tags_rep.split("[]")
        tags.remove("")
        
        words_rep = request.POST["add_words"]
        added_words = words_rep.split("[]")
        added_words.remove("")

        words_pep = request.POST["add_words_roots"]
        added_roots = words_pep.split("[]")
        added_roots.remove("")

        for tag in tags:
            new = Tag(name=tag)
            new.save()
        
        for word in added_words:
            cool = word.split("||")
            if (cool[0][0] + cool[0][1] + cool[0][2]) == "---":
                bad = Tag.objects.get(name=(cool[0].replace("---", "")))
                word = Word.objects.get(word=cool[1])
                word.tags.remove(bad)
                word.save()
                if len(word.tags.all()) == 0:
                    word.tagged = False
                    word.save()
            else:
                bad = Tag.objects.get(name=(cool[0].replace("---", "")))
                word = Word.objects.get(word=cool[1])
                word.tags.add(bad)
                word.tagged = True
                word.save()
        
        for word in added_roots:
            cool = word.split("||")
            if (cool[0][0] + cool[0][1] + cool[0][2]) == "---":
                bad = Root.objects.get(name=(cool[0].replace("---", "")))
                word = Word.objects.get(word=cool[1])
                word.roots.remove(bad)
                word.save()
                if len(word.roots.all()) == 0:
                    word.rooted = False
                    word.save()
            else:
                bad = Root.objects.get(name=(cool[0].replace("---", "")))
                word = Word.objects.get(word=cool[1])
                word.roots.add(bad)
                word.rooted = True
                word.save()

    order_in = request.POST["order"]
    order = order_in.split(", ")
    order.remove("")

    ids_used = request.POST["ids_used"]
    total_gags = ids_used.split(", ")
    total_gags.remove("")

    corrs = request.POST["correct_array"]
    correct_array = corrs.split(", ")
    correct_array.remove("")

    glob = request.POST["words"]
    words = glob.split(", ")
    words.remove("")

    dumb = request.POST["attempts"]
    atts = dumb.split(", ")
    atts.remove("")

    timings = request.POST["time"]
    time = timings.split(", ")
    time.remove("")

    cool = 0
    id_using = 0
    thingy = (request.POST["score"]).split("/")
    userusing = Account.objects.get(username=request.user.username)
    new = Report(used=ids_used, correct=thingy[0], total=(thingy[1]), percent=(int((int(thingy[0])/int(thingy[1]))*100)), specific=False, user=userusing)
    new.save()
    id_using = new.id

    wilk = []
    for ite in total_gags:
        if ite == "*..*":
            nice = 0
            cool = 0
            abhi = 0
            for ishaan in order:
                if ishaan == ite:
                    nice += int(correct_array[cool])
                    abhi += 1
                cool += 1
            
            if abhi != 0:
                new = Report(used="Untagged", correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing)
                new.save()
                wilk.append("Untagged")
        elif ite == "|--|*..*":
            nice = 0
            cool = 0
            abhi = 0
            for ishaan in order:
                if ishaan == ite:
                    nice += int(correct_array[cool])
                    abhi += 1
                cool += 1
            
            if abhi != 0:
                new = Report(used="No Roots", correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing)
                new.save()
                wilk.append("No Roots")
        elif "|--|" in ite:
            nice = 0
            cool = 0
            abhi = 0
            for ishaan in order:
                if ishaan == ite:
                    nice += int(correct_array[cool])
                    abhi += 1
                cool += 1
            
            if abhi != 0:
                new = Report(used=("Root - " + ite.replace("|--|", "")), correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing)
                new.save()
                wilk.append(("Root - " + ite.replace("|--|", "")))
        else:
            nice = 0
            cool = 0
            abhi = 0
            for ishaan in order:
                if ishaan == ite:
                    nice += int(correct_array[cool])
                    abhi += 1
                cool += 1
            
            if abhi != 0:
                new = Report(used=("Tag - " + ite), correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing)
                new.save()
                wilk.append(("Tag - " + ite))
    
    for ite in order:
        if ite == "*..*":
            wilk.append("Untagged")
        elif ite == "|--|*..*":
            wilk.append("No Roots")
        elif "|--|" in ite:
            wilk.append(("Root - " + ite.replace("|--|", "")))
        else:
            wilk.append(("Tag - " + ite))
        
    count = 1

    for tmp in words:
        if int(correct_array[count - 1]) == 0:
            roger = count
            detail = ReportDetail(count=roger, identification=wilk[count - 1], word=tmp, attempt=atts[count - 1], result="INCORRECT", time=time[count - 1], iid=id_using)
            detail.save()
        else:
            roger = count
            detail = ReportDetail(count=roger, identification=wilk[count - 1], word=tmp, attempt=atts[count - 1], result="CORRECT", time=time[count - 1], iid=id_using)
            detail.save()
        count += 1
    
    msg = MIMEMultipart()
    msg['Subject'] = 'Official SpellNOW! Notification! -- New Report'
    msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
    msg["To"] = request.user.email
    body_text = """Hello!\n\nThis is an Official SpellNOW! Notification. You have complete a spelling activity on SpellNOW! with a score of """ + request.POST["score"] + """. Thank you, and we hope for your continued progress for the future.\n\nSincerely,\nSpellNOW! Support Team"""

    body_part = MIMEText(body_text, 'plain')
    msg.attach(body_part)
    with smtplib.SMTP(host="smtp.ionos.com", port=587) as smtp_obj:
        smtp_obj.ehlo()
        smtp_obj.starttls()
        smtp_obj.ehlo()
        smtp_obj.login("support@spellnow.org", "3BGV6@7*X-2Yi/e")
        smtp_obj.sendmail(msg['From'], [msg['To'],], msg.as_string())
    
    return render(request, "spell/spelling_finish.html", {
        "bar": "activities",
        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
        "active": "spellit",
        "score": request.POST["score"]
    })

# Reports
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def reports(request):
    return render(request, "spell/reports.html", {
        "bar": "",
        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
        "active": "reports",
        "reports": Report.objects.filter(specific=False, user=request.user).order_by('-finished')
    })

@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def report(request, id):
    userusing = Account.objects.get(username=request.user.username)
    if len(Report.objects.filter(pk=id, specific=False, user=userusing)) != 0:
        used = Report.objects.filter(iid=id, specific=True)
        fnu = Report.objects.get(pk=id)
        bring = ReportDetail.objects.filter(iid=id)

        return render(request, "spell/report.html", {
            "bar": "",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "reports",
            "used": used,
            "title": fnu.finished,
            "correct": fnu.correct,
            "total": fnu.total,
            "percent": fnu.percent,
            "records": bring,
        })
    else:
        return render(request, "spell/error_404.html", {})

# Profile

@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def profile(request):
    return render(request, "spell/profile.html", {
        "bar": "",
        "active": "profilit",
        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
    })

@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def changedetails(request):
    userusing = Account.objects.get(username=request.user.username)
    userproblems = False

    total = ""

    if userusing.first_name != request.POST["fname"]:
        total += "First Name: " + userusing.first_name + " -> " + request.POST["fname"] + "\n"
    
    if userusing.last_name != request.POST["lname"]:
        total += "Last Name: " + userusing.last_name + " -> " + request.POST["lname"] + "\n"
    
    if (userusing.username != request.POST["username"]) and len(Account.objects.filter(username=request.POST["username"])) == 0:
        total += "Username: " + userusing.username + " -> " + request.POST["username"] + "\n"
        userusing.username = request.POST["username"]
    elif (userusing.username != request.POST["username"]):
        userproblems = True
    
    userusing.first_name = request.POST["fname"]
    userusing.last_name = request.POST["lname"]
    userusing.save()

    if total != "" and userusing.changenotifs:
        msg = MIMEMultipart()
        msg['Subject'] = 'Official SpellNOW! Notification! -- Changes Made to Your Account'
        msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
        msg["To"] = userusing.email
        body_text = """Hello!\n\nThis is an official SpellNOW! Notification. The following email is to inform you as to the recent change(s) made to your SpellNOW! account.\n\n""" + total + """\n\nThank you, and we hope you enjoy your continued use of SpellNOW!\n\nSincerely,\nSpellNOW! Support Team"""

        body_part = MIMEText(body_text, 'plain')
        msg.attach(body_part)
        with smtplib.SMTP(host="smtp.ionos.com", port=587) as smtp_obj:
            smtp_obj.ehlo()
            smtp_obj.starttls()
            smtp_obj.ehlo()
            smtp_obj.login("support@spellnow.org", "3BGV6@7*X-2Yi/e")
            smtp_obj.sendmail(msg['From'], [msg['To'],], msg.as_string())

    if userusing.email != request.POST["email"]:
        it1 = random.randint(10000, 99999)
        it2 = random.randint(10000, 99999)
        late = EmailValidate(userid=request.user.id, email=request.POST["email"], lock1=it1, lock2=it2)
        late.save()
        
        try:
            msg = MIMEMultipart()
            msg['Subject'] = 'Official SpellNOW! Notification! -- Validate Email'
            msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
            msg["To"] = request.POST["email"]
            body_text = """Hello!\n\nThis is an official SpellNOW! Notification. You have recently requested to change the email address associated with your SpellNOW! account. As per SpellNOW! policy you must click the link below to validate your email address.\n\nhttps://spellnow.org/validatemail/""" + str(request.user.id) + """-""" + str(it1) + """-""" + str(it2) + """\n\nThank you, and we hope you enjoy your continued use of SpellNOW!\n\nSincerely,\nSpellNOW! Support Team"""
            body_part = MIMEText(body_text, 'plain')
            msg.attach(body_part)
            with smtplib.SMTP(host="smtp.ionos.com", port=587) as smtp_obj:
                smtp_obj.ehlo()
                smtp_obj.starttls()
                smtp_obj.ehlo()
                smtp_obj.login("support@spellnow.org", "3BGV6@7*X-2Yi/e")
                smtp_obj.sendmail(msg['From'], [msg['To'],], msg.as_string())
        except:
            pass
        
        return HttpResponseRedirect(reverse("informvalidation"))

    if userproblems:
        return render(request, "spell/profile.html", {
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "problems": True,
            "bandit": request.POST["username"],
            "bar": "",
            "active": "profilit",
        })
    else:
        return HttpResponseRedirect(reverse("profile"))

@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def changenotifs(request):
    userusing = Account.objects.get(username=request.user.username)
    prev = userusing.changenotifs

    total = ""

    try:
        cool = request.POST["changenotifs"]
        if cool == "checked":
            if userusing.changenotifs == False:
                total += "Email Notifications: On"
                userusing.changenotifs = True
    except:
        if userusing.changenotifs == True:
            total += "Email Notifications: Off"
            userusing.changenotifs = False

    try:
        cool = request.POST["newsletter"]
        if cool == "checked":
            if userusing.newsletter == False:
                total += "SpellNOW! Newsletter Subscription: On"
                userusing.newsletter = True
    except:
        if userusing.newsletter == True:
                total += "SpellNOW! Newsletter Subscription: Off"
                userusing.newsletter = False

    userusing.save()

    if total != "" and prev:
        msg = MIMEMultipart()
        msg['Subject'] = 'Official SpellNOW! Notification! -- Changes Made to Your Account'
        msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
        msg["To"] = userusing.email
        body_text = """Hello!\n\nThis is an official SpellNOW! Notification. The following email is to inform you as to the recent change(s) made to your SpellNOW! account.\n\n""" + total + """\n\nThank you, and we hope you enjoy your continued use of SpellNOW!\n\nSincerely,\nSpellNOW! Support Team"""

        body_part = MIMEText(body_text, 'plain')
        msg.attach(body_part)
        with smtplib.SMTP(host="smtp.ionos.com", port=587) as smtp_obj:
            smtp_obj.ehlo()
            smtp_obj.starttls()
            smtp_obj.ehlo()
            smtp_obj.login("support@spellnow.org", "3BGV6@7*X-2Yi/e")
            smtp_obj.sendmail(msg['From'], [msg['To'],], msg.as_string())

    return HttpResponseRedirect(reverse("profile"))

@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def changepassword(request):
    user = authenticate(request, username=request.user.username, password=request.POST["current"])
    if user is not None:
        if request.POST["new"] == request.POST["fun"]:
            request.user.set_password(request.POST["new"])
            request.user.save()

            msg = MIMEMultipart()
            msg['Subject'] = 'Official SpellNOW! Notification! -- Changes Made to Your Account'
            msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
            msg["To"] = request.user.email
            body_text = """Hello!\n\nThis is an official SpellNOW! Notification. The following email is to inform you that the password associated with your SpellNOW! account has been recently changed. As per SpellNOW! policy, we are required to inform you of a change in password to your account. If you did not change your SpellNOW! password, please contact SpellNOW! imediately in order to protect the integrity of SpellNOW! content. As per SpellNOW! policy, we ask that you not provide personal details when contacting SpellNOW!, rather specify only your username and phone number.\n\nThank you, and we hope you enjoy your continued use of SpellNOW!\n\nSincerely,\nSpellNOW! Support Team"""

            body_part = MIMEText(body_text, 'plain')
            msg.attach(body_part)
            with smtplib.SMTP(host="smtp.ionos.com", port=587) as smtp_obj:
                smtp_obj.ehlo()
                smtp_obj.starttls()
                smtp_obj.ehlo()
                smtp_obj.login("support@spellnow.org", "3BGV6@7*X-2Yi/e")
                smtp_obj.sendmail(msg['From'], [msg['To'],], msg.as_string())
            
            return HttpResponseRedirect(reverse("profile"))
        else:
            return render(request, "spell/profile.html", {
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "combucer": True,
                "rentry": True,
                "bar": "",
                "active": "profilit",
            })
    else:
        return render(request, "spell/profile.html", {
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "combucer": True,
            "grepper": True,
            "bar": "",
            "active": "profilit",
        })

@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def informvalidation(request):
    if EmailValidate.objects.filter(userid=request.user.id):
        return render(request, "spell/inform.html", {})
    else:
        return render(request, "spell/error_404.html", {})

@login_required(login_url='/login')
def validatemail(request, userit, lockit1, lockit2):
    idofuser=userit
    lock1=lockit1
    lock2=lockit2

    try:
        valid = EmailValidate.objects.get(userid=idofuser, lock1=lock1, lock2=lock2)
        userusing = Account.objects.get(pk=idofuser)

        if userusing.changenotifs:
            msg = MIMEMultipart()
            msg['Subject'] = 'Official SpellNOW! Notification! -- Changes Made to Your Account'
            msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
            msg["To"] = valid.email
            body_text = """Hello!\n\nThis is an official SpellNOW! Notification. The following email is to inform you as to the recent change(s) made to your SpellNOW! account.\n\n""" + "Email: " + userusing.username + " -> " + valid.email + """\n\nThank you, and we hope you enjoy your continued use of SpellNOW!\n\nSincerely,\nSpellNOW! Support Team"""

            body_part = MIMEText(body_text, 'plain')
            msg.attach(body_part)
            with smtplib.SMTP(host="smtp.ionos.com", port=587) as smtp_obj:
                smtp_obj.ehlo()
                smtp_obj.starttls()
                smtp_obj.ehlo()
                smtp_obj.login("support@spellnow.org", "3BGV6@7*X-2Yi/e")
                smtp_obj.sendmail(msg['From'], [msg['To'],], msg.as_string())

        userusing.email = valid.email
        userusing.save()
        valid.delete()
        return HttpResponseRedirect(reverse("profile"))
    except:
        return render(request, "spell/error_404.html", {})

# Subscribe

@login_required(login_url='/login')
def subscribe(request):
    if not request.user.is_superuser:
        userusing = Account.objects.get(username=request.user.username)
        if userusing.locked == True:
            return render(request, "spell/subscribe.html", {})
        else:
            return render(request, "spell/error_404.html", {})
    else:
        return render(request, "spell/error_404.html", {})

@login_required(login_url='/login')
def payment(request, sessionid):
    stripe.api_key = 'sk_test_51LQUbqGjGQJlNWoiV9Y3tyReZKx8VQtVSGpOOdCiRKk9O69AQvtxRN4Lzu8z5a1MrkMLSYbTWVAKH7UBuywsAlw0009eisFzdi'
    try:
        session = stripe.checkout.Session.retrieve(sessionid)
        userusing = Account.objects.get(username=request.user.username)
        userusing.subscribed = True
        userusing.locked = False
        userusing.trigger = True
        userusing.save()
    except:
        return render(request, "spell/error_404.html", {})
    
    return HttpResponseRedirect(reverse("admin_panel"))