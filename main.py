from flask import Flask, render_template
from datetime import date
import requests as req

current_year = date.today().year

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html", current_year=current_year)


@app.route("/blog")
def get_blog():
    data_url = "https://api.npoint.io/c790b4d5cab58020d391"

    res = req.get(data_url)

    data = res.json()

    return render_template("blog.html", posts=data)



if __name__ == "__main__":
    app.run(debug=True)
