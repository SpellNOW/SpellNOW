from re import L
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Word, Tag, Report
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
    
    if not error:
        for stuff in info:
            if (stuff["hwi"]["hw"].replace("*", "")).lower() == word:
                try:
                    stuff["fl"].capitalize()
                except KeyError:
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
    
    new = Word(word=word, speech = final_parts, origin = final_origin, definition = final_right, pronounce = final_audio, tagged = False)
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
    if (("pin" not in request.session) or (request.session["pin"] != "CONFIRMED")):
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
    if (("pin" not in request.session) or (request.session["pin"] != "CONFIRMED")):
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "spell/categories.html", {
            "tag": Tag.objects.all()
        })

def make_tag(request):
    thing = request.POST["tag"]
    if not (("---" in thing) or ('"' in thing) or ("'" in thing) or ("*..*" in thing) or (", " in thing)):
        new = Tag(name=thing)
        new.save()
        return HttpResponseRedirect(reverse("categories"))
    else:
        return render(request, "spell/categories.html", {
            "tag": Tag.objects.all(),
            "error": True
        })

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
            word.tagged = True
            word.save()
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
            usage = Tag.objects.filter(words__id=word.pk)
            if len(usage) == 0:
                word.tagged = False
                word.save()
    f.close()
    os.remove("spell/static/spell/delete-tags.csv")

    if len(nots) > 0:
        return render(request, "spell/del-error.html", {
            'nots': nots,
        })
    else:
        return HttpResponseRedirect(reverse("categories"))

def chooser(request):
    if (("pin" not in request.session) or (request.session["pin"] != "CONFIRMED")):
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
        order = ""
        thing = request.POST["tags"]
        tags = thing.split(", ")
        tags.remove('')
        allwords = []
        
        tag_count = 0
        length_tags = len(tags)
        print("========================Generating Word List========================")
        for tag in tags:
            if not tag == "*..*":
                word_count = 0
                print("Looking through tag '" + tag + "'..........")
                right = Tag.objects.get(name=tag)
                word_length = len(right.words.all())
                for word in right.words.all():
                    if not word in allwords:
                        allwords.append(word)
                    word_count += 1
                    print("Looked through word " + str(word_count) + "/" + str(word_length) + "...")
                tag_count += 1
                print("Looked through tag '" + tag + "'.........." + str(tag_count) + "/" + str(length_tags))
            else:
                word_count = 0
                print("Looked through untagged words...")
                word_length = len(Word.objects.all())
                for word in Word.objects.all():
                    if word.tagged == False:
                        if not word in allwords:
                            allwords.append(word)
                    word_count += 1
                    print("Looked through word " + str(word_count) + "/" + str(word_length) + "...")
                tag_count += 1
                print("Looked through untagged words.........." + str(tag_count) + "/" + str(length_tags))
        
        print("========================Verifying word amount========================")
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
            final_last_total = 0
            final_tags = ""

            print("========================Choosing words========================")
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
                            if not len(currently) == 0:
                                using = random.randint(0, (len(currently) - 1))
                                if (not currently[using] in fines):
                                    thingybob = Word.objects.get(word=currently[using])
                                    order += (lll.name + ", ")
                                    break
                                elif len(currently) == 0:
                                    nogo = True
                                    break
                                currently.remove(currently[using])
                            else:
                                nogo = True
                                break
                    else:
                        options = []
                        for asdf in Word.objects.filter(tagged=False):
                            options.append(asdf)
                        
                        while True:
                            using = random.randint(0, (len(options) - 1))
                            thingybob = options[using]
                            options.remove(thingybob)
                            if (not thingybob.word in fines):
                                order += ("*..*, ")
                                break
                            elif len(options) == 0:
                                nogo = True
                                break

                    if not nogo:
                        fines.append(thingybob.word)

                        allspeechs.append(thingybob.speech)
                        allorigins.append(thingybob.origin)
                        alldefs.append(thingybob.definition)
                        
                        if (count + 1) == int(request.POST["numwords"]):
                            allprons += thingybob.pronounce
                        else:
                            allprons += (thingybob.pronounce + " || ")
                        
                        if count == (len(tags) - 1):
                            count = 0
                        else:
                            count += 1
                        
                        final_last_total += 1
                        print("Got word " + str(final_last_total) + " of " + request.POST["numwords"])
                        
                        usage = Tag.objects.filter(words__id=thingybob.id)
                        badder = 0

                        for bad in usage:
                            if badder == (len(usage) - 1):
                                final_tags += bad.name
                            else:
                                final_tags += (bad.name + "<>")
                        
                        if not final_last_total == int(request.POST["numwords"]):
                            final_tags += "><"

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
                "tags": Tag.objects.all(),
                "tags_used": thing,
                "order": order,
                "final_tags": final_tags
            })

def finish(request):
    tags_rep = request.POST["new_tags"]
    tags = tags_rep.split("[]")
    tags.remove("")
    
    words_rep = request.POST["add_words"]
    added_words = words_rep.split("[]")
    added_words.remove("")

    for tag in tags:
        print(tag)
        new = Tag(name=tag)
        new.save()
    
    for word in added_words:
        cool = word.split("||")
        if (cool[0][0] + cool[0][1] + cool[0][2]) == "---":
            bad = Tag.objects.get(name=(cool[0].replace("---", "")))
            word = Word.objects.get(word=cool[1])
            bad.words.remove(word)
            bad.save()
            usage = Tag.objects.filter(words__id=word.pk)
            if len(usage) == 0:
                word.tagged = False
                word.save()
        else:
            bad = Tag.objects.get(name=(cool[0].replace("---", "")))
            word = Word.objects.get(word=cool[1])
            bad.words.add(word)
            bad.save()
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
                    if not ((len(added_words) == 0) or (len(added_words) == (good + 1))):
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
                    if not ((len(added_words) == 0) or (len(added_words) == (good + 1))):
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
    
    return render(request, "spell/score.html", {
        "score": request.POST["score"]
    })

def reports(request):
    if (("pin" not in request.session) or (request.session["pin"] != "CONFIRMED")):
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "spell/report.html", {
            "reports": Report.objects.filter(specific=False)
        })

def report(request, id):
    if (("pin" not in request.session) or (request.session["pin"] != "CONFIRMED")):
        return HttpResponseRedirect(reverse("index"))
    else:
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
        
        return render(request, "spell/each.html", {
            "tags": total,
            "title": fnu.finished,
            "correct": fnu.correct,
            "total": fnu.total,
            "percent": fnu.percent,
            "records": bring,
        })
