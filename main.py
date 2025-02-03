import hashlib
import os
import secrets
from datetime import date
from functools import wraps
from typing import List

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_ckeditor import CKEditor, CKEditorField
from flask_ckeditor.utils import cleanify
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import EmailField, PasswordField, StringField, SubmitField, URLField
from wtforms.validators import URL, DataRequired, Email

import email_sender

SECRET_KEY = secrets.token_hex()

load_dotenv()

my_email = os.getenv("MY_EMAIL")
my_password = os.getenv("MY_PASSWORD")

today = date.today().strftime("%d %B %Y")
current_year = date.today().year
data_url = "https://api.npoint.io/ee84059f6d2a9704021f"

# Create the app
app = Flask(__name__)
## Configure the app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
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
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(back_populates="post")


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    posts: Mapped[List["Post"]] = relationship(back_populates="user")
    comments: Mapped[List["Comment"]] = relationship(back_populates=("user"))


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="comments")
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    post: Mapped["Post"] = relationship(back_populates="comments")


### Create the Tables
with app.app_context():
    db.create_all()

# Initialize flask-ckeditor
ckeditor = CKEditor(app)

# Configure flask-login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Forms
class NewPostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    img_url = URLField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()])
    email = EmailField("Your Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_again = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class CommentForm(FlaskForm):
    comment_body = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


def admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.id == 1:
            return f(*args, **kwargs)
        else:
            return abort(403)

    return wrapper


def send_msg(name: str, email: str, phone: str, msg: str):
    sender = email_sender.EmailSender(
        smtp_host="smtp.gmail.com", sender_email=my_email, sender_password=my_password
    )
    sender.send_email(
        recipient_email=my_email,
        subject=f"Message from {name}!",
        email_body=f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {msg}",
    )


@app.template_global()
def gravatar_url(email, size=40, rating="g", default="retro", force_default=False):
    hash_value = hashlib.md5(email.lower().encode("utf-8")).hexdigest()
    gravatar_url = f"https://www.gravatar.com/avatar/{hash_value}?s={size}&d={default}&r={rating}&f={force_default}"
    return gravatar_url


@app.route("/")
def home():
    posts = db.session.execute(db.select(Post)).scalars()

    return render_template("index.html", current_year=current_year, posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    # print("Method:", request.method)
    # print("Form data:", form.data)
    # print("Form errors:", form.errors)
    # print("Validate:", form.validate())
    # print("Validate on submit:", form.validate_on_submit())
    if form.validate_on_submit():
        pass1 = form.data.get("password")
        pass2 = form.data.get("password_again")
        if pass1 != pass2:
            return redirect("/register")

        name = form.data.get("name")
        email = form.data.get("email")
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            flash("Account already exists! Try Logging in.")
            return redirect("login")
        password = generate_password_hash(
            password=pass1, method="pbkdf2:sha256:600000", salt_length=8
        )
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect("/")
    return render_template("register.html", current_year=current_year, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.data.get("email")
        print(email)
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        print(user)
        if not user:
            flash("No account on this email exists!")
            return render_template("login.html", current_year=current_year, form=form)

        password = form.data.get("password")
        if check_password_hash(pwhash=user.password, password=password):
            login_user(user)
            return redirect("/")
        else:
            flash("Incorrect Password!")
            return render_template("login.html", current_year=current_year, form=form)

    return render_template("login.html", current_year=current_year, form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


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
@login_required
@admin_only
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
        new_blogpost.user_id = current_user.id
        new_blogpost.img_url = form.data.get("img_url")
        new_blogpost.body = cleanify(form.body.data)

        db.session.add(new_blogpost)
        db.session.commit()

        return redirect("/")

    return render_template("make-post.html", current_year=current_year, form=form)


@app.route("/post/<int:id>", methods=["GET", "POST"])
def get_post(id):
    post = db.session.execute(db.select(Post).where(Post.id == id)).scalar()
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            text=cleanify(form.comment_body.data), user_id=current_user.id, post_id=id
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("get_post", id=id))
    return render_template("post.html", current_year=current_year, post=post, form=form)


@app.route("/edit-post/<int:id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_post(id):
    post = db.session.execute(db.select(Post).where(Post.id == id)).scalar()
    form = NewPostForm()
    if form.validate_on_submit():
        post.title = form.data.get("title")
        post.subtitle = form.data.get("subtitle")
        post.author = form.data.get("author")
        post.img_url = form.data.get("img_url")
        post.body = cleanify(form.body.data)
        db.session.commit()
        return redirect(f"/post/{id}")
    
    form.title.data = post.title
    form.subtitle.data = post.subtitle
    form.author.data = post.author
    form.img_url.data = post.img_url
    article_body = post.body
    
    return render_template(
        "make-post.html",
        current_year=current_year,
        post=post,
        form=form,
        is_edit=True,
        article_body=article_body,
    )


@app.route("/delete-post/<int:id>")
@login_required
@admin_only
def delete_post(id):
    post = db.session.execute(db.select(Post).where(Post.id == id)).scalar()
    db.session.delete(post)
    db.session.commit()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
