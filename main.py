import os
from datetime import date

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request
from flask_ckeditor import CKEditor, CKEditorField
from flask_ckeditor.utils import cleanify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import URL, DataRequired

import email_sender

SECRET_KEY = os.urandom(32)

load_dotenv()

my_email = os.getenv("MY_EMAIL")
my_password = os.getenv("MY_PASSWORD")

today = date.today().strftime("%d %B %Y")
current_year = date.today().year
data_url = "https://api.npoint.io/ee84059f6d2a9704021f"

# Create the app
app = Flask(__name__)
## Configure the app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SECRET_KEY"] = SECRET_KEY


# Initialize Flask-Sqlalchemy
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


## Define Models
class Post(db.Model):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)


### Create the Tables
with app.app_context():
    db.create_all()

# Initialize flask-ckeditor
ckeditor = CKEditor(app)


# Forms
class NewPostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    img_url = URLField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


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
    posts = db.session.execute(db.select(Post)).scalars()

    return render_template("index.html", current_year=current_year, posts=posts)


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


@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    form = NewPostForm()
    # print("CKEditor body:", request.form.get('body'))
    # print("Form body field:", form.body.data)
    # print("Method:", request.method)
    # print("Form data:", form.data)
    # print("Form errors:", form.errors)
    # print("Validate:", form.validate())
    # print("Validate on submit:", form.validate_on_submit())
    if form.validate_on_submit():
        new_blogpost = Post()
        new_blogpost.title = form.data.get("title")
        new_blogpost.subtitle = form.data.get("subtitle")
        new_blogpost.date = today
        new_blogpost.author = form.data.get("author")
        new_blogpost.img_url = form.data.get("img_url")
        new_blogpost.body = cleanify(form.body.data)

        db.session.add(new_blogpost)
        db.session.commit()

        return redirect(
            "/",
        )

    return render_template("make-post.html", current_year=current_year, form=form)


@app.route("/post/<int:id>")
def get_post(id):
    post = db.session.execute(db.select(Post).where(Post.id == id)).scalar()
    return render_template("post.html", current_year=current_year, post=post)


if __name__ == "__main__":
    app.run(debug=True)
