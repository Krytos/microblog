import datetime
from pymongo import MongoClient
from flask import Flask, render_template, request


def create_app():
    app = Flask(__name__)
    client = MongoClient("mongodb+srv://Krytos:301018905@microblog-app.5h6by.mongodb.net/microblog.entries?retryWrites=true&w=majority")
    app.db = client.microblog
    entries = []

    @app.route('/', methods=['GET', "POST"])
    def home():  # put application's code here
        today = datetime.date.today()
        time = datetime.datetime.today()
        months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }

        formatted_date = datetime.date.today().strftime("%Y-%m-%d")

        if request.method == "POST":
            entry_content = request.form.get('content')
            app.db.entries.insert_one({"content": entry_content, "date": formatted_date})

        entries_with_date = [
            (entry["content"],
             entry["date"],
             datetime.datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%d %b")
             )
            for entry in app.db.entries.find()
        ]
        return render_template("html/home.html", entries=entries_with_date)

    return app
