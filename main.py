from datetime import datetime

import requests
from flask import Flask, render_template

RES = requests.get("https://api.npoint.io/bd19e496786f829612b2")
ALL_POSTS = RES.json()

TODAY = str(datetime.now().date())
YEAR = str(datetime.now().year)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html", posts=ALL_POSTS, today=TODAY)


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/contact")
def contact_page():
    return render_template("contact.html")


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
