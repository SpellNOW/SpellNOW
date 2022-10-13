from importlib.metadata import distribution
from operator import ilshift
from re import L
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count
from .models import Account, Word, Tag, Report, Root, ReportDetail, EmailValidate, ConfirmReq, VocabReportDetail
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
from bs4 import BeautifulSoup
import re

languages = ["Middle English","Latin", "French","German","Italian", "Greek", "Spanish", "Hebrew"]

def merriamweb_scrape(word_to_scrape):
    my_word = re.sub(r"[^a-zA-Z]","", word_to_scrape)
    URL = "https://www.merriam-webster.com/dictionary/" + my_word
    page = requests.get(URL)
    data = []
    
    if page.status_code != 200:
        data.append(my_word)
        data.append("WORD NOT FOUND")
        return -1
    soup = BeautifulSoup(page.content, "html.parser")
    #Search for word
    try:
        words = soup.find_all("h1", class_="hword")
        if len(words) <= 0:
            data.append(my_word)
            data.append("WORD NOT FOUND")
            return -1
        i = 0
        for word in words:
            word_element = word.get_text()
            data.append(word_element)
            i = i + 1
            if i == 1:
                break
    except:
        data.append(my_word)
        data.append("WORD NOT FOUND")
        return -1

    try:
        i = 0
        meanings = soup.find_all("span", class_="dtText")
        for meaning in meanings:
            deftext = meaning.get_text()
            data.append(deftext)
            i = i + 1
            if i == 3:
                break
        if i == 1:
            data.append("")
            data.append("")

        if i == 2:
            data.append("")
    except:
        data.append("")
        data.append("")
        data.append("")

    try:
        i = 0
        poss = soup.find_all("a", class_="important-blue-link")
        for pos in poss:
            postext = pos.get_text()
            data.append(postext)
            i = i + 1
            if i == 1:
                break
    except:
        data.append("")

    try:
        i = 0
        add_count = 0
        loos = soup.find_all("p", class_="et")
        for loo_ele in loos:
            los_text = loo_ele.get_text()
            i = i + 1
            if i == 3:
                break
            for x in range(len(languages)):
               position=los_text.find(languages[x])
               if position >= 0:
                   add_count += 1
                   if add_count <=3 :
                      data.append(languages[x])
        if add_count == 0:
            data.append("")
            data.append("")
            data.append("")
        if add_count == 1:
            data.append("")
            data.append("")
        if add_count == 2:
            data.append("")
    except:
        data.append("")
        data.append("")
        data.append("")

    try:
        i = 0
        sound_files = soup.find_all("span", class_="pr")
        for sound_file in sound_files:
            title_element = sound_file.get_text()
            data.append(title_element)
            i = i + 1
            if i == 1:
                break
    except:
        data.append("")

    with open('wordsscraped.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)
    return 1



def dictionarydotcom_scrape(word_to_scrape):
    my_word = re.sub(r"[^a-zA-Z]","", word_to_scrape)

    URL = "https://www.dictionary.com/browse/" + my_word
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="base-pw")
    data = []
 
    #Search for word
    try:
        words = results.find_all("div", class_="css-jv03sw e1wg9v5m6")
        if len(words) <= 0:
            data.append(my_word)
            data.append("WORD NOT FOUND")
            return -1
        i = 0
        for word in words:
            word_element = word.find("h1", class_="css-1sprl0b e1wg9v5m5")
            data.append(word_element.text.strip())
            i = i + 1
            if i == 1:
                break
    except:
        data.append(my_word)
        data.append("WORD NOT FOUND")
        return -1
    #search for sound file link if no sound abort
    link_url = ""
    try:
        i = 0
        sound_files = results.find_all("div", class_="audio-wrapper")
        for sound_file in sound_files:
            title_element = sound_file.find("source", type="audio/mpeg")
            link_url = title_element["src"]
            i = i + 1
            if i == 1:
                break
    except:
        link_url = ""

    if link_url == "":
        data.append("WORD NOT FOUND")
        return -1   #Dont write to csv file
    
    try:
        i = 0
        meanings = results.find_all("div", class_="css-10ul8x e1q3nk1v2")
        for meaning in meanings:
            def_element = meaning.find("span", class_="one-click-content css-nnyc96 e1q3nk1v1")
            data.append(def_element.text.strip())
            i = i + 1
            if i == 3:
                break
        if i == 1:
            data.append("")
            data.append("")

        if i == 2:
            data.append("")
    except:
        data.append("")
        data.append("")
        data.append("")

    try:
        i = 0
        poss = results.find_all("div", class_="css-69s207 e1hk9ate3")
        for pos in poss:
            pos_element = pos.find("span", class_="luna-pos")
            data.append(pos_element.text.strip())
            i = i + 1
            if i == 1:
                break
    except:
        data.append("")

    try:
        i = 0
        add_count = 0
        loos = results.find_all("div", class_="one-click-content css-omho54 e16svm7n0")
        for loo_ele in loos:
            los_text = loo_ele.text
            i = i + 1
            if i == 3:
                break
            for x in range(len(languages)):
               position=los_text.find(languages[x])
               if position >= 0:
                   add_count += 1
                   if add_count <=3 :
                      data.append(languages[x])
        if add_count == 0:
            data.append("")
            data.append("")
            data.append("")
        if add_count == 1:
            data.append("")
            data.append("")
        if add_count == 2:
            data.append("")
    except:
        data.append("")
        data.append("")
        data.append("")
    
    try:
        i = 0
        sound_files = results.find_all("div", class_="audio-wrapper")
        for sound_file in sound_files:
            title_element = sound_file.find("source", type="audio/mpeg")
            link_url = title_element["src"]
            data.append(link_url)
            i = i + 1
            if i == 1:
                break
    except:
        data.append("")
    
    with open('wordsscraped.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)
    return 1

def merriammedialapi_scrape(word_to_scrape):
    r = requests.get('https://www.dictionaryapi.com/api/v3/references/medical/json/' + word_to_scrape + '?key=49fe6b68-417a-44fc-99bd-349b04acca2e')
    info = r.json()
    data = []
    
    if r.status_code != 200:
        return -1
    else:    
        replacers = []
        parts = []
        right = []
        origin = []
        audio = []

        final_parts = ""
        final_right = ["No definition given."]
        final_origin = ["Medical / Scientific"]
        final_audio = "["

        try:
            for stuff in info:
                if (stuff["hwi"]["hw"].replace("*", "")).lower() == word_to_scrape:
                    parts.append(stuff["fl"].capitalize())
                parts = list(set(parts))
        except:
            return -1

        try:
            for stuff in info:
                for thing in stuff["shortdef"]:
                    if (stuff["hwi"]["hw"].replace("*", "")).lower() == word_to_scrape:
                        right.append(thing.capitalize())
        except:
            return -1

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
                    
                if (stuff["hwi"]["hw"].replace("*", "")).lower() == word_to_scrape:
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
                    if (stuff["hwi"]["hw"].replace("*", "")).lower() == word_to_scrape:
                        audio = "https://media.merriam-webster.com/audio/prons/en/us/mp3/" + great + "/" + id + ".mp3"
            except:
                pass
        if not audio or audio == "" or audio == "[]":
            return -1
            
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

        data = []
        
        data.append(word_to_scrape)
        data.append(final_right[0])
        data.append(final_right[1])
        data.append(final_right[2])
        data.append(final_parts)
        data.append(final_origin[0])
        data.append(final_origin[1])
        data.append(final_origin[2])        
        data.append(audio)        

        with open('wordsscraped.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)
        
    return 1


def oxfordapi(word_to_scrape):
    app_id = "ad49f899"
    app_key = "01622cb742e08d73a16cb360e1b4a581"
    endpoint = "entries"
    language_code = "en-us"

    word_id = re.sub(r"[^a-zA-Z]","", word_to_scrape)
    data = []
    try:
        url = "https://od-api.oxforddictionaries.com/api/v2/" + endpoint + "/" + language_code + "/" + word_id.lower()    
        r = requests.get(url, headers = {"app_id": app_id, "app_key": app_key})
        jsonObj = r.json()
        if r.status_code != 200:
            return -1
        else:
            wordtext = jsonObj['word']
            data.append(wordtext)
            result = jsonObj['results']

            try: 
              senses = result[0]['lexicalEntries'][0]['entries'][0]['senses']
              li_counter = 0
              for i in range(len(senses)):
                  definiton = senses[i]['definitions']
                  data.append(definiton[0])
                  li_counter = li_counter + 1
                  if li_counter == 3:
                      break
              if li_counter == 1:
                  data.append("")
                  data.append("")
              if li_counter == 2:
                  data.append("")
            except:
                data.append("")
                data.append("")
                data.append("")

            try:
                pos = result[0]['lexicalEntries'][0]['lexicalCategory']['text']
                data.append(pos)
            except:
                data.append("")
            
            try:
                add_count = 0
                etymology = result[0]['lexicalEntries'][0]['entries'][0]['etymologies']
                for x in range(len(languages)):
                    position=etymology[0].find(languages[x])
                    if position >= 0:
                        add_count += 1
                        if add_count <=3 :
                             data.append(languages[x])
                if add_count == 0:
                    data.append("")
                    data.append("")
                    data.append("")
                if add_count == 1:
                    data.append("")
                    data.append("")
                if add_count == 2:
                    data.append("")
            except:
                data.append("")
                data.append("")
                data.append("")
            

            try:
                entries = result[0]['lexicalEntries'][0]['entries'][0]            
                if entries.get('pronunciations') is not None:
                    pronunci = audiofile = result[0]['lexicalEntries'][0]['entries'][0]['pronunciations'][0]
                    if pronunci.get('audioFile') is not None:
                        audiofile = pronunci['audioFile']
                        data.append(audiofile)
                    else:
                        pronunci = audiofile = result[0]['lexicalEntries'][0]['entries'][0]['pronunciations'][1]
                        if pronunci.get('audioFile') is not None:
                            audiofile = pronunci['audioFile']
                            data.append(audiofile)
            except Exception as e: 
                data.append("")

        with open('wordsscraped.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)
        return 1
    except:
        return -1

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
    r = requests.get('https://dictionaryapi.com/api/v3/references/collegiate/json/' + word + '?key=932f5c09-8f67-49aa-b856-e8e99dd4ad7b')
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
        if not i >= 3 and (origin[i] != ""):
            final_origin[i] = origin[i]

    final_right.append(None)
    final_right.append(None)
    for i in range(len(right)):
        if not i >= 3 and (right[i] != ""):
            final_right[i] = right[i]

    for i in range(len(audio)):
        if i != (len(audio) - 1):
            final_audio += ("'" + audio[i] + "', ")
        else: 
            final_audio += ("'" + audio[i] + "']")
    
    new = Word(word=word, speech = final_parts, origin1 = final_origin[0], origin2 = final_origin[1], origin3 = final_origin[2], definition1 = final_right[0], definition2 = final_right[1], definition3 = final_right[2], pronounce = final_audio, tagged = False, rooted=False)
    new.save()

def locked(user):
    if not user.is_superuser:
        account = Account.objects.get(username=user.username)
        if not account.parent:
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
        else:
            account.daysleft = 30
            account.save()

    if user.is_superuser:
        return True
    elif Account.objects.get(username=user.username).locked == True:
        return False
    else:
        return True

def is_child(user):
    account = Account.objects.get(username=user.username)

    if account.parent == True:
        return False
    else:
        return True

# Create your views here.

def error_404(request, exception=False):
    return render(request, "spell/error_404.html", {})

# Homepage
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("admin_panel"))
    else:
        return render(request, "spell/index.html")

def contactrender(request):
    return render(request, "spell/contact.html", {
        "bar": "",
        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
        "active": "contactus"
    })

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

# Authorization pages
def login(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        form=MyForm(request.POST)
        
        if user is None:
            return render(request, "spell/login.html", {
                "form": MyForm(),
                "message": "Invalid username and/or password."
            })
        elif not form.is_valid():
            return render(request, "spell/login.html", {
                "form": MyForm(),
                "message": "Invalid captcha."
            })
        else:
            auth_login(request, user)
            return HttpResponseRedirect(reverse("admin_panel"))
    else:
        form=MyForm()
        return render(request, "spell/login.html", {"form": form})

def register(request):
    if request.method == "POST":
        pfname = request.POST["pfname"]
        plname = request.POST["plname"]
        pusername = request.POST["pusername"]
        pemail = request.POST["pemail"]
        ppasswordi = request.POST["ppassword"]
        pparentid = 0
        form=MyForm(request.POST)

        if not form.is_valid():
            return render(request, "spell/register.html", {
                "form": MyForm(),
                "message": "Invalid captcha."
            })

        if not Account.objects.filter(username=pusername).exists():
            it1 = random.randint(10000, 99999)
            it2 = random.randint(10000, 99999)
            confreq = ConfirmReq(fname = pfname, lname = plname, username = pusername, email = pemail, password = ppasswordi, lock1 = it1, lock2 = it2, parent=None)
            confreq.save()
            parentid = confreq.id

            try:
                msg = MIMEMultipart()
                msg['Subject'] = 'Official SpellNOW! Notification! -- Validate Email'
                msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
                msg["To"] = request.POST["email"]
                body_text = """Hello!\n\nThis is an official SpellNOW! Notification. You have recently attempted to register for a SpellNOW! account. As per SpellNOW! policy you must click the link below to validate your email address in order to complete account setup.\n\nhttps://spellnow.org/uservalidate/""" + str(confreq.id) + """-""" + str(it1) + """-""" + str(it2) + """\n\nThank you, and we hope you enjoy your continued use of SpellNOW!\n\nSincerely,\nSpellNOW! Support Team"""
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
        else:
            return render(request, "spell/register.html", {
                "form": MyForm(),
                "message": "Parent username already taken."
            })
        
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        username = request.POST["username"]
        email = request.POST["email"]
        passwordi = request.POST["password"]

        if (not Account.objects.filter(username=username).exists()) and (not ConfirmReq.objects.filter(username=username).exists()):
            it1 = random.randint(10000, 99999)
            it2 = random.randint(10000, 99999)
            confreq = ConfirmReq(fname = fname, lname = lname, username = username, email = email, password = passwordi, lock1 = it1, lock2 = it2, parent=parentid)
            confreq.save()

            try:
                msg = MIMEMultipart()
                msg['Subject'] = 'Official SpellNOW! Notification! -- Validate Email'
                msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
                msg["To"] = request.POST["email"]
                body_text = """Hello!\n\nThis is an official SpellNOW! Notification. Your parent recently attempted to register for a SpellNOW! account. As per SpellNOW! policy you must click the link below to validate your email address in order to complete account setup.\n\nhttps://spellnow.org/uservalidate/""" + str(confreq.id) + """-""" + str(it1) + """-""" + str(it2) + """\n\nThank you, and we hope you enjoy your continued use of SpellNOW!\n\nSincerely,\nSpellNOW! Support Team"""
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
        else:
            return render(request, "spell/register.html", {
                "form": MyForm(),
                "message": "Student username already taken."
            })
    else:
        form=MyForm()
        return render(request, "spell/register.html", {"form": form})

@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def single_register(request):
    if request.method == "POST":
        userusing = Account.objects.get(username=request.user.username)
        if userusing.parent:
            fname = request.POST["fname"]
            lname = request.POST["lname"]
            username = request.POST["username"]
            email = request.POST["email"]
            passwordi = request.POST["password"]

            form=MyForm(request.POST)

            if not form.is_valid():
                return render(request, "spell/single_register.html", {
                    "form": MyForm(),
                    "message": "Invalid captcha.",
                    "student": False
                })

            if (not Account.objects.filter(username=username).exists()) and (not ConfirmReq.objects.filter(username=username).exists()):
                it1 = random.randint(10000, 99999)
                it2 = random.randint(10000, 99999)
                confreq = ConfirmReq(fname = request.user.first_name, lname = request.user.last_name, username = request.user.username, email = request.user.email, password = request.user.password, lock1 = 1, lock2 = 1, parent=None)
                confreq.save()
                confreq = ConfirmReq(fname = fname, lname = lname, username = username, email = email, password = passwordi, lock1 = it1, lock2 = it2, parent=confreq.id)
                confreq.save()

                try:
                    msg = MIMEMultipart()
                    msg['Subject'] = 'Official SpellNOW! Notification! -- Validate Email'
                    msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
                    msg["To"] = request.POST["email"]
                    body_text = """Hello!\n\nThis is an official SpellNOW! Notification. Your parent recently attempted to register for a SpellNOW! account. As per SpellNOW! policy you must click the link below to validate your email address in order to complete account setup.\n\nhttps://spellnow.org/uservalidate/""" + str(confreq.id) + """-""" + str(it1) + """-""" + str(it2) + """\n\nThank you, and we hope you enjoy your continued use of SpellNOW!\n\nSincerely,\nSpellNOW! Support Team"""
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
            else:
                return render(request, "spell/single_register.html", {
                    "form": MyForm(),
                    "message": "Student username already taken.",
                    "student": False
                })
        else:
            return render(request, "spell/error_404.html", {}) 
    else:
        form=MyForm()
        return render(request, "spell/single_register.html", {"form": form, "student": False})

def student_register(request):
    if request.method == "POST":
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        username = request.POST["username"]
        email = request.POST["email"]
        passwordi = request.POST["password"]

        form=MyForm(request.POST)

        if not form.is_valid():
            return render(request, "spell/register.html", {
                "form": MyForm(),
                "message": "Invalid captcha.",
                "student": True
            })

        if not Account.objects.filter(username=username).exists():
            it1 = random.randint(10000, 99999)
            it2 = random.randint(10000, 99999)
            confreq = ConfirmReq(fname = fname, lname = lname, username = username, email = email, password = passwordi, lock1 = it1, lock2 = it2, parent=None)
            confreq.save()

            try:
                msg = MIMEMultipart()
                msg['Subject'] = 'Official SpellNOW! Notification! -- Validate Email'
                msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
                msg["To"] = request.POST["email"]
                body_text = """Hello!\n\nThis is an official SpellNOW! Notification. Your recently attempted to register for a SpellNOW! account. As per SpellNOW! policy you must click the link below to validate your email address in order to complete account setup.\n\nhttps://spellnow.org/uservalidate/""" + str(confreq.id) + """-""" + str(it1) + """-""" + str(it2) + """\n\nThank you, and we hope you enjoy your continued use of SpellNOW!\n\nSincerely,\nSpellNOW! Support Team"""
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
        else:
            return render(request, "spell/register.html", {
                "form": MyForm(),
                "message": "Student username already taken.",
                "student": True
            })

def uservalidate(request, userit, lockit1, lockit2):
    idofuser=userit
    lock1=lockit1
    lock2=lockit2

    try:
        valid = ConfirmReq.objects.get(pk=idofuser, lock1=lock1, lock2=lock2)
    
        # Attempt to create new user
        if (valid.parent == None) and (ConfirmReq.objects.filter(parent=valid.id).exists()):
            student = ConfirmReq.objects.get(parent=valid.id)
            user = Account.objects.create_user(valid.username, valid.email, valid.password, subscribed=False, locked=False, daysleft=30, trigger=True, repsub=True, changenotifs=True, newsletter=True, parent=True, parents=None)
        else:
            user = Account.objects.create_user(valid.username, valid.email, valid.password, subscribed=False, locked=False, daysleft=30, trigger=True, repsub=True, changenotifs=True, newsletter=True, parent=False)
        
        user.first_name = valid.fname
        user.last_name = valid.lname
        user.save()

        if user.parent:
            try:
                iguy = Account.objects.get(username=student.username)
                iguy.parents = user.id
                iguy.haschild = False
                iguy.save()
                user.children.add(iguy)
                user.date_joined = iguy.date_joined
                user.haschild = True
                user.save()
                student.delete()
                valid.delete()
            except:
                pass
        else:
            try:
                kool = ConfirmReq.objects.get(pk=idofuser, lock1=lock1, lock2=lock2)
                par = Account.objects.get(username = (ConfirmReq.objects.get(pk=kool.parent)).username)
                par.haschild = True
                par.save()
                user.haschild = False
                par.children.add(user)
                par.save()
                user.parents = par.id
                if par.haschild:
                    user.date_joined = par.date_joined
                user.save()
                
                (ConfirmReq.objects.get(pk=kool.parent)).delete()
                
                kool.delete()
            except:
                try:
                    fun = (ConfirmReq.objects.get(pk=kool.parent))
                except:
                    kool.delete()
        
        auth_login(request, user)
        return HttpResponseRedirect(reverse("admin_panel"))
    except:
        return render(request, "spell/error_404.html", {})

@login_required(login_url='/login')
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse("login"))

# Dashboard
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def admin_panel(request):
    if request.method == "POST":
        parent = Account.objects.get(username=request.user.username)
        userusing = Account.objects.get(pk=request.POST["child"])

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
        for report in Report.objects.filter(user=userusing, specific=True, finished__gt=datetime.date.today()):
            tagcount.append(report.used)
        tagcount = list(dict.fromkeys(tagcount))
        alltags = tagcount
        tagcount = len(tagcount)

        prevtags = []
        start = datetime.date.today() - datetime.timedelta(days = 1)
        end = datetime.date.today()

        for report in Report.objects.filter(user=userusing, specific=False, finished__range=(start, end)):
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
            
            tagrep.append({'tag': tag, 'correct': correct, 'total': total, 'percent': int((correct / total) * 100)})
        
        toppers = sorted(tagrep, key=lambda d: d['percent'])[:5]

        return render(request, "spell/parent_dashboard.html", {
            "bar": "",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "home",
            "ready": True,
            "children": parent.children.all(),
            "child": request.POST["child"],
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
        if not request.user.is_superuser:
            userusing = Account.objects.get(username=request.user.username)
            
            if userusing.parent == True:
                if userusing.trigger:
                    userusing.trigger = False
                    userusing.save()
                    return render(request, "spell/parent_dashboard.html", {
                        "bar": "",
                        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                        "active": "home",
                        "trigger": True,
                        "children": userusing.children.all(),
                    })
                else:
                    return render(request, "spell/parent_dashboard.html", {
                        "bar": "",
                        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                        "active": "home",
                        "children": userusing.children.all(),
                    })
            else:
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
                for report in Report.objects.filter(user=userusing, specific=True, finished__gt=datetime.date.today()):
                    tagcount.append(report.used)
                tagcount = list(dict.fromkeys(tagcount))
                alltags = tagcount
                tagcount = len(tagcount)

                prevtags = []
                start = datetime.date.today() - datetime.timedelta(days = 1)
                end = datetime.date.today()

                for report in Report.objects.filter(user=userusing, specific=False, finished__range=(start, end)):
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
                    
                    tagrep.append({'tag': tag, 'correct': correct, 'total': total, 'percent': int((correct / total) * 100)})
                
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
                        "tags": Tag.objects.filter(parent=None),
                        "roots": Root.objects.all(),
                        "results": results
                    })
                except:
                    return render(request, "spell/word_library.html", {
                        "bar": "libraries",
                        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                        "active": "coolwords",
                        "tags": Tag.objects.filter(parent=None),
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
                                "tags": Tag.objects.filter(parent=None),
                                "roots": Root.objects.all(),
                                "results": results
                            })
                        else:
                            return render(request, "spell/word_library.html", {
                                "bar": "libraries",
                                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                                "active": "coolwords",
                                "tags": Tag.objects.filter(parent=None),
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
                                    "tags": Tag.objects.filter(parent=None),
                                    "roots": Root.objects.all(),
                                    "results": set(results)
                                })
                            else:
                                return render(request, "spell/word_library.html", {
                                    "bar": "libraries",
                                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                                    "active": "coolwords",
                                    "tags": Tag.objects.filter(parent=None),
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
                                "tags": Tag.objects.filter(parent=None),
                                "roots": Root.objects.all(),
                                "results": results
                            })
                        else:
                            return render(request, "spell/word_library.html", {
                                "bar": "libraries",
                                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                                "active": "coolwords",
                                "tags": Tag.objects.filter(parent=None),
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
                            "tags": Tag.objects.filter(parent=None),
                            "roots": Root.objects.all(),
                            "results": results
                        })
                    else:
                        return render(request, "spell/word_library.html", {
                            "bar": "libraries",
                            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                            "active": "coolwords",
                            "tags": Tag.objects.filter(parent=None),
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
                            "tags": Tag.objects.filter(parent=None),
                            "roots": Root.objects.all(),
                            "results": results
                        })
                    else:
                        return render(request, "spell/word_library.html", {
                            "bar": "libraries",
                            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                            "active": "coolwords",
                            "tags": Tag.objects.filter(parent=None),
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
                            "tags": Tag.objects.filter(parent=None),
                            "roots": Root.objects.all(),
                            "results": results
                        })
                    else:
                        return render(request, "spell/word_library.html", {
                            "bar": "libraries",
                            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                            "active": "coolwords",
                            "tags": Tag.objects.filter(parent=None),
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
                        "tags": Tag.objects.filter(parent=None),
                        "roots": Root.objects.all(),
                        "results": results
                    })
                else:
                    return render(request, "spell/word_library.html", {
                        "bar": "libraries",
                        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                        "active": "coolwords",
                        "tags": Tag.objects.filter(parent=None),
                        "roots": Root.objects.all(),
                        "message": True
                    })
    else:
        return render(request, "spell/word_library.html", {
            "bar": "libraries",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "coolwords",
            "tags": Tag.objects.filter(parent=None),
            "roots": Root.objects.all()
        })

@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def tag_library(request):
    if request.method == "POST":
        try:
            thing = request.POST["tag"]
            part = int(request.POST["parent"])
            part = Tag.objects.get(id=part)
            if not (("---" in thing) or ('"' in thing) or ("'" in thing) or ("*..*" in thing) or (", " in thing) or (thing in Tag.objects.all().values_list("name", flat=True))):
                new = Tag(name=thing, parent=part)
                new.save()
                return render(request, "spell/tag_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "taags",
                    "partags": Tag.objects.filter(parent=None),
                    "childtags": Tag.objects.filter(parent__isnull=False),
                    "tags": Tag.objects.all()
                })
            else:
                return render(request, "spell/tag_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "taags",
                    "tags": Tag.objects.all(),
                    "partags": Tag.objects.filter(parent=None),
                    "childtags": Tag.objects.filter(parent__isnull=False),
                    "error": True
                })
        except:
            thing = request.POST["rentag"]
            if not (("---" in thing) or ('"' in thing) or ("'" in thing) or ("*..*" in thing) or (", " in thing) or (thing in Tag.objects.all().values_list("name", flat=True))):
                new = Tag.objects.get(pk=int(request.POST["tagid"]))
                new.name = thing
                new.save()
                return render(request, "spell/tag_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "taags",
                    "partags": Tag.objects.filter(parent=None),
                    "childtags": Tag.objects.filter(parent__isnull=False),
                    "tags": Tag.objects.all()
                })
            else:
                return render(request, "spell/tag_library.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "taags",
                    "tags": Tag.objects.all(),
                    "partags": Tag.objects.filter(parent=None),
                    "childtags": Tag.objects.filter(parent__isnull=False),
                    "namerror": int(request.POST["tagid"])
                })
    else:
        return render(request, "spell/tag_library.html", {
            "bar": "libraries",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "taags",
            "partags": Tag.objects.filter(parent=None),
            "childtags": Tag.objects.filter(parent__isnull=False),
            "tags": Tag.objects.all()
        })

