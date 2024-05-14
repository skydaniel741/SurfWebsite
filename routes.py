from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey'

@app.route('/login',methods=['GET', 'POST'])
def login():
  # finds the user in the database
  if request.method == 'POST':
    username = request.form ['username']
    password = request.form['password']
    conn = sqlite3.connect("SurfBoards.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE username = ? and password = ?", (username, password))
    user = cur.fetchone()
    #if user is in session
    if user:
        session['loggedin'] = True
        session['user_id'] = user[0]
        session['username'] = user[1]
        return redirect(url_for('home'))
    else:
        message = print("Invalid username or password")
        return render_template("login.html", message = message)
  return render_template ("login.html")



@app.route('/')
def layout():
  return render_template("layout.html")

@app.route('/signup')
def signup():
  return render_template("signup.html")



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