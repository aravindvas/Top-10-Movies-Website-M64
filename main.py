from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mynameisvas'
Bootstrap(app)

##CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)
db.create_all()


# # After adding the new_movie the code needs to be commented out/deleted.
# # So you are not trying to add the same movie twice.
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    all_mvs = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_mvs)):
        all_mvs[i].ranking = len(all_mvs) - i
    db.session.commit()
    return render_template("index.html", mvs=all_mvs)

class rate_mv(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")


@app.route("/editt", methods=["GET", "POST"])
def edit():
    frm = rate_mv()
    mv_id = request.args.get("id")
    mv = Movie.query.get(mv_id)
    if frm.validate_on_submit():
        mv.rating = float(frm.rating.data)
        mv.review = frm.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", mov=mv, form=frm)

@app.route("/delete")
def delt():
    mv_id2 = request.args.get("id2")
    mv2 = Movie.query.get(mv_id2)
    db.session.delete(mv2)
    db.session.commit()
    return redirect(url_for('home'))

class add_mv(FlaskForm):
    Title = StringField("Movie Title",validators=[DataRequired()])
    sbt = SubmitField("Add Movie")

mvdb_url = "https://api.themoviedb.org/3/search/movie"
API = "3b85a80fe26eebe258d320361ee067c4"
mvinfo_url = "https://api.themoviedb.org/3/movie"
mvimg_url = "https://image.tmdb.org/t/p/w500"

@app.route("/addd", methods=["GET", "POST"])
def add():
    frm2 = add_mv()
    if frm2.validate_on_submit():
        mv_tit = frm2.Title.data
        rsp = requests.get(url=mvdb_url, params={"api_key": API, "query": mv_tit})
        dat = rsp.json()["results"]
        # print(dat)
        return render_template('select.html', options=dat)

    return render_template("add.html",form2=frm2)

@app.route("/find")
def fnd_mv():
    mv_api_id = request.args.get("id4")
    if mv_api_id:
        mv_api_url = f"{mvinfo_url}/{mv_api_id}"
        rsp2 = requests.get(url=mv_api_url, params={"api_key": API, "language": "en-US"})
        dat2 = rsp2.json()
        new_movie = Movie(
            title=dat2['title'],
            year=dat2['release_date'].split('-')[0],
            description=dat2["overview"],
            img_url= f"{mvimg_url}/{dat2['poster_path']}",
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("home"))



if __name__ == '__main__':
    app.run(debug=True)
