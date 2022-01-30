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

    @app.route("/", methods=["GET", "POST"])
    def home():
        if request.method == "POST":
            username = request.form['user']
            password = request.form["password"]
            for user_id in app.db.login.find():
                if user_id["username"] == username and user_id["password"] == password:
                    return redirect(url_for("user", name=username))
                    
        return render_template("html/index.html")

    @app.route("/<name>/", methods=["GET", "POST"])
    def user(name):

        if request.method == "POST":
            entry_content = request.form.get('content')
            if entry_content is not None and len(entry_content) >= 2:
                formatted_date = datetime.date.today().strftime("%Y-%m-%d")
                app.db[name].insert_one({"content": entry_content, "date": formatted_date})
            else:
                pass

        entries_with_date = [
            (entry["content"],
             entry["date"],
             datetime.datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%d %b")
             )
            for entry in app.db[name].find().limit(5)
        ]

        return render_template("html/home.html", entries=entries_with_date, name=name)

    @app.route("/<name>/recent/", methods=["GET"])
    def recent(name):
        page = request.args.get("page")
        if page is not None:
            page = int(page)
        else:
            page = 1
        count = app.db[name].count_documents({})
        page_count = 1
        for x in range(count):
            # print(f"x = {x}")
            if (x + 1) % 10 == 0:
                page_count += ((x+1) // 10)
        entries_with_date = [
            (entry["content"],
             entry["date"],
             datetime.datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%d %b")
             )
            for entry in app.db[name].find().skip((page - 1) * 10).limit(10 * page)
        ]
        return render_template("html/recent.html", entries=entries_with_date, links=page_count, name=name, page=page)

    # @app.route("/<name>/recent/<page_count>", metho=["GET"])
    # def current_page(name, page_count):
    #     count = app.db[name].count_documents({})
    #     page_count = 1
    #     for x in range(count):
    #         print(f"x = {x}")
    #         if (x + 1) % 10 == 0:
    #             page_count = int(((x + 11) / 10))

    return app