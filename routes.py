from flask import Flask, render_template, redirect, url_for, request 
import sqlite3

app = Flask(__name__)


@app.route('/')
def layout():
  return render_template("layout.html")

@app.route('/signup')
def signup():
  return render_template("signup.html")

@app.route('/login' ,methods=['GET', 'POST'])
def login():
  return render_template("login.html")


@app.route('/surfboard/<int:id>')
def surfboard(id):
  conn = sqlite3.connect("SurfBoards.db")
  cur = conn.cursor()
  cur.execute("SELECT * FROM SurfBoards WHERE surfboard_id =?",(id,))
  surfboard = cur.fetchone()
  return render_template("surfboards.html",surfboard=surfboard)

@app.route('/brands')
def brands():
  return render_template("brands.html")


@app.route('/checkout')
def checkout():
  return render_template("checkout.html")

@app.route('/home')
def home():
  return render_template("home.html")


if __name__ == "__main__":
  app.run(debug=True)