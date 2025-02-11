from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'secretkey'  # Untuk flash messages

# Buat folder upload jika belum ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Inisialisasi database
def init_db():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS menu (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        price REAL NOT NULL,
                        image TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_name TEXT NOT NULL,
                        table_number INTEGER NOT NULL,
                        item_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        status TEXT DEFAULT 'Pending',
                        paid INTEGER DEFAULT 0,
                        FOREIGN KEY (item_id) REFERENCES menu(id))''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    menu_items = cursor.fetchall()
    conn.close()
    return render_template('index.html', menu=menu_items)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        file = request.files['image']

        if file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            cursor.execute("INSERT INTO menu (name, price, image) VALUES (?, ?, ?)", (name, price, filename))
            conn.commit()
            flash("Menu berhasil ditambahkan!", "success")
        else:
            flash("Gagal menambahkan menu, file gambar harus diunggah!", "danger")

    # Menangani pencarian menu
    search_query = request.args.get('search', '')
    if search_query:
        cursor.execute("SELECT * FROM menu WHERE name LIKE ?", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT * FROM menu")

    menu_items = cursor.fetchall()
    conn.close()
    return render_template('admin.html', menu=menu_items, search_query=search_query)


@app.route('/edit_menu/<int:menu_id>', methods=['POST'])
def edit_menu(menu_id):
    name = request.form['name']
    price = request.form['price']
    file = request.files['image']
    
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        cursor.execute("UPDATE menu SET name = ?, price = ?, image = ? WHERE id = ?", 
                       (name, price, filename, menu_id))
    else:
        cursor.execute("UPDATE menu SET name = ?, price = ? WHERE id = ?", 
                       (name, price, menu_id))

    conn.commit()
    conn.close()

    flash("Menu berhasil diperbarui!", "success")
    return redirect(url_for('admin'))

@app.route('/delete_menu/<int:menu_id>', methods=['POST'])
def delete_menu(menu_id):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM menu WHERE id = ?", (menu_id,))
    conn.commit()
    conn.close()

    flash("Menu berhasil dihapus!", "danger")
    return redirect(url_for('admin'))

@app.route('/order', methods=['POST'])
def order():
    customer_name = request.form.get('customer_name')
    table_number = request.form.get('table_number')
    item_ids = request.form.getlist('item_id[]')
    quantities = request.form.getlist('quantity[]')

    if not customer_name or not table_number:
        flash("Nama pelanggan dan nomor meja harus diisi!", "danger")
        return redirect(url_for('home'))

    if not item_ids or not quantities:
        flash("Tidak ada item yang dipesan!", "danger")
        return redirect(url_for('home'))

    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    items_added = False
    for item_id, quantity in zip(item_ids, quantities):
        if int(quantity) > 0:
            cursor.execute("INSERT INTO orders (customer_name, table_number, item_id, quantity) VALUES (?, ?, ?, ?)",
                           (customer_name, table_number, item_id, quantity))
            items_added = True

    conn.commit()
    conn.close()

    if not items_added:
        flash("Tidak ada item yang dipesan!", "danger")
        return redirect(url_for('home'))

    flash("Pesanan berhasil disimpan!", "success")
    return redirect(url_for('home'))

@app.route('/orders')
def view_orders():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT orders.id, orders.customer_name, orders.table_number, menu.name, orders.quantity, orders.status FROM orders JOIN menu ON orders.item_id = menu.id")
    orders = cursor.fetchall()
    conn.close()
    return render_template('orders.html', orders=orders)

@app.route('/update_order/<int:order_id>', methods=['POST'])
def update_order(order_id):
    status = request.form['status']
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()
    flash("Status order diperbarui!", "info")
    return redirect(url_for('view_orders'))
    
@app.route('/cashier', methods=['GET', 'POST'])
def cashier():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        table_number = request.form.get('table_number')
        total_price = float(request.form.get('total_price'))
        amount_paid = float(request.form.get('amount_paid'))

        if amount_paid < total_price:
            flash("Uang tidak cukup untuk membayar!", "danger")
            return redirect(url_for('cashier'))

        change = amount_paid - total_price  # Hitung kembalian

        # Update status pembayaran
        cursor.execute("UPDATE orders SET paid = 1 WHERE customer_name = ? AND table_number = ?", 
                       (customer_name, table_number))
        conn.commit()
        
        flash(f"Pembayaran berhasil! Kembalian: Rp {change}", "success")

        # Ambil order_id untuk struk
        cursor.execute("SELECT id FROM orders WHERE customer_name = ? AND table_number = ? LIMIT 1", 
                       (customer_name, table_number))
        order_id = cursor.fetchone()[0]

        return redirect(url_for('receipt', order_id=order_id, amount_paid=amount_paid, change=change))

    # Tampilkan daftar pesanan untuk kasir
    cursor.execute("""
        SELECT orders.customer_name, orders.table_number, 
               SUM(orders.quantity * menu.price) AS total_price, 
               MAX(orders.paid) AS paid, MIN(orders.id) AS order_id
        FROM orders 
        JOIN menu ON orders.item_id = menu.id 
        GROUP BY orders.customer_name, orders.table_number
    """)
    orders = cursor.fetchall()
    
    conn.close()
    return render_template('cashier.html', orders=orders)


@app.route('/receipt/<int:order_id>')
def receipt(order_id):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT customer_name, table_number 
        FROM orders 
        WHERE id = ?
    """, (order_id,))
    order_info = cursor.fetchone()

    if not order_info:
        flash("Struk tidak ditemukan!", "danger")
        return redirect(url_for('cashier'))

    customer_name, table_number = order_info

    cursor.execute("""
        SELECT menu.name, orders.quantity, menu.price, (orders.quantity * menu.price) as subtotal
        FROM orders
        JOIN menu ON orders.item_id = menu.id
        WHERE orders.customer_name = ? AND orders.table_number = ?
    """, (customer_name, table_number))
    
    order_items = cursor.fetchall()
    total_price = sum(item[3] for item in order_items)

    amount_paid = float(request.args.get('amount_paid', total_price))  # Default: total harga
    change = amount_paid - total_price  # Hitung kembalian

    conn.close()

    return render_template('receipt.html', 
                           customer_name=customer_name, 
                           table_number=table_number, 
                           order_items=order_items, 
                           total_price=total_price, 
                           amount_paid=amount_paid, 
                           change=change)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))
