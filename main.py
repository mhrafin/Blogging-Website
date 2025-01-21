from flask import Flask, render_template
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


@app.route("/contact")
def contact():
    return render_template("contact.html", current_year=current_year)


if __name__ == "__main__":
    app.run(debug=True)
