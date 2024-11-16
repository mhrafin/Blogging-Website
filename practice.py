from datetime import datetime

import requests
from flask import Flask, render_template

YEAR = datetime.now().year
print(YEAR)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html", year=YEAR)


@app.route("/guess/<name>")
def guess(name):
    age_res = requests.get("https://api.agify.io", params={"name": name})
    guessed_age = age_res.json()["age"]

    gender_res = requests.get("https://api.genderize.io", params={"name": name})
    guessed_gender = gender_res.json()["gender"]

    return render_template(
        "guess.html", name_=name, age=guessed_age, gender=guessed_gender
    )


@app.route("/blog")
def blog():
    blog_url = "https://api.npoint.io/c790b4d5cab58020d391"
    response = requests.get(blog_url)
    all_posts = response.json()
    return render_template("blog.html", posts=all_posts)


if __name__ == "__main__":
    app.run(debug=True)