@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def partag(request):
    thing = request.POST["tag"]
    if not (("---" in thing) or ('"' in thing) or ("'" in thing) or ("*..*" in thing) or (", " in thing) or (thing in Tag.objects.all().values_list("name", flat=True))):
        new = Tag(parent=None, name=thing)
        new.save()
        return HttpResponseRedirect(reverse("tag_library"))
    else:
        return render(request, "spell/tag_library.html", {
            "bar": "libraries",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "taags",
            "tags": Tag.objects.all(),
            "partags": Tag.objects.filter(parent=None),
            "childtags": Tag.objects.filter(parent__isnull=False),
            "perror": True
        })

@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def save_tag(request, tagid):
    thing = int(request.POST["parent"])
    child = Tag.objects.get(id=tagid)
    parent = Tag.objects.get(id=thing)
    child.parent = parent
    child.save()
    
    return HttpResponseRedirect(reverse("tag_library"))

@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def root_library(request):
    if request.method == "POST":
        try:
            thing = request.POST["root"]
            if not (("---" in thing) or ('"' in thing) or ("'" in thing) or ("*..*" in thing) or (", " in thing) or (thing in Tag.objects.all().values_list("name", flat=True))):
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
            if not (("---" in thing) or ('"' in thing) or ("'" in thing) or ("*..*" in thing) or (", " in thing) or (thing in Tag.objects.all().values_list("name", flat=True))):
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
@user_passes_test(locked, login_url='/subscribe')
def delete_tag(request, id):
    tag = Tag.objects.get(pk=id)

    for child in Tag.objects.filter(parent=tag):
        child.parent = Tag.objects.get(pk=248)
        child.save()

    tag.delete()
    return HttpResponseRedirect(reverse("tag_library"))

