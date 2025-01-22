import os
from datetime import date

import requests as req
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import email_sender

load_dotenv()

my_email = os.getenv("MY_EMAIL")
my_password = os.getenv("MY_PASSWORD")

current_year = date.today().year
data_url = "https://api.npoint.io/ee84059f6d2a9704021f"


# Initialize Flask-Sqlalchemy
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)

# Configure the flask-sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db.init_app(app)


# Define Models
class Post(db.Model):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )  # If not work use Integer on mapped_column
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)
    


# Create the Tables
with app.app_context():
    db.create_all()


def send_msg(name: str, email: str, phone: str, msg: str):
    sender = email_sender.EmailSender(
        smtp_host="smtp.gmail.com", sender_email=my_email, sender_password=my_password
    )
    sender.send_email(
        recipient_email=my_email,
        subject=f"Message from {name}!",
        email_body=f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {msg}",
    )


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
        send_msg(name=name, email=email, phone=phone, msg=message)
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
