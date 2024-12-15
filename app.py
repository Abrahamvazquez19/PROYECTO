from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import mysql.connector
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Configuración de la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="punto_de_ventas"
)

app.secret_key = 'tu_clave_secreta'  # Necesaria para las sesiones

# Página de inicio de sesión
@app.route('/usuario', methods=['GET', 'POST'])
def usuario():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):  # Verifica la contraseña
            # Si las credenciales son correctas, guardamos al usuario en la sesión
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            cursor.close()
            return redirect(url_for('almacen'))  # Redirige a la página del almacén
        else:
            flash('Credenciales incorrectas, intenta nuevamente.', 'error')
            cursor.close()
            return redirect(url_for('usuario'))  # Si la autenticación falla, vuelve a la página de login
    return render_template('usuario.html')


# Página del almacén
@app.route('/almacen')
def almacen():
    if 'user_id' not in session:
        return redirect(url_for('usuario'))  # Si no está logueado, redirige al login
    return render_template('almacen.html')  # Aquí renderizas almacen.html

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/venta')
def venta():
    return render_template('venta.html')

@app.route('/add_product', methods=['POST'])
def add_product():
    id_producto = request.form['id_producto']
    cantidad = request.form['cantidad']
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM productos WHERE id = %s", (id_producto,))
    producto = cursor.fetchone()
    
    if producto:
        nuevo_total = producto[3] + int(cantidad)
        cursor.execute("UPDATE productos SET cantidad = %s WHERE id = %s", (nuevo_total, id_producto))
    else:
        cursor.execute("INSERT INTO productos (id, cantidad) VALUES (%s, %s)", (id_producto, cantidad))
    
    db.commit()
    cursor.close()
    
    return redirect(url_for('home'))

@app.route('/complete_sale', methods=['POST'])
def complete_sale():
    try:
        # Asegúrate de recibir los datos como JSON
        data = request.get_json()
        ticket = data.get('ticket')
        total = data.get('total')
        
        if not ticket or not total:
            return jsonify({"error": "Datos incompletos"}), 400
        
        cursor = db.cursor()
        cursor.execute("INSERT INTO ventas (ticket, total) VALUES (%s, %s)", (str(ticket), total))
        db.commit()
        cursor.close()

        return jsonify({"message": "Venta completada con éxito", "ticket": ticket, "total": total}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/procesar-venta', methods=['POST'])
def procesar_venta():
    try:
        # Obtén los datos enviados desde el frontend
        data = request.get_json()

        # Valida que el ticket contenga información
        if not data or 'ticket' not in data or not data['ticket']:
            return jsonify({'error': 'Ticket vacío o datos inválidos'}), 400

        # Procesa los datos del ticket
        ticket = data['ticket']
        total = sum(item['price'] * item['quantity'] for item in ticket)

        cursor = db.cursor()

        # Verificar si hay suficiente stock para cada producto en el ticket
        for item in ticket:
            cursor.execute("SELECT cantidad FROM productos WHERE id = %s", (item['id'],))
            producto = cursor.fetchone()

            if producto:
                stock_actual = producto[0]
                if stock_actual < item['quantity']:
                    return jsonify({'error': f'No hay suficiente stock para {item["name"]}. Stock disponible: {stock_actual}'}), 400
            else:
                return jsonify({'error': f'Producto {item["name"]} no encontrado en la base de datos'}), 404

        # Si todo es correcto, actualizamos el inventario
        for item in ticket:
            cursor.execute("""
                UPDATE productos
                SET cantidad = cantidad - %s
                WHERE id = %s
            """, (item['quantity'], item['id']))

        # Guardamos la venta en la base de datos
        cursor.execute("INSERT INTO ventas (ticket, total) VALUES (%s, %s)", (str(ticket), total))
        db.commit()
        cursor.close()

        return jsonify({'message': 'Venta procesada correctamente', 'total': total}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
