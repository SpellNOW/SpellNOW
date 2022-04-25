from re import L
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Word, Tag
import csv
from django import forms
from django.core.files.storage import FileSystemStorage
import os
import requests
import json
from os.path import exists
import random
import smtplib

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
                
                if (stuff["hwi"]["hw"].replace("*", "")).lower() == word:
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
            final_audio += ("'" + audio[i] + "', ")
        else: 
            final_audio += ("'" + audio[i] + "']")
    
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
    if pin != "5823":
        request.session["pin"] = "UNCONFIRMED"
        return HttpResponseRedirect(reverse("index"))
    else:
        request.session["pin"] = "CONFIRMED"
        return HttpResponseRedirect(reverse("chooser"))

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
            new_origin = "<ol><li>" + row[2].lower() + "</li></ol>"
            new_def = "<ol><li>" + row[3].lower() + "</li></ol>"

            new = Word(word=new_word, speech = new_speech, origin = new_origin, definition = new_def, pronounce = ("*--*" + new_word))
            new.save()
    return HttpResponseRedirect(reverse("admin_panel"))

def categories(request):
    if "pin" not in request.session or request.session["pin"] != "CONFIRMED":
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "spell/categories.html", {
            "tag": Tag.objects.all()
        })

def make_tag(request):
    thing = request.POST["tag"]
    new = Tag(name=thing)
    new.save()
    return HttpResponseRedirect(reverse("categories"))

def ins_words_tag(request):
    nots = []
    already = []
    file = request.FILES["insert"]
    fs = FileSystemStorage()
    fs.save("spell/static/spell/insert-tags.csv", file)
    f = open("spell/static/spell/insert-tags.csv", "r")
    reader = csv.reader(f)
    next(reader)
    tag = Tag.objects.get(pk=int(request.POST["id"]))
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
    f.close()
    os.remove("spell/static/spell/insert-tags.csv")

    if len(nots) > 0:
        fields = ['Words']
            
        # writing to csv file 
        with open("spell/static/spell/CreateWords.csv", 'w', newline="") as csvfile:
            csvwriter = csv.writer(csvfile) 
            csvwriter.writerow(fields)
            
            for thingy in nots:
                rows = [thingy]
                csvwriter.writerow(rows)

    if len(nots) > 0 or len(already) > 0:
        return render(request, "spell/ins-error.html", {
            'already': already,
            'nots': nots,
        })
    else:
        return HttpResponseRedirect(reverse("categories"))

def del_words_tag(request):
    nots = []
    file = request.FILES["del"]
    fs = FileSystemStorage()
    fs.save("spell/static/spell/delete-tags.csv", file)
    f = open("spell/static/spell/delete-tags.csv", "r")
    reader = csv.reader(f)
    next(reader)
    tag = Tag.objects.get(pk=int(request.POST["id"]))
    for row in reader:
        final = row[0].lower()
        
        if not tag.words.filter(word=final):
            nots.append(final)
        else:
            word = Word.objects.get(word=final)
            tag.words.remove(word)
            tag.save()
    f.close()
    os.remove("spell/static/spell/delete-tags.csv")

    if len(nots) > 0:
        return render(request, "spell/del-error.html", {
            'nots': nots,
        })
    else:
        return HttpResponseRedirect(reverse("categories"))

def chooser(request):
    if "pin" not in request.session or request.session["pin"] != "CONFIRMED":
        return HttpResponseRedirect(reverse("index"))
    else:
        words = Word.objects.all()
        return render(request, "spell/chooser.html")

def delete_words(request):
    nots = []
    file = request.FILES["deleter"]
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
        return render(request, "spell/del-words-err.html", {
            'nots': nots,
        })
    else:
        return HttpResponseRedirect(reverse("admin_panel"))

def delete_tag(request, id):
    tag = Tag.objects.get(pk=id)
    tag.delete()
    return HttpResponseRedirect(reverse("categories"))

def start(request):
    total = ""
    for tag in Tag.objects.all():
        total += (", " + tag.name)
    total += ", *..*"

    return render(request, "spell/start.html", {
        "tags": Tag.objects.all(),
        "total": total,
        "number": len(Word.objects.all())
    })

