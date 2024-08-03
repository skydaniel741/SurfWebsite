from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secretkey'

def get_db_connection():
    conn = sqlite3.connect('SurfBoards.db')
    conn.row_factory = sqlite3.Row
    return conn




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
            session['cart'] = []  # Initialize cart in session
            return redirect(url_for('surfboards'))
        else:
            msg = 'Invalid username or password'
    return render_template("login.html", message=msg)


@app.route('/surfboards_data')
def surfboards_data():
    conn = sqlite3.connect("SurfBoards.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM SurfBoards")
    surfboards = cur.fetchall()
    conn.close()
    surfboard_list = []
    for row in surfboards:
        surfboard = {
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "condition": row[3],
            "price": row[4],
            "image": row[5],
        }
        surfboard_list.append(surfboard)

    return jsonify(surfboard_list)



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("lobby"))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not re.match(r'^[A-Za-z]+$', username):
            msg = 'Invalid Username Try Again'
        elif not re.match(r'^[A-Za-z0-9]+$', password):
            msg = 'Invalid Password Try Again'
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


@app.route('/surfboard')
def surfboards():
    conn = sqlite3.connect("SurfBoards.db")
    cur = conn.cursor()
    cur.execute("SELECT *  FROM SurfBoards")
    surfboards = cur.fetchall()
    conn.close()
    return render_template("surfboards.html", surfboards=surfboards)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor() 
    
    cart_items = session.get('cart', [])
    surfboards = []
    final_total = 0

    for item in cart_items:
        cur.execute("SELECT * FROM SurfBoards WHERE surfboard_id = ?", (item['surfboard_id'],))
        surfboard = cur.fetchone()
        if surfboard:
            surfboard_dict = {
                'surfboard_id': surfboard['surfboard_id'],
                'name': surfboard['surfboard_name'],
                'type': surfboard['surfboard_type'],
                'condition': surfboard['surfboard_condition'],
                'price': surfboard['purchase_price'],
                'image': surfboard['surfboard_photo'],
                'quantity': item['quantity']
            }
            final_total += surfboard['purchase_price'] * item['quantity']
            surfboards.append(surfboard_dict) 

    conn.close()

    return render_template('checkout.html', cart=surfboards, final_total=final_total)


@app.route('/lobby')
def lobby():
    return render_template("lobby.html")


if __name__ == "__main__":
    app.run(debug=True)