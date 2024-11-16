import requests
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    response = requests.get("https://api.npoint.io/c790b4d5cab58020d391")
    all_posts = response.json()
    return render_template("index.html", posts=all_posts)


@app.route("/blog/<int:num>")
def get_post(num):
    response = requests.get("https://api.npoint.io/c790b4d5cab58020d391")
    all_posts = response.json()
    the_post = None
    for post in all_posts:
        if post["id"] == num:
            the_post = post
            break
    if the_post is None:
        the_post = {"id": 0, "body": "None", "title": "None", "subtitle": "None"}
    return render_template("post.html", post=the_post)


if __name__ == "__main__":
    app.run(debug=True)
