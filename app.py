import os
import datetime
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    client = MongoClient(os.environ.get("MONGODB_URI"))
    app.db = client.microblog
    app.secret_key = os.environ.get("SECRET_KEY")
    app.permanent_session_lifetime = datetime.timedelta(days=30)

    @app.route("/")
    def root():
        return redirect(url_for("home"))

    @app.route("/login/", methods=["GET", "POST"])
    def home():
        if request.method == "POST":
            remember = request.form.get("remember")
            if remember == "true":
                session.permanent = True
            else:
                session.permanent = False

            for user_id in app.db.login.find():
                if user_id["username"] == request.form['user'] and user_id["password"] == request.form["password"]:
                    session["user"] = user_id["username"]
                    return redirect(url_for("user"))

            return render_template("html/index.html")
        elif "user" in session:
            return redirect(url_for("user"))
        else:
            return render_template("html/index.html")

    @app.route("/user/", methods=["GET", "POST"])
    def user():
        name = session["user"]
        if "user" in session:
            if request.method == "POST":
                entry_content = request.form['content']
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
                for entry in app.db[name].find().limit(5).sort("date", -1)
            ]
            return render_template("html/home.html", entries=entries_with_date)
        else:
            return redirect(url_for("home"))

    @app.route("/user/recent/", methods=["GET", "POST"])
    def recent():
        if request.method == "GET":
            name = session["user"]
            page = request.args.get("page")
            if page is not None:
                page = int(page)
            else:
                page = 1
            count = app.db[name].count_documents({})
            page_count = 1
            for x in range(count):
                if (x + 1) % 10 == 0:
                    page_count += ((x+1) // 10)
            entries_with_date = [
                (entry["content"],
                 entry["date"],
                 datetime.datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%d %b"),
                 entry["_id"]
                 )
                for entry in app.db[name].find().skip((page - 1) * 10).limit(10 * page).sort("date", -1)
            ]
            return render_template("html/recent.html", entries=entries_with_date, links=page_count, page=page)
        elif request.method == "post":
            return redirect(url_for("recent"))

    @app.route("/logout/")
    def logout():
        session.pop("user", None)
        return redirect(url_for("home"))
    return app