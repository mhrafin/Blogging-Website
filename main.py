from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import requests as req

current_year = date.today().year
data_url = "https://api.npoint.io/ee84059f6d2a9704021f"

app = Flask(__name__)


@app.route("/")
def home():
    res = req.get(data_url)
    data = res.json()

    return render_template("index.html", current_year=current_year, posts=data)


@app.route("/about")
def about():
    return render_template("about.html", current_year=current_year)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        print(name, email, phone, message)
        return render_template("contact.html", current_year=current_year, msg_sent=True)
    return render_template("contact.html", current_year=current_year, msg_sent=False)


@app.route("/post/<int:id>")
def get_post(id):
    res = req.get(data_url)
    data = res.json()
    the_post = None
    for post in data:
        if post["id"] == id:
            the_post = post
    return render_template("post.html", current_year=current_year, post=the_post)


if __name__ == "__main__":
    app.run(debug=True)
