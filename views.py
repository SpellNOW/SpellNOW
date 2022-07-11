from operator import ilshift
from re import L
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Account, Word, Tag, Report, Root
import csv
from django import forms
from django.core.files.storage import FileSystemStorage
import os
import requests
import json
from os.path import exists
from django.db.models import Q
import random
import smtplib
from django.contrib.auth.decorators import login_required
from string import ascii_lowercase

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

# Create your views here.

# Homepage
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("admin_panel"))
    else:
        return render(request, "spell/index.html")

# Authorization pages
def login(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect(reverse("admin_panel"))
        else:
            return render(request, "spell/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "spell/login.html")

def register(request):
    if request.method == "POST":
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        # Attempt to create new user
        try:
            user = Account.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            user.save()
        except IntegrityError:
            return render(request, "spell/register.html", {
                "message": "Username already taken."
            })
        
        auth_login(request, user)
        return HttpResponseRedirect(reverse("admin_panel"))
    else:
        return render(request, "spell/register.html")

@login_required(login_url='/login')
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse("index"))

# Dashboard
@login_required(login_url='/login')
def admin_panel(request):
    return render(request, "spell/dashboard.html")

# Libraries
@login_required(login_url='/login')
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
                        "tags": Tag.objects.all(),
                        "results": results
                    })
                except ObjectDoesNotExist:
                    return render(request, "spell/word_library.html", {
                        "tags": Tag.objects.all(),
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
                                "tags": Tag.objects.all(),
                                "results": results
                            })
                        else:
                            return render(request, "spell/word_library.html", {
                                "tags": Tag.objects.all(),
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
                                    "tags": Tag.objects.all(),
                                    "results": set(results)
                                })
                            else:
                                return render(request, "spell/word_library.html", {
                                    "tags": Tag.objects.all(),
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
                            print("HEEEERE")
                            return render(request, "spell/word_library.html", {
                                "tags": Tag.objects.all(),
                                "results": results
                            })
                        else:
                            return render(request, "spell/word_library.html", {
                                "tags": Tag.objects.all(),
                                "message": True
                            })
                else:
                    results = Word.objects.filter(word__contains=word)
                    
                    if len(results) > 0:
                        return render(request, "spell/word_library.html", {
                            "tags": Tag.objects.all(),
                            "results": results
                        })
                    else:
                        return render(request, "spell/word_library.html", {
                            "tags": Tag.objects.all(),
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
                            "tags": Tag.objects.all(),
                            "results": results
                        })
                    else:
                        return render(request, "spell/word_library.html", {
                            "tags": Tag.objects.all(),
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
                            "tags": Tag.objects.all(),
                            "results": results
                        })
                    else:
                        return render(request, "spell/word_library.html", {
                            "tags": Tag.objects.all(),
                            "message": True
                        })
            else:
                results = Word.objects.all()
                
                if len(results) > 0:
                    return render(request, "spell/word_library.html", {
                        "tags": Tag.objects.all(),
                        "results": results
                    })
                else:
                    return render(request, "spell/word_library.html", {
                        "tags": Tag.objects.all(),
                        "message": True
                    })
    else:
        return render(request, "spell/word_library.html", {
            "tags": Tag.objects.all()
        })

@login_required(login_url='/login')
def tag_library(request):
    if request.method == "POST":
        try:
            thing = request.POST["tag"]
            if not (("---" in thing) or ('"' in thing) or ("'" in thing) or ("*..*" in thing) or (", " in thing)):
                new = Tag(name=thing)
                new.save()
                return render(request, "spell/tag_library.html", {
                    "tags": Tag.objects.all()
                })
            else:
                return render(request, "spell/tag_library.html", {
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
                    "tags": Tag.objects.all()
                })
            else:
                return render(request, "spell/tag_library.html", {
                    "tags": Tag.objects.all(),
                    "namerror": int(request.POST["tagid"])
                })
    else:
        return render(request, "spell/tag_library.html", {
            "tags": Tag.objects.all()
        })

# Word Changes
@login_required(login_url='/login')
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
            bad.words.remove(time)
            bad.save()
            time.tags.remove(bad)
            time.save()
        else:
            bad = Tag.objects.get(pk=int(thing[1]))
            bad.words.add(time)
            bad.save()
            time.tags.add(bad)
            time.save()
    
    return HttpResponseRedirect(reverse("word_library"))

# Tag Changes
@login_required(login_url='/login')
def delete_tag(request, id):
    tag = Tag.objects.get(pk=id)
    tag.delete()
    return HttpResponseRedirect(reverse("tag_library"))

# Import
@login_required(login_url='/login')
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
                    'nots': nots,
                    'message1': "SpellNOW!&trade; was unable to add these words to your list:",
                    "download": True
                })
            elif len(already) > 0 and not len(nots) > 0:
                return render(request, "spell/error.html", {
                    'already': already,
                    'message2': "SpellNOW!&trade; found these words already in your list:"
                })
            elif len(already) > 0 and len(nots) > 0:
                return render(request, "spell/error.html", {
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
                    'words': new_word,
                    'already': already,
                    "error": True,
                    'message2': "SpellNOW!&trade; found these words already in your list:",
                })
            else:
                return render(request, "spell/custom.html", {
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
                
                if tag.words.filter(word=final):
                    already.append(final)
                if not Word.objects.filter(word=final):
                    nots.append(final)
                else:
                    word = Word.objects.get(word=final)
                    tag.words.add(word)
                    tag.save()
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
                    'already': already,
                    'nots': nots,
                    "message1": "SpellNOW!&trade; was unable to tag these words because they do not exist:",
                    "message2": "SpellNOW!&trade; was unable to tag these words because they are already tagged:",
                    "download": True
                })
            elif len(nots) > 0:
                return render(request, "spell/error.html", {
                    'nots': nots,
                    "message1": "SpellNOW!&trade; was unable to tag these words because they do not exist:",
                    "download": True
                })
            elif len(already) > 0:
                return render(request, "spell/error.html", {
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
                
                if not tag.words.filter(word=final):
                    nots.append(final)
                else:
                    word = Word.objects.get(word=final)
                    tag.words.remove(word)
                    tag.save()
                    word.tags.remove(tag)
                    word.save()
                    usage = Tag.objects.filter(words__id=word.pk)
                    if len(usage) == 0:
                        word.tagged = False
                        word.save()
            f.close()
            os.remove("spell/static/spell/delete-tags.csv")

            if len(nots) > 0:
                return render(request, "spell/error.html", {
                    'nots': nots,
                    "message1": "SpellNOW!&trade; was unable to untag these words because they are not tagged:",
                })
            else:
                return HttpResponseRedirect(reverse("tag_library"))
    else:
        return render(request, "spell/import.html", {
            "tags": Tag.objects.all()
        })

@login_required(login_url='/login')
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
def start(request):
    return render(request, "spell/spelling_start.html", {
        "tags": Tag.objects.all(),
        "number": len(Word.objects.all())
    })

@login_required(login_url='/login')
def spell(request):
    if request.method == "POST":
        tags = request.POST.getlist('*..*tags*..*')

        print("========================Verifying word amount========================")
        results = []
        fun = []
        for i in tags:
            if not i == "*..*":
                fun.append(i)
        
        if "*..*" in tags:
            results.extend(list((Word.objects.filter(Q(tags__name__in=fun) | Q(tagged=False))).distinct()))
        else:
            results.extend(list((Word.objects.filter(tags__name__in=fun)).distinct()))
        
        if int(len(results)) < int(request.POST["numwords"]) or int(len(tags)) > int(request.POST["numwords"]):
            return render(request, "spell/spelling_start.html", {
                "tags": Tag.objects.all(),
                "number": len(Word.objects.all()),
                "message": "Invalid Word Count"
            })
        else:
            gag = []
            fines = []
            allspeechs = []
            alldefs = ""
            allorigins = ""
            allprons = ""
            order = ""
            final_last_total = 0
            final_tags = ""
            hllg = []
            tags_used = ""
            random.shuffle(results)
            results = results[:(int(request.POST["numwords"]))]

            i = 0
            print("========================Getting Words========================")
            for word in results:
                tag = ""
                for cooly in set(word.tags.all()):
                    if cooly.name in fun:
                        tag = cooly.name
                        break
                
                order += tag + ", "

                if not tag in hllg:
                    hllg.append(tag)
                    tags_used += (tag + ", ")

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
                        
                usage = Tag.objects.filter(words__id=word.id)

                badder = 0
                for bad in usage:
                    if badder == (len(usage) - 1):
                        final_tags += bad.name
                    else:
                        final_tags += (bad.name + "<>")
                    badder += 1
                     
                if not final_last_total == int(request.POST["numwords"]):
                    final_tags += "><"
                
                i += 1
            
            return render(request, "spell/spelling_spell.html", {
                "words": fines,
                "speech": allspeechs,
                "origin": allorigins,
                "definition": alldefs,
                "prons": allprons,
                "tags": Tag.objects.all(),
                "order": order,
                "final_tags": final_tags,
                "tags_used": tags_used
            })

@login_required(login_url='/login')
def finish(request):
    tags_rep = request.POST["new_tags"]
    tags = tags_rep.split("[]")
    tags.remove("")
    
    words_rep = request.POST["add_words"]
    added_words = words_rep.split("[]")
    added_words.remove("")

    for tag in tags:
        new = Tag(name=tag)
        new.save()
    
    for word in added_words:
        cool = word.split("||")
        if (cool[0][0] + cool[0][1] + cool[0][2]) == "---":
            bad = Tag.objects.get(name=(cool[0].replace("---", "")))
            word = Word.objects.get(word=cool[1])
            bad.words.remove(word)
            bad.save()
            word.tags.remove(bad)
            word.save()
            usage = Tag.objects.filter(words__id=word.pk)
            if len(usage) == 0:
                word.tagged = False
                word.save()
        else:
            bad = Tag.objects.get(name=(cool[0].replace("---", "")))
            word = Word.objects.get(word=cool[1])
            bad.words.add(word)
            bad.save()
            word.tags.add(bad)
            word.tagged = True
            word.save()

    order_in = request.POST["order"]
    order = order_in.split(", ")
    order.remove("")

    tags_used = request.POST["tags_used"]
    total_gags = tags_used.split(", ")
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
    new = Report(tags=tags_used, correct=thingy[0], total=(thingy[1]), percent=(int((int(thingy[0])/int(thingy[1]))*100)), specific=False)
    new.save()
    id_using = new.id

    for righter in total_gags:
        if not righter == "*..*":
            nice = 0
            cool = 0
            abhi = 0
            for ishaan in order:
                if ishaan == righter:
                    nice += int(correct_array[cool])
                    abhi += 1
                cool += 1
            
            if abhi != 0:
                new = Report(tags=righter, correct=nice, total=abhi, percent=(int((nice/abhi)*100)), specific=True, iid=id_using)
                new.save()
    
    
    with open("spell/static/spell/reports/report_" + str(id_using) + ".csv", 'w', newline="") as csvfile:
        csvwriter = csv.writer(csvfile) 
        fields = []
        count = 1
        good = 0

        for i in range(len(added_words)):
            added_words[i] = (added_words[i]).split("||")

        for tmp in words:
            actions = ""
            if int(correct_array[count - 1]) == 0:
                while True:
                    if not ((len(added_words) == 0) or (len(added_words) == good)):
                        if added_words[good][1] == words[count - 1]:
                            if (added_words[good][0][0] + added_words[good][0][1] + added_words[good][0][2]) == "---":
                                actions += ("'" + words[count - 1] + "' removed from tag '" + added_words[good][0].replace("---", "") +"'<br><br>")
                            else:
                                actions += ("'" + words[count - 1] + "' added to tag '" + added_words[good][0].replace("---", "") +"'<br><br>")
                            good += 1
                        else:
                            break
                    else:
                        break
                if not order[count - 1] == "*..*":
                    fields = [count, order[count - 1], words[count - 1], atts[count - 1], "INCORRECT", actions, (str(int(int(time[count - 1])/60)) + " min. " + str(int(time[count - 1]) - int(int(int(time[count - 1])/60)*60)) + " sec.")]
                else:
                    fields = [count, "Untagged", words[count - 1], atts[count - 1], "INCORRECT", actions, (str(int(int(time[count - 1])/60)) + " min. " + str(int(time[count - 1]) - int(int(int(time[count - 1])/60)*60)) + " sec.")]
            else:
                actions = ""
                while True:
                    if not ((len(added_words) == 0) or (len(added_words) == good)):
                        if added_words[good][1] == words[count - 1]:
                            if (added_words[good][0][0] + added_words[good][0][1] + added_words[good][0][2]) == "---":
                                actions += ("'" + words[count - 1] + "' removed from tag '" + added_words[good][0].replace("---", "") +"'<br><br>")
                            else:
                                actions += ("'" + words[count - 1] + "' added to tag '" + added_words[good][0].replace("---", "") +"'<br><br>")
                            good += 1
                        else:
                            break
                    else:
                        break
                if not order[count - 1] == "*..*":
                    fields = [count, order[count - 1], words[count - 1], atts[count - 1], "CORRECT", actions, (str(int(int(time[count - 1])/60)) + " min. " + str(int(time[count - 1]) - int(int(int(time[count - 1])/60)*60)) + " sec.")]
                else:
                    fields = [count, "Untagged", words[count - 1], atts[count - 1], "CORRECT", actions, (str(int(int(time[count - 1])/60)) + " min. " + str(int(time[count - 1]) - int(int(int(time[count - 1])/60)*60)) + " sec.")]
            count += 1
            csvwriter.writerow(fields)
    
    gmail_user = 'turboluckyc@gmail.com'
    gmail_password = 'ibwwfiwlmivwwfkd'
    sent_from = "SpellNOW!"
    to = ['naveensc@gmail.com']
    subject = 'Official SpellNOW! Notification!'
    body = 'This is an Official SpellNOW! Notification...\n\nAnjali has recently complete a spelling activity on SpellNOW! with a score of ' + request.POST["score"] +".\n\nThank you."

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)       
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
    except Exception as ex:
        pass
    
    return render(request, "spell/spelling_finish.html", {
        "score": request.POST["score"]
    })


# Reports
@login_required(login_url='/login')
def reports(request):
    return render(request, "spell/reports.html", {
        "reports": Report.objects.filter(specific=False).order_by('-finished')
    })

@login_required(login_url='/login')
def report(request, id):
    tags = Report.objects.filter(iid=id, specific=True)
    fnu = Report.objects.get(pk=id)
    total = []
    bring = []

    for tag in tags:
        great = {"brian": tag.tags, "correct": tag.correct, "total": tag.total, "percent": tag.percent}
        total.append(great)
    
    f = open("spell/static/spell/reports/report_" + str(id) + ".csv", "r")
    reader = csv.reader(f)
    for row in reader:
        abhay = {"number": row[0], "tag": row[1], "word": row[2], "attempt": row[3], "result": row[4], "actions": row[5], "time": row[6]}
        bring.append(abhay)
    f.close()
    
    return render(request, "spell/report.html", {
        "tags": total,
        "title": fnu.finished,
        "correct": fnu.correct,
        "total": fnu.total,
        "percent": fnu.percent,
        "records": bring,
    })