# Root Changes
@user_passes_test(lambda u: u.is_staff)
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
                try:
                    new_word = row[0].lower()
                except:
                    continue
                
                if not Word.objects.filter(word=new_word):
                    if is_word(new_word):
                        create_word(new_word)
                    else:
                        nots.append(new_word)
                else:
                    already.append(new_word)
            f.close()
            os.remove("spell/static/spell/words.csv")

            if exists("wordsscraped.csv"):
                os.remove("wordsscraped.csv")

            if len(nots) > 0:
                header = ['word', 'def1','def2','def3', 'pos', 'loo1','loo2','loo3', 'soundfile']

                with open('wordsscraped.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(header)

                counter = 1
                li_ret = 0
                for x in nots:
                    print("Counter-",counter)
                    counter += 1
                    my_word = re.sub(r"[^a-zA-Z]","", x)
                    data = []

                    li_ret = int(dictionarydotcom_scrape(my_word))
                    if li_ret <= 0:
                        li_ret = int(oxfordapi(my_word))
                        if li_ret <= 0:
                            li_ret = int(merriammedialapi_scrape(my_word))
                            if li_ret <= 0:
                                li_ret = int(merriamweb_scrape(my_word))
                                if li_ret <= 0:
                                    print("merriamweb fail")
                                    data.append(my_word)
                                    data.append("WORD NOT FOUND")
                                    with open('wordsscraped.csv', 'a', newline='', encoding='utf-8') as csvfile:
                                        writer = csv.writer(csvfile)
                                        writer.writerow(data)

                with open('wordsscraped.csv', 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)
                    
                    for row in reader:
                        try:
                            new_word = row[0].lower()
                            new_speech = row[4]

                            new_origin1 = "No origin given."
                            if row[5] != "":
                                new_origin1 = row[5]
                            new_origin2 = None
                            if row[6] != "":
                                new_origin2 = row[6]
                            new_origin3 = None
                            if row[7] != "":
                                new_origin3 = row[7]
                            
                            new_def1 = "No definition given."
                            if row[1] != "":
                                new_def1 = row[1]
                            new_def2 = None
                            if row[2] != "":
                                new_def2 = row[2]
                            new_def3 = None
                            if row[3] != "":
                                new_def3 = row[3]

                            if "mp3" in row[8]:
                                new_pronounce = "['" + row[8] + "']"
                                new = Word(word=new_word, speech = new_speech, origin1 = new_origin1, origin2 = new_origin2, origin3 = new_origin3, definition1 = new_def1, definition2 = new_def2, definition3 = new_def3, pronounce = new_pronounce, tagged=False, rooted=False)
                                new.save()
                                nots.remove(new_word)
                        except:
                            pass
            
            os.remove("wordsscraped.csv")

            for duplicate in Word.objects.values("word").annotate(records=Count("word")).filter(records__gt=1):
                for word in Word.objects.filter(word=duplicate["word"])[1:]:
                    word.delete()

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
            file = request.FILES["csv"]
            fs = FileSystemStorage()
            fs.save("spell/static/spell/custom.csv", file)
            f = open("spell/static/spell/custom.csv", "r")
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                try:
                    final = row[0].lower()
                except:
                    continue
                
                if not Word.objects.filter(word=final):
                    new_word = row[0].lower()
                    new_speech = row[4]

                    new_origin1 = "No origin given."
                    new_origin2 = None
                    if row[6] != "":
                        new_origin2 = row[6]
                    new_origin3 = None
                    if row[7] != "":
                        new_origin3 = row[7]
                    
                    new_def1 = "No definition given."
                    new_def2 = None
                    if row[2] != "":
                        new_def2 = row[2]
                    new_def3 = None
                    if row[2] != "":
                        new_def3 = row[2]
                    
                    new_pronounce = "['" + row[8] + "']"

                    new = Word(word=new_word, speech = new_speech, origin1 = new_origin1, origin2 = new_origin2, origin3 = new_origin3, definition1 = new_def1, definition2 = new_def2, definition3 = new_def3, pronounce = new_pronounce, tagged=False, rooted=False)
                    new.save()
                else:
                    already.append(final)
            
            f.close()
            if len(already) > 0:
                return render(request, "spell/error.html", {
                    "bar": "libraries",
                    "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                    "active": "import",
                    'nots': [],
                    'already': already,
                    'message2': "SpellNOW!&trade; found these words already in your list:",
                })
            else:
                return HttpResponseRedirect(reverse("word_library"))
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
                try:
                    final = row[0].lower()
                except:
                    continue
                
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
                try:
                    final = row[0].lower()
                except:
                    continue
                
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
                try:
                    final = row[0].lower()
                except:
                    continue
                
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
                try:
                    final = row[0].lower()
                except:
                    continue
                
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
                try:
                    final = row[0].lower()
                except:
                    continue
                
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
            "tags": Tag.objects.all().exclude(parent=None),
            "roots": Root.objects.all()
        })

