import os
import datetime
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    client = MongoClient(os.environ.get("MONGODB_URI"))
    app.db = client.microblog
    entries = []

    @app.route("/", methods=["GET", "POST"])
    def home():
        if request.method == "POST":
            username = request.form['user']
            password = request.form["password"]
            for user_id in app.db.login.find():
                print(user_id["username"], username, user_id["password"], password)
                if user_id["username"] == username and user_id["password"] == password:
                    return redirect(url_for("user", name=username))
                    
        return render_template("html/index.html")

    @app.route("/<name>/", methods=["GET", "POST"])
    def user(name):

        if request.method == "POST":
            entry_content = request.form.get('content')
            formatted_date = datetime.date.today().strftime("%Y-%m-%d")
            app.db[name].insert_one({"content": entry_content, "date": formatted_date})

        entries_with_date = [
            (entry["content"],
             entry["date"],
             datetime.datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%d %b")
             )
            for entry in app.db[name].find()
        ]
        return render_template("html/home.html", entries=entries_with_date)

    return app
