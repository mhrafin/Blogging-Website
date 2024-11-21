import os
import smtplib
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("GMAIL_APP_PASS")


RES = requests.get("https://api.npoint.io/bd19e496786f829612b2")
ALL_POSTS = RES.json()

TODAY = str(datetime.now().date())
YEAR = str(datetime.now().year)

app = Flask(__name__)


def send_email(message):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=EMAIL, password=PASSWORD)
        connection.sendmail(
            from_addr=EMAIL,
            to_addrs=EMAIL,
            msg=f"Subject:Contacting From Raf Blogs\n\n{message}",
        )


@app.route("/")
def home():
    return render_template("index.html", posts=ALL_POSTS, today=TODAY)


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact_page():
    if request.method == "POST":
        data = request.form
        print(data["name"])
        print(data["email"])
        print(data["phone"])
        print(data["message"])
        message = f"Name: {data['name']}\nEmail: {data['email']}\nPhone: {data['phone']}\nMessage: {data['message']}"
        send_email(message=message)
        return render_template("contact_simple.html", msg="Success")

    return render_template("contact_simple.html")


@app.route("/post/<int:id>")
def post_page(id):
    clicked_post = None
    for post in ALL_POSTS:
        if post["id"] == id:  # Assuming each post has an 'id' field
            clicked_post = post
            break
    return render_template("post.html", post=clicked_post, today=TODAY)


if __name__ == "__main__":
    app.run(debug=True)
