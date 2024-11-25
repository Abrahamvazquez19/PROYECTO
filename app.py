from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
db = SQLAlchemy(app)

# Modelo para productos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

# Crear la base de datos
with app.app_context():
    db.create_all()

# Ruta para agregar productos
@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    data = request.json
    nuevo_producto = Producto(
        nombre=data['nombre'],
        cantidad=data['cantidad'],
        precio=data['precio']
    )
    db.session.add(nuevo_producto)
    db.session.commit()
    return jsonify({"message": "Producto agregado"}), 201

# Ruta para obtener todos los productos
@app.route('/productos', methods=['GET'])
def obtener_productos():
    productos = Producto.query.all()
    return jsonify([{
        "id": p.id,
        "nombre": p.nombre,
        "cantidad": p.cantidad,
        "precio": p.precio
    } for p in productos])

if __name__ == '__main__':
    app.run(debug=True)
