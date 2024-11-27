from datetime import date

from flask import Flask, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor, CKEditorField
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from wtforms import StringField, SubmitField
from wtforms.validators import URL, DataRequired

app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
Bootstrap5(app)


ckeditor = CKEditor(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


class NewBlogForm(FlaskForm):
    title = StringField("name", validators=[DataRequired()])
    subtitle = StringField("subtitle", validators=[DataRequired()])
    body = CKEditorField("body", validators=[DataRequired()])
    author = StringField("author", validators=[DataRequired()])
    img_url = StringField("img_url", validators=[DataRequired()])
    submit = SubmitField("Add")


@app.route("/")
def get_all_posts():
    # Queries the database for all the posts. Converts the data to a python list.
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts)


# a route to click on individual posts.
@app.route("/show-post")
def show_post():
    post_id = request.args.get("post_id")

    # Retrieves a BlogPost from the database based on the post_id
    requested_post = db.session.execute(
        db.select(BlogPost).where(BlogPost.id == post_id)
    ).scalar()
    return render_template("post.html", post=requested_post)


# create a new blog post
@app.route("/add-new-post", methods=["GET", "POST"])
def add_new_post():
    form = NewBlogForm()
    if request.method == "POST":
        new_post = BlogPost(
            title=request.form.get("title"),
            subtitle=request.form.get("subtitle"),
            date=date.today().strftime("%B %d, %Y"),
            body=request.form.get("body"),
            author=request.form.get("author"),
            img_url=request.form.get("img_url"),
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, h1="Add New Post")


# TODO: edit_post() to change an existing blog post
@app.route("/edit-post", methods=["GET", "POST"])
def edit_post():
    post_id = request.args.get("post_id")
    post_date = (
        db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id))
        .scalar()
        .date
    )

    selected_post = db.get_or_404(BlogPost, post_id)

    form = NewBlogForm(
        title=selected_post.title,
        subtitle=selected_post.subtitle,
        body=selected_post.body,
        author=selected_post.author,
        img_url=selected_post.img_url,
    )
    form.submit.label.text = "Update"

    if request.method == "POST":
        db.session.delete(selected_post)
        db.session.commit()

        new_post = BlogPost(
            id=post_id,
            title=request.form.get("title"),
            subtitle=request.form.get("subtitle"),
            date=post_date,
            body=request.form.get("body"),
            author=request.form.get("author"),
            img_url=request.form.get("img_url"),
        )

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id))
    return render_template("make-post.html", form=form, h1="Edit Post")


# TODO: delete_post() to remove a blog post from the database
@app.route("/delete", methods=["Get", "POST"])
def delete_post():
    post_id = request.args.get("post_id")
    selected_post = db.get_or_404(BlogPost, post_id)

    db.session.delete(selected_post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