# Activities

# Spelling
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
@user_passes_test(is_child, login_url='/error_404')
def start(request):
    total = []
    for tag in Tag.objects.filter(parent=None).exclude(name="Other Tags"):
        part = {"parent": tag, "children": Tag.objects.filter(parent=tag)}
        total.append(part)
    total.append({"parent": Tag.objects.get(name="Other Tags"), "children": Tag.objects.filter(parent=Tag.objects.get(name="Other Tags"))})

    return render(request, "spell/spelling_start.html", {
        "bar": "activities",
        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
        "active": "spellit",
        "tags": total,
        "roots": Root.objects.all(),
        "number": len(Word.objects.all()),
        "fun": [{"Ids": "latin", "Root": "Latin", "Go": list(Root.objects.filter(origin="Latin"))}, {"Ids": "newlatin", "Root": "New Latin", "Go": list(Root.objects.filter(origin="New Latin"))}, {"Ids": "greek", "Root": "Greek", "Go": list(Root.objects.filter(origin="Greek"))}, {"Ids": "italian", "Root": "Italian", "Go": list(Root.objects.filter(origin="Italian"))}, {"Ids": "spanish", "Root": "Spanish", "Go": list(Root.objects.filter(origin="Spanish"))}, {"Ids": "french", "Root": "French", "Go": list(Root.objects.filter(origin="French"))}, {"Ids": "german", "Root": "German", "Go": list(Root.objects.filter(origin="German"))}, {"Ids": "portuguese", "Root": "Portuguese", "Go": list(Root.objects.filter(origin="Portuguese"))}, {"Ids": "middlenglish", "Root": "Middle English", "Go": list(Root.objects.filter(origin="Middle English"))}, {"Ids": "isv", "Root": "International Scientific Vocabulary", "Go": list(Root.objects.filter(origin="International Scientific Vocabulary"))}],
        "others": Root.objects.all().exclude(Q(origin="Latin") | Q(origin="International Scientific Vocabulary") | Q(origin="New Latin") | Q(origin="Greek") | Q(origin="Italian") | Q(origin="Spanish") | Q(origin="French") | Q(origin="German") | Q(origin="Portuguese") | Q(origin="Middle English"))
    })