def spell(request):
    if request.method == "POST":
        thing = request.POST["tags"]
        tags = thing.split(", ")
        tags.remove('')
        allwords = []

        for tag in tags:
            if not tag == "*..*":
                right = Tag.objects.get(name=tag)
                for word in right.words.all():
                    if not word in allwords:
                        allwords.append(word)
            else:
                for word in Word.objects.all():
                    is_tagged = False
                    for tag in Tag.objects.all():
                        if word in tag.words.all():
                            is_tagged = True
                    if not is_tagged:
                        if not word in allwords:
                            allwords.append(word)
        
        if int(len(allwords)) < int(request.POST["numwords"]) or int(len(tags)) > int(request.POST["numwords"]):
            total = ""
            for tag in Tag.objects.all():
                total += (", " + tag.name)
            total += ", *..*"

            return render(request, "spell/start.html", {
                "tags": Tag.objects.all(),
                "total": total,
                "number": len(Word.objects.all()),
                "message": "Invalid Word Count"
            })
        else:
            allspeechs = []
            allorigins = []
            alldefs = []
            allprons = ""
            fines = []
            count = 0
            using = 0
            thingybob = ""
            nogo = False
            i = 0

            for i in range(int(request.POST["numwords"])):
                while True:   
                    nogo = False
                    if not tags[count] == "*..*":
                        lll = Tag.objects.get(name=tags[count])
                        last = lll.words.all()
                        currently = []

                        for asdf in last:
                            currently.append(asdf.word)

                        while True:
                            using = random.randint(0, (len(last) - 1))
                            thingybob = last[using]
                            currently.remove(thingybob.word)
                            if (not thingybob.word in fines):
                                break
                            elif len(last) == 0:
                                nogo = True
                                break
                    else:
                        options = []
                        for word in Word.objects.all():
                            is_tagged = False
                            for tag in Tag.objects.all():
                                if word in tag.words.all():
                                    is_tagged = True
                            if not is_tagged:
                                options.append(word)
                        
                        while True:
                            using = random.randint(0, (len(options) - 1))
                            thingybob = options[using]
                            options.remove(thingybob)
                            if (not thingybob.word in fines):
                                break
                            elif len(options) == 0:
                                nogo = True
                                break

                    if not nogo:
                        fines.append(thingybob.word)
                        right = request.POST["chooser"]

                        if "Part of Speech" in right:
                            allspeechs.append(thingybob.speech)
                        if "Language of Origin" in right:
                            allorigins.append(thingybob.origin)
                        if "Definition" in right:
                            alldefs.append(thingybob.definition)
                        
                        if (count + 1) == int(request.POST["numwords"]):
                            allprons += thingybob.pronounce
                        else:
                            allprons += (thingybob.pronounce + " || ")
                        
                        if count == (len(tags) - 1):
                            count = 0
                        else:
                            count += 1
                        
                        break
                    else:
                        if count == (len(tags) - 1):
                            count = 0
                        else:
                            count += 1
            
            return render(request, "spell/spell.html", {
                "words": fines,
                "speech": allspeechs,
                "origin": allorigins,
                "definition": alldefs,
                "prons": allprons,
                "tags": Tag.objects.all()
            })

def finish(request):
    tags_rep = request.POST["new_tags"]
    tags = tags_rep.split("[]")
    tags.remove("")
    
    words_rep = request.POST["add_words"]
    added_words = words_rep.split("[]")
    length = (len(added_words) - 1)
    count = 0

    for tag in tags:
        new = Tag(name=tag)
        new.save()
    
    for word in added_words:
        if not count == length:
            cool = word.split("||")
            bad = Tag.objects.get(name=cool[0])
            word = Word.objects.get(word=cool[1])
            bad.words.add(word)
            bad.save()
            count += 1

    gmail_user = 'turboluckyc@gmail.com'
    gmail_password = 'ibwwfiwlmivwwfkd'
    sent_from = "SpellNOW!"
    to = ['chauhanl@mcvts.net']
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
    
    return render(request, "spell/score.html", {
        "score": request.POST["score"]
    })