from flask import Flask, render_template, redirect, url_for, request, session, flash
import sqlite3
import re
from functools import wraps
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
            session['cart'] = []  
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('surfboards'))
        else:
            msg = 'Invalid username or password'
    return render_template("login.html", message=msg)



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
        if not re.match(r'^[A-Za-z0-9]+$', username):
            msg = 'Invalid Username Try Again'
            msg = 'Only can Have letters and numbers'
        elif not re.match(r'^[A-Za-z0-9]+$', password):
            msg = 'Invalid Password Try Again'
            msg = 'Only can have letters and numbers'
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
    cur.execute("SELECT * FROM SurfBoards")
    surfboards = cur.fetchall()
    conn.close()
    return render_template("surfboards.html", surfboards=surfboards)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
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
                'condition': surfboard['surfboard_condtion'],
                'price': surfboard['purchase_price'],
                'image': surfboard['surfboard_photo'],
                'quantity': item['quantity']
            }
            final_total += surfboard['purchase_price'] * item['quantity']
            surfboards.append(surfboard_dict)

    conn.close()

    return render_template('checkout.html', cart=surfboards,  
                           final_total=final_total)


@app.route('/<int:surfboard_id>/remove_from_cart', methods=['POST'])
def remove_from_cart(surfboard_id):
    cart_items = session.get('cart', [])
    cart_items = [item for item in cart_items 
        if item['surfboard_id'] != surfboard_id]
    session['cart'] = cart_items
    return redirect(url_for('checkout'))


@app.route('/surfboards/brand/<brand_name>')
def surfboards_by_brand(brand_name):
    conn = sqlite3.connect("SurfBoards.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM SurfBoards WHERE surfboard_name LIKE ?",
        ('%' + brand_name + '%',)
    )
    surfboards = cur.fetchall()
    conn.close()
    return render_template(
        "surfboards.html",
        surfboards=surfboards,
        brand_name=brand_name
    )


@app.route('/brands')
def brands():
    conn = sqlite3.connect("SurfBoards.db")
    cur = conn.cursor()
    cur.execute("SELECT *  FROM Brands")
    brands = cur.fetchall()
    conn.close()
    return render_template("brands.html", brands=brands)


@app.route('/purchase_products', methods=['POST'])
def purchase_products():
    cart_items = session.get('cart', [])  
    conn = get_db_connection()
    cur = conn.cursor()
    user_id = session.get('user_id', None)
    for item in cart_items:
        cur.execute("SELECT surfboard_name, purchase_price FROM SurfBoards WHERE surfboard_id = ?",
                     (item['surfboard_id'],))
        surfboard = cur.fetchone()
        if surfboard:
            surfboard_name = surfboard['surfboard_name']
            purchase_price = surfboard['purchase_price']
            if user_id:
                cur.execute
    ("INSERT INTO Checkout (user_id, surfboard_id, surfboard_name, purchase_price) VALUES (?, ?, ?, ?)", 
     (user_id, item['surfboard_id'], surfboard_name, purchase_price))
    conn.commit()
    conn.close()
    session['cart'] = [] 
    flash('Thank you for your purchase!')
    flash('Please come to the nearest workshop for payment')
    return redirect(url_for('checkout'))
    
@app.route('/<int:surfboard_id>/add_to_cart', methods=["POST", "GET"])
def add_to_cart(surfboard_id):
    cart_items = session.get('cart', [])
    item_in_cart = next((item for item in cart_items if item['surfboard_id'] == surfboard_id), None)
    if item_in_cart:
        item_in_cart['quantity'] += 1
    else:
        cart_items.append({'surfboard_id': surfboard_id, 'quantity': 1})
    session['cart'] = cart_items  
    return redirect(url_for('checkout')) 

@app.route('/lobby')
def lobby():
    return render_template("lobby.html")


if __name__ == "__main__":
    app.run(debug=True)