@user_passes_test(locked, login_url='/subscribe')
@user_passes_test(is_child, login_url='/error_404')
def spell(request):
    if request.method == "POST":
        getterem = Tag.objects.filter(parent=None).values_list('pk', flat=True)
        tags = []
        for gotte in getterem:
            whatwegot = request.POST.getlist("query" + str(gotte))
            tags.extend(whatwegot)
        
        try:
            if request.POST.get("untagged") == "yes":
                tags.append("*..*")
        except:
            pass
        
        roots = []
        whatwegot = request.POST.getlist("acctlatin")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctnewlatin")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctgreek")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctitalian")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctspanish")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctfrench")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctgerman")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctportuguese")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctmiddlenglish")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctisv")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctothers")
        roots.extend(whatwegot)

        try:
            if request.POST.get("unrooted") == "yes":
                roots.append("|--|*..*")
        except:
            pass

        fullcall = []
        fullcall.extend(tags)
        fullcall.extend(roots)
        attn = False

        try:
            if request.POST.get("attn") == "attemptednone":
                attn = True
        except:
            attn = False

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

        gunroots = []
        for root in roots:
            gunroots.append(root.replace("|--|", ""))

        if not attn:
            if "*..*" in tags and "|--|*..*" in roots:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(tagged=False) | Q(roots__name__in=gunroots) | Q(rooted=False))).distinct()))
            elif "*..*" in tags:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(tagged=False) )).distinct()))
            elif "|--|*..*" in roots:
                results.extend(list((Word.objects.filter(Q(roots__name__in=cool) | Q(rooted=False) )).distinct()))
            else:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(roots__name__in=gunroots))).distinct()))
        else:
            yaylmao = ReportDetail.objects.filter(report__user__username=request.user.username).values_list('word', flat=True)

            if "*..*" in tags and "|--|*..*" in roots:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(tagged=False) | Q(roots__name__in=gunroots) | Q(rooted=False))).exclude(word__in = yaylmao).distinct()))
            elif "*..*" in tags:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(tagged=False) )).exclude(word__in = yaylmao).distinct()))
            elif "|--|*..*" in roots:
                results.extend(list((Word.objects.filter(Q(roots__name__in=cool) | Q(rooted=False) )).exclude(word__in = yaylmao).distinct()))
            else:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(roots__name__in=gunroots))).exclude(word__in = yaylmao).distinct()))
        
        if (int(len(results)) < int(request.POST["numwords"])) or (int(len(tags)) > int(request.POST["numwords"])):
            total = []
        
            for tag in Tag.objects.filter(parent=None).exclude(name="Other Tags"):
                part = {"parent": tag, "children": Tag.objects.filter(parent=tag)}
                total.append(part)
            total.append({"parent": Tag.objects.get(name="Other Tags"), "children": Tag.objects.filter(parent=Tag.objects.get(name="Other Tags"))})
            
            return render(request, "spell/spelling_start.html", {
                "bar": "activities",
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "active": "spellit",
                "tags": total,
                "roots": Root.objects.all(),
                "number": len(Word.objects.all()),
                "message": "Invalid word count, the maximum number of words you may have under this configuration is " + str(int(len(results))) + ". Or the number of tags that you have chosen is less than the number of words you have requested.",
                "fun": [{"Ids": "latin", "Root": "Latin", "Go": list(Root.objects.filter(origin="Latin"))}, {"Ids": "newlatin", "Root": "New Latin", "Go": list(Root.objects.filter(origin="New Latin"))}, {"Ids": "greek", "Root": "Greek", "Go": list(Root.objects.filter(origin="Greek"))}, {"Ids": "italian", "Root": "Italian", "Go": list(Root.objects.filter(origin="Italian"))}, {"Ids": "spanish", "Root": "Spanish", "Go": list(Root.objects.filter(origin="Spanish"))}, {"Ids": "french", "Root": "French", "Go": list(Root.objects.filter(origin="French"))}, {"Ids": "german", "Root": "German", "Go": list(Root.objects.filter(origin="German"))}, {"Ids": "portuguese", "Root": "Portuguese", "Go": list(Root.objects.filter(origin="Portuguese"))}, {"Ids": "middlenglish", "Root": "Middle English", "Go": list(Root.objects.filter(origin="Middle English"))}, {"Ids": "isv", "Root": "International Scientific Vocabulary", "Go": list(Root.objects.filter(origin="International Scientific Vocabulary"))}],
                "others": Root.objects.all().exclude(Q(origin="Latin") | Q(origin="International Scientific Vocabulary") | Q(origin="New Latin") | Q(origin="Greek") | Q(origin="Italian") | Q(origin="Spanish") | Q(origin="French") | Q(origin="German") | Q(origin="Portuguese") | Q(origin="Middle English"))
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
            
            if not attn:
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
            else:
                yaylmao = ReportDetail.objects.filter(report__user__username=request.user.username).values_list('word', flat=True)

                for ite in fullcall:
                    if ite == "*..*":
                        didi.append(list(Word.objects.filter(tagged=False).exclude(id__in = results).exclude(word__in = yaylmao).values_list('pk', flat=True)))
                        results.extend(list(Word.objects.filter(tagged=False).exclude(id__in = results).exclude(word__in = yaylmao).values_list('pk', flat=True)))
                        use = len(didi[jeff])
                        lengths.append(use)
                    elif ite == "|--|*..*":
                        didi.append(list(Word.objects.filter(rooted=False).exclude(id__in = results).exclude(word__in = yaylmao).values_list('pk', flat=True)))
                        results.extend(list(Word.objects.filter(rooted=False).exclude(id__in = results).exclude(word__in = yaylmao).values_list('pk', flat=True)))
                        use = len(didi[jeff])
                        lengths.append(use)
                    elif "|--|" in ite:
                        didi.append(list(Word.objects.filter(roots__name=ite.replace("|--|", "")).exclude(word__in = yaylmao).exclude(id__in = results).values_list('pk', flat=True)))
                        results.extend(list(Word.objects.filter(roots__name=ite.replace("|--|", "")).exclude(word__in = yaylmao).exclude(id__in = results).values_list('pk', flat=True)))
                        use = len(didi[jeff])
                        lengths.append(use)
                    else:
                        didi.append(list(Word.objects.filter(tags__name=ite).exclude(id__in = results).exclude(word__in = yaylmao).values_list('pk', flat=True)))
                        results.extend(list((Word.objects.filter(tags__name=ite).exclude(id__in = results)).exclude(word__in = yaylmao).values_list('pk', flat=True)))
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
                print(surplus[i])
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
    userusing = Account.objects.get(pk=int(request.POST["user"]))
    new = Report(used=ids_used, correct=thingy[0], total=(thingy[1]), percent=(int((int(thingy[0])/int(thingy[1]))*100)), specific=False, user=userusing, spelling=True)
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
                new = Report(used="Untagged", correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing, spelling=True)
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
                new = Report(used="No Roots", correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing, spelling=True)
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
                new = Report(used=("Root - " + ite.replace("|--|", "")), correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing, spelling=True)
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
                new = Report(used=("Tag - " + ite), correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing, spelling=True)
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

    report_using = Report.objects.get(id=id_using)
    for tmp in words:
        if int(correct_array[count - 1]) == 0:
            roger = count
            detail = ReportDetail(count=roger, identification=wilk[count - 1], word=tmp, attempt=atts[count - 1], result="INCORRECT", time=time[count - 1], report=report_using)
            detail.save()
        else:
            roger = count
            detail = ReportDetail(count=roger, identification=wilk[count - 1], word=tmp, attempt=atts[count - 1], result="CORRECT", time=time[count - 1], report=report_using)
            detail.save()
        count += 1
    
    try:
        parent = Account.objects.get(pk=userusing.parents)

        if parent.repsub == True:
            msg = MIMEMultipart()
            msg['Subject'] = 'Official SpellNOW! Notification! -- New Report'
            msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
            msg["To"] = parent.email
            body_text = """Hello!\n\nThis is an Official SpellNOW! Notification. """ + userusing.first_name + """ has complete a spelling activity on SpellNOW! with a score of """ + request.POST["score"] + """. You can learn more details of this activity by visiting https://spellnow.org/report/""" + str(report_using.id) + """. Thank you, and we hope for your continued progress for the future.\n\nSincerely,\nSpellNOW! Support Team"""

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
    
    return render(request, "spell/spelling_finish.html", {
        "bar": "activities",
        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
        "active": "spellit",
        "score": request.POST["score"]
    })

# Spelling
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
@user_passes_test(is_child, login_url='/error_404')
def vocab_start(request):
    total = []
    for tag in Tag.objects.filter(parent=None).exclude(name="Other Tags"):
        part = {"parent": tag, "children": Tag.objects.filter(parent=tag)}
        total.append(part)
    total.append({"parent": Tag.objects.get(name="Other Tags"), "children": Tag.objects.filter(parent=Tag.objects.get(name="Other Tags"))})

    return render(request, "spell/vocab_start.html", {
        "bar": "activities",
        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
        "active": "vocabit",
        "tags": total,
        "roots": Root.objects.all(),
        "number": len(Word.objects.all()),
        "fun": [{"Ids": "latin", "Root": "Latin", "Go": list(Root.objects.filter(origin="Latin"))}, {"Ids": "newlatin", "Root": "New Latin", "Go": list(Root.objects.filter(origin="New Latin"))}, {"Ids": "greek", "Root": "Greek", "Go": list(Root.objects.filter(origin="Greek"))}, {"Ids": "italian", "Root": "Italian", "Go": list(Root.objects.filter(origin="Italian"))}, {"Ids": "spanish", "Root": "Spanish", "Go": list(Root.objects.filter(origin="Spanish"))}, {"Ids": "french", "Root": "French", "Go": list(Root.objects.filter(origin="French"))}, {"Ids": "german", "Root": "German", "Go": list(Root.objects.filter(origin="German"))}, {"Ids": "portuguese", "Root": "Portuguese", "Go": list(Root.objects.filter(origin="Portuguese"))}, {"Ids": "middlenglish", "Root": "Middle English", "Go": list(Root.objects.filter(origin="Middle English"))}, {"Ids": "isv", "Root": "International Scientific Vocabulary", "Go": list(Root.objects.filter(origin="International Scientific Vocabulary"))}],
        "others": Root.objects.all().exclude(Q(origin="Latin") | Q(origin="International Scientific Vocabulary") | Q(origin="New Latin") | Q(origin="Greek") | Q(origin="Italian") | Q(origin="Spanish") | Q(origin="French") | Q(origin="German") | Q(origin="Portuguese") | Q(origin="Middle English"))
    })

@user_passes_test(locked, login_url='/subscribe')
@user_passes_test(is_child, login_url='/error_404')
def vocab(request):
    if request.method == "POST":
        getterem = Tag.objects.filter(parent=None).values_list('pk', flat=True)
        tags = []
        for gotte in getterem:
            whatwegot = request.POST.getlist("query" + str(gotte))
            tags.extend(whatwegot)
        
        try:
            if request.POST.get("untagged") == "yes":
                tags.append("*..*")
        except:
            pass

        roots = []
        whatwegot = request.POST.getlist("acctlatin")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctnewlatin")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctisv")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctgreek")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctitalian")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctspanish")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctfrench")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctgerman")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctportuguese")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctmiddlenglish")
        roots.extend(whatwegot)
        whatwegot = request.POST.getlist("acctothers")
        roots.extend(whatwegot)

        try:
            if request.POST.get("unrooted") == "yes":
                roots.append("|--|*..*")
        except:
            pass

        fullcall = []
        fullcall.extend(tags)
        fullcall.extend(roots)
        attn = False

        try:
            if request.POST.get("attn") == "attemptednone":
                attn = True
        except:
            attn = False

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

        gunroots = []
        for root in roots:
            gunroots.append(root.replace("|--|", ""))

        if not attn:
            if "*..*" in tags and "*..*" in roots:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(tagged=False) | Q(roots__name__in=gunroots) | Q(rooted=False))).exclude(definition1=None).distinct()))
            elif "*..*" in tags:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(tagged=False))).exclude(definition1=None).distinct()))
            elif "*..*" in roots:
                results.extend(list((Word.objects.filter(Q(roots__name__in=cool) | Q(rooted=False))).exclude(definition1=None).distinct()))
            else:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(roots__name__in=gunroots))).exclude(definition1=None).distinct()))
        else:
            yaylmao = list(VocabReportDetail.objects.filter(report__user__username=request.user.username).exclude(answer__contains=" ").values_list('answer', flat=True))
            yaylmao.extend(list(VocabReportDetail.objects.filter(report__user__username=request.user.username).exclude(question__contains=" ").values_list('question', flat=True)))

            if "*..*" in tags and "*..*" in roots:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(tagged=False) | Q(roots__name__in=gunroots) | Q(rooted=False))).exclude(definition1=None).exclude(word__in = yaylmao).distinct()))
            elif "*..*" in tags:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(tagged=False) )).exclude(word__in = yaylmao).exclude(definition1=None).distinct()))
            elif "*..*" in roots:
                results.extend(list((Word.objects.filter(Q(roots__name__in=cool) | Q(rooted=False) )).exclude(word__in = yaylmao).exclude(definition1=None).distinct()))
            else:
                results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(roots__name__in=gunroots))).exclude(word__in = yaylmao).exclude(definition1=None).distinct()))
        
        if (int(len(results)) < int(request.POST["numwords"])) or (int(len(tags)) > int(request.POST["numwords"])):
            total = []
        
            for tag in Tag.objects.filter(parent=None).exclude(name="Other Tags"):
                part = {"parent": tag, "children": Tag.objects.filter(parent=tag)}
                total.append(part)
            total.append({"parent": Tag.objects.get(name="Other Tags"), "children": Tag.objects.filter(parent=Tag.objects.get(name="Other Tags"))})
            
            return render(request, "spell/vocab_start.html", {
                "bar": "activities",
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "active": "vocabit",
                "tags": total,
                "roots": Root.objects.all(),
                "number": len(Word.objects.all()),
                "message": "Invalid word count, the maximum number of words you may have under this configuration is " + str(int(len(results))) + ". Or the number of tags that you have chosen is less than the number of words you have requested.",
                "fun": [{"Ids": "latin", "Root": "Latin", "Go": list(Root.objects.filter(origin="Latin"))}, {"Ids": "newlatin", "Root": "New Latin", "Go": list(Root.objects.filter(origin="New Latin"))}, {"Ids": "greek", "Root": "Greek", "Go": list(Root.objects.filter(origin="Greek"))}, {"Ids": "italian", "Root": "Italian", "Go": list(Root.objects.filter(origin="Italian"))}, {"Ids": "spanish", "Root": "Spanish", "Go": list(Root.objects.filter(origin="Spanish"))}, {"Ids": "french", "Root": "French", "Go": list(Root.objects.filter(origin="French"))}, {"Ids": "german", "Root": "German", "Go": list(Root.objects.filter(origin="German"))}, {"Ids": "portuguese", "Root": "Portuguese", "Go": list(Root.objects.filter(origin="Portuguese"))}, {"Ids": "middlenglish", "Root": "Middle English", "Go": list(Root.objects.filter(origin="Middle English"))}, {"Ids": "isv", "Root": "International Scientific Vocabulary", "Go": list(Root.objects.filter(origin="International Scientific Vocabulary"))}],
                "others": Root.objects.all().exclude(Q(origin="Latin") | Q(origin="International Scientific Vocabulary") | Q(origin="New Latin") | Q(origin="Greek") | Q(origin="Italian") | Q(origin="Spanish") | Q(origin="French") | Q(origin="German") | Q(origin="Portuguese") | Q(origin="Middle English"))
            })
        else:
            fines = []
            allans = ""
            order = ""
            final_last_total = 0
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

            if not attn:
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
            else:
                yaylmao = list(VocabReportDetail.objects.filter(report__user__username=request.user.username).exclude(answer__contains=" ").values_list('answer', flat=True))
                yaylmao.extend(list(VocabReportDetail.objects.filter(report__user__username=request.user.username).exclude(question__contains=" ").values_list('question', flat=True)))

                for ite in fullcall:
                    if ite == "*..*":
                        didi.append(list(Word.objects.filter(tagged=False).exclude(id__in = results).exclude(word__in = yaylmao).values_list('pk', flat=True)))
                        results.extend(list(Word.objects.filter(tagged=False).exclude(id__in = results).exclude(word__in = yaylmao).values_list('pk', flat=True)))
                        use = len(didi[jeff])
                        lengths.append(use)
                    elif ite == "|--|*..*":
                        didi.append(list(Word.objects.filter(rooted=False).exclude(id__in = results).exclude(word__in = yaylmao).values_list('pk', flat=True)))
                        results.extend(list(Word.objects.filter(rooted=False).exclude(id__in = results).exclude(word__in = yaylmao).values_list('pk', flat=True)))
                        use = len(didi[jeff])
                        lengths.append(use)
                    elif "|--|" in ite:
                        didi.append(list(Word.objects.filter(roots__name=ite.replace("|--|", "")).exclude(word__in = yaylmao).exclude(id__in = results).values_list('pk', flat=True)))
                        results.extend(list(Word.objects.filter(roots__name=ite.replace("|--|", "")).exclude(word__in = yaylmao).exclude(id__in = results).values_list('pk', flat=True)))
                        use = len(didi[jeff])
                        lengths.append(use)
                    else:
                        didi.append(list(Word.objects.filter(tags__name=ite).exclude(id__in = results).exclude(word__in = yaylmao).values_list('pk', flat=True)))
                        results.extend(list((Word.objects.filter(tags__name=ite).exclude(id__in = results)).exclude(word__in = yaylmao).values_list('pk', flat=True)))
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
                print(surplus[i])
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

            defs1 = list(Word.objects.filter().exclude(definition1 = "No definition given.").values_list('definition1', flat=True))
            defs2 = list(Word.objects.filter().exclude(definition2 = None).values_list('definition2', flat=True))
            defs3 = list(Word.objects.filter().exclude(definition3 = None).values_list('definition3', flat=True))
            wordsample = Word.objects.filter().values_list('word', flat=True)
            optionsit = ""
            questions = ""

            i = 0
            print("========================Getting Words========================")
            for lemmon in range(int(len(better))):
                for pkg in didi[lemmon]:
                    word = Word.objects.get(pk=pkg)
                    chooser = random.randrange(2)

                    if chooser == 0:
                        questions += "Which of the following best defines the word <b>" + word.word + "</b>?+--+"

                        options = []
                        
                        if not word.definition1 == None:
                            options.append(word.definition1)
                        
                        if not word.definition2 == None:
                            options.append(word.definition2)
                        
                        if not word.definition3 == None:
                            options.append(word.definition3)
                        
                        optionuse = (random.choice(options))

                        tmp1 = defs1
                        tmp2 = defs2
                        tmp3 = defs3
                    
                        try:
                            tmp1.remove(word.definition1)
                            tmp2.remove(word.definition2)
                            tmp3.remove(word.definition3)
                        except:
                            pass
                        
                        answer = random.randrange(4)

                        if answer == 0:
                            allans += "A||==||"
                            optionsit += (optionuse + "--00--")

                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--")
                            
                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--")
                            
                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--9889")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--9889")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--9889")

                        elif answer == 1:
                            allans += "B||==||"
                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--")
                            
                            optionsit += (optionuse + "--00--")
                            
                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--")
                            
                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--9889")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--9889")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--9889")
                        
                        elif answer == 2:
                            allans += "C||==||"
                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--")
                            
                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--")
                            
                            optionsit += (optionuse + "--00--")
                            
                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--9889")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--9889")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--9889")
                        else:
                            allans += "D||==||"
                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--")
                            
                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--")
                            
                            next = random.randrange(3)

                            if next == 0:
                                optionsit += (random.choice(tmp1) + "--00--")
                            elif next == 1:
                                optionsit += (random.choice(tmp2) + "--00--")
                            else:
                                optionsit += (random.choice(tmp3) + "--00--")
                            
                            optionsit += (optionuse + "--00--9889")
                    else:
                        options = []
                        
                        if not word.definition1 == None:
                            options.append(word.definition1)
                        
                        if not word.definition2 == None:
                            options.append(word.definition2)
                        
                        if not word.definition3 == None:
                            options.append(word.definition3)

                        questions += "Which of the following words is best defined by: <b>" + (random.choice(options)) + "</b>?+--+"
                        optionuse = word.word

                        tmp = wordsample

                        try:
                            tmp.remove(word.word)
                        except:
                            pass
                        
                        answer = random.randrange(4)

                        if answer == 0:
                            allans += "A||==||"
                            optionsit += ((optionuse + "--00--") + (random.choice(tmp) + "--00--") + (random.choice(tmp) + "--00--") + (random.choice(tmp) + "--00--9889"))                        
                        elif answer == 1:
                            allans += "B||==||"
                            optionsit += ((random.choice(tmp) + "--00--") + (optionuse + "--00--") + (random.choice(tmp) + "--00--") + (random.choice(tmp) + "--00--9889"))
                        elif answer == 2:
                            allans += "C||==||"
                            optionsit += ((random.choice(tmp) + "--00--") + (random.choice(tmp) + "--00--") + (optionuse + "--00--") + (random.choice(tmp) + "--00--9889"))
                        else:
                            allans += "D||==||"
                            optionsit += ((random.choice(tmp) + "--00--") + (random.choice(tmp) + "--00--") + (random.choice(tmp) + "--00--") + (optionuse + "--00--9889"))

                    order += (fullcall[lemmon] + ", ")
                    
                    if not fullcall[lemmon] in hllg:
                        hllg.append(fullcall[lemmon])
                        ids_used += (fullcall[lemmon] + ", ")

                    fines.append(word.word)

                    print("Got word " + str(final_last_total) + " of " + request.POST["numwords"])
                    final_last_total += 1
                    
                    i += 1
            
            return render(request, "spell/vocab.html", {
                "bar": "activities",
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "active": "vocabit",
                "words": fines,
                "ans": allans,
                "questions": questions,
                "options": optionsit,
                "order": order,
                "ids_used": ids_used,
            })

