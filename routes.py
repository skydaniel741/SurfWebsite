from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'secretkey'

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect("SurfBoards.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username = ? and password = ?", (username, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session['loggedin'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('home'))
        else:
            msg = 'Invalid username or password'
    return render_template("login.html", message=msg)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not re.match(r'^[A-Za-z]+$', username):
            msg = 'Invalid Signup Try Again'
        elif not re.match(r'^[A-Za-z0-9]+$', password):
            msg = 'Invalid Signup Try Again'
        else:
            conn = sqlite3.connect("SurfBoards.db")
            cur = conn.cursor()
            cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
            user = cur.fetchone()
            if user:
                msg = 'Username already exists'
            else:
                cur.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                msg = 'Account Created'
            conn.close()
    return render_template("signup.html", message=msg)


@app.route('/')
def layout():
    return render_template("lobby.html")


@app.route('/surfboard/<int:id>')
def surfboard(id):
    conn = sqlite3.connect("SurfBoards.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM SurfBoards WHERE surfboard_id = ?", (id,))
    surfboard = cur.fetchone()
    conn.close()
    return render_template("surfboards.html", surfboard=surfboard)


@app.route('/brands')
def brands():
    return render_template("brands.html")


@app.route('/checkout')
def checkout():
    return render_template("checkout.html")


@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/lobby')
def lobby():
    return render_template("lobby.html")


@app.route(404)
def error():
    return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=True)