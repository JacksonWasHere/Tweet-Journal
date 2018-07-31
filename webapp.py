import os
import json
from datetime import datetime
from flask import Flask, url_for, render_template, request, Markup

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("home.html")

@app.route("/add_entry")
def add_new():
    return render_template("add_entry.html")

@app.route("/upload")
def upload():
    with open("notes.json") as f:
        data=json.load(f)
    new_note=request.args["new_entry"]
    new_entry={
        "date":{
            "year":str(datetime.now().year),
            "month":str(datetime.now().month),
            "day":str(datetime.now().day),
            "time":str(format(datetime.now().time()))
          },
        "note":new_note,
        "references":[]
    }
    data["jackson"]["notes"].append(new_entry)
    with open("notes.json", 'w') as outfile:
        json.dump(data, outfile, indent=4)
    return "<meta http-equiv='refresh' content='0; url=/entries' />"

def format_note(text,links):
    indexes = []
    replace_inds = []
    for char_ind in range(len(text)):
        if text[char_ind]=="<" or text[char_ind]==">":
            if char_ind>0 and not text[char_ind-1]=="*":
                indexes.append(char_ind)
            else:
                replace_inds.append(char_ind-1)

    for i in replace_inds:
        text=text[:i]+"\f"+text[i+1:]

    print(text)
    print(indexes)

    new_text = []
    if len(indexes)==0:
        new_text = [text]
    else:
        previous = 0
        for i in indexes:
            new_text.append(text[previous:i])
            previous = i+1

    print(new_text)

    out = ""
    link_num=0
    isLink = False
    for section in new_text:
        if isLink:
            out += "<a href='/entries/"+links[link_num]+"'>"+section+"</a>"
            link_num+=1
        else:
            out += section
        isLink = not isLink
    return out


def get_note(note_path,data):

    note_path=note_path.split(",")

    item = data[note_path[0]][note_path[1]][int(note_path[2])]

    date = item["date"]
    date_formatted = "<h3>On "+str(date["month"])+"/"+str(date["day"])+"/"+str(date["year"])+" at "+str(date["time"])+" you said:</h3>"

    note = item["note"]
    note_formatted = format_note(note,item["references"])

    return date_formatted + note_formatted

@app.route("/entries")
def entries():
    with open("notes.json") as f:
        data=json.load(f)
    out=""
    for item in range(len(data["jackson"]["notes"])):
        date=data["jackson"]["notes"][item]["date"]
        date_formatted = str(date["month"])+"/"+str(date["day"])+"/"+str(date["year"])
        out+="<a href='/entries/jackson,notes,"+str(item)+"'>entry from "+date_formatted+"</a><br>"
    return render_template("entries.html",notes=Markup(out))

@app.route("/entries/<entry_url>")
def display_note(entry_url):
    with open("notes.json") as f:
        data=json.load(f)
    return render_template("entry.html",note=Markup(get_note(entry_url,data)))

if __name__ == "__main__":
    app.run(port=5000)