def vocab_finish(request):
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
    words = glob.split("990099")
    words.remove("")

    coolb = request.POST["vocabas"]
    vocabas = coolb.split("9009")
    vocabas.remove("")

    dumb = request.POST["attempts"]
    atts = dumb.split("9009")
    atts.remove("")

    timings = request.POST["time"]
    time = timings.split(", ")
    time.remove("")

    cool = 0
    id_using = 0
    thingy = (request.POST["score"]).split("/")
    userusing = Account.objects.get(pk=int(request.POST["user"]))
    new = Report(used=ids_used, correct=thingy[0], total=(thingy[1]), percent=(int((int(thingy[0])/int(thingy[1]))*100)), specific=False, user=userusing, spelling=False)
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
                new = Report(used="Untagged", correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing, spelling=False)
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
                new = Report(used="No Roots", correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing, spelling=False)
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
                new = Report(used=("Root - " + ite.replace("|--|", "")), correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing, spelling=False)
                new.save()
                wilk.append(("Root - " + ite.replace("|--|", "")))
        else:
            print(correct_array)
            nice = 0
            cool = 0
            abhi = 0
            for ishaan in order:
                if ishaan == ite:
                    nice += int(correct_array[cool])
                    abhi += 1
                cool += 1
            
            if abhi != 0:
                new = Report(used=("Tag - " + ite), correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using, user=userusing, spelling=False)
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

    report_using = Report.objects.get(id=id_using)
    for tmp in words:
        if int(correct_array[count - 1]) == 0:
            roger = count
            detail = VocabReportDetail(count=roger, identification=wilk[count - 1], question=tmp, answer = vocabas[count-1], attempt=atts[count - 1], result="INCORRECT", time=time[count - 1], report=report_using)
            detail.save()
        else:
            roger = count
            detail = VocabReportDetail(count=roger, identification=wilk[count - 1], question=tmp, answer = vocabas[count-1], attempt=atts[count - 1], result="CORRECT", time=time[count - 1], report=report_using)
            detail.save()
        count += 1
    
    try:
        parent = Account.objects.get(pk=userusing.parents)

        if parent.repsub == True:
            msg = MIMEMultipart()
            msg['Subject'] = 'Official SpellNOW! Notification! -- New Report'
            msg["From"] = formataddr((str(Header('SpellNOW! Support', 'utf-8')), 'support@spellnow.org'))
            msg["To"] = parent.email
            body_text = """Hello!\n\nThis is an Official SpellNOW! Notification. """ + userusing.first_name + """ has complete a vocabulary activity on SpellNOW! with a score of """ + request.POST["score"] + """. You can learn more details of this activity by visiting https://spellnow.org/report/""" + str(report_using.id) + """. Thank you, and we hope for your continued progress for the future.\n\nSincerely,\nSpellNOW! Support Team"""

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
    
    return render(request, "spell/vocab_finish.html", {
        "bar": "activities",
        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
        "active": "vocabit",
        "score": request.POST["score"]
    })

# Reports
@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def reports(request):
    userusing = Account.objects.get(username=request.user.username)

    if userusing.parent:
        if request.method == "POST":
            fun = Account.objects.get(pk=int(request.POST["child"]))
            print(fun)

            return render(request, "spell/reports.html", {
                "bar": "fullreports",
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "active": "reports",
                "reports": Report.objects.filter(specific=False, user=fun).order_by('-finished'),
                "ready": True,
                "child": request.POST["child"],
                "children": userusing.children.all(),
            })
        else:
            userusing = Account.objects.get(username=request.user.username)

            return render(request, "spell/reports.html", {
                "bar": "fullreports",
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "active": "reports",
                "children": userusing.children.all(),
            })
    else:
        return render(request, "spell/reports.html", {
            "bar": "fullreports",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "reports",
            "ready": True,
            "reports": Report.objects.filter(specific=False, user=request.user).order_by('-finished')
        })

@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def report(request, id):
    great = Account.objects.get(username=request.user.username)

    if great.parent:
        userusing = Account.objects.get(username=request.user.username)
        try:
            thingy = Report.objects.get(pk=id, specific=False)
            
            if thingy.user in great.children.all():
                used = Report.objects.filter(iid=id, specific=True)
                fnu = Report.objects.get(pk=id)

                if fnu.spelling:
                    bring = ReportDetail.objects.filter(report=fnu)

                    return render(request, "spell/report.html", {
                        "bar": "fullreports",
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
                    bring = VocabReportDetail.objects.filter(report=fnu)

                    return render(request, "spell/vocab_report.html", {
                        "bar": "fullreports",
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
        except:
            return render(request, "spell/error_404.html", {})
    else:
        userusing = Account.objects.get(username=request.user.username)
        if len(Report.objects.filter(pk=id, specific=False, user=userusing)) != 0:
            used = Report.objects.filter(iid=id, specific=True)
            fnu = Report.objects.get(pk=id)

            if fnu.spelling:
                bring = ReportDetail.objects.filter(report=fnu)

                return render(request, "spell/report.html", {
                    "bar": "fullreports",
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
                bring = VocabReportDetail.objects.filter(report=fnu)

                return render(request, "spell/vocab_report.html", {
                    "bar": "fullreports",
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

@login_required(login_url='/login')
@user_passes_test(locked, login_url='/subscribe')
def wordreports(request):
    userusing = Account.objects.get(username=request.user.username)

    if userusing.parent:
        if request.method == "POST":
            totals = []
            cool = 0
            repdet = ReportDetail.objects.filter(report__user__id=int(request.POST["child"]), report__specific = False).values_list('word', flat=True).distinct()

            for word in repdet:
                if len(ReportDetail.objects.filter(word=word)) > cool:
                    cool = len(ReportDetail.objects.filter(word=word))
                
                thing = {"word": word, "records": list(ReportDetail.objects.filter(word=word).values_list('result', flat=True)), "tags": list(Word.objects.get(word=word).tags.all().values_list('pk', flat=True))}
                totals.append(thing)
    
            alltags = ""

            for tag in Tag.objects.all():
                alltags += tag.name + "*..*"

            return render(request, "spell/wordreports.html", {
                "bar": "fullreports",
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "active": "wordreports",
                "ready": True,
                "totals": totals,
                "cool": cool,
                "child": request.POST["child"],
                "children": userusing.children.all(),
                "tags": Tag.objects.all(),
                "alltags": alltags,
            })
        else:
            userusing = Account.objects.get(username=request.user.username)

            return render(request, "spell/wordreports.html", {
                "bar": "fullreports",
                "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
                "active": "wordreports",
                "children": userusing.children.all(),
            })
    else:
        totals = []
        cool = 0
        repdet = ReportDetail.objects.filter(report__user=request.user, report__specific = False).values_list('word', flat=True).distinct()

        for word in repdet:
            if len(ReportDetail.objects.filter(word=word)) > cool:
                cool = len(ReportDetail.objects.filter(word=word))
            
            thing = {"word": word, "records": list(ReportDetail.objects.filter(word=word).values_list('result', flat=True)), "tags": list(Word.objects.get(word=word).tags.all().values_list('pk', flat=True))}
            totals.append(thing)

        alltags = ""

        for tag in Tag.objects.all():
            alltags += tag.name + "*..*"

        return render(request, "spell/wordreports.html", {
            "bar": "fullreports",
            "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
            "active": "wordreports",
            "ready": True,
            "totals": totals,
            "cool": cool,
            "tags": Tag.objects.all(),
            "alltags": alltags,
        })

# Profile

@login_required(login_url='/login')
def profile(request):
    account = Account.objects.get(username=request.user.username)
    actualparent = False
    if account.parent:
        for account in Account.objects.filter(parents=account.id):
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
            
            actualparent = True
    
    if account.parent or ConfirmReq.objects.filter(username=account.username, parent=None) or ((not ConfirmReq.objects.filter(username=account.username).exists()) and (not Account.objects.filter(children__in=[account]).exists())):
        actualparent = True

    return render(request, "spell/profile.html", {
        "bar": "",
        "active": "profilit",
        "question": Account.objects.get(username=request.user.username) if Account.objects.filter(username=request.user.username) else {"subscribed": True, "daysleft": 10},
        "actualparent": actualparent,
    })

@login_required(login_url='/login')
def deleteuser(request, id):
    userusing = Account.objects.get(username=request.user.username)
    student = Account.objects.get(pk=id)

    if userusing.parent:
        if student in userusing.children.all():
            student.delete()
            return HttpResponseRedirect(reverse("profile"))
        else:
            return render(request, "spell/error_404.html", {})
    elif ((not ConfirmReq.objects.filter(username=userusing.username).exists()) and (not Account.objects.filter(children__in=[userusing]).exists())):
        userusing.delete()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "spell/error_404.html", {})

@login_required(login_url='/login')
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
def changenotifs(request):
    userusing = Account.objects.get(username=request.user.username)
    prev = userusing.changenotifs

    total = ""

    try:
        cool = request.POST["repsub"]
        if cool == "checked":
            if userusing.repsub == False:
                total += "Report Notifications: On"
                userusing.repsub = True
    except:
        if userusing.repsub == True:
            total += "Report Notifications Notifications: Off"
            userusing.repsub = False

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

def informvalidation(request):
    return render(request, "spell/inform.html", {})

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