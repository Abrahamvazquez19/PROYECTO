
import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QMessageBox

class InventarioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Inventario")
        self.setGeometry(200, 200, 300, 200)

        # Configuración de Layout
        layout = QVBoxLayout()
        
        # Widgets de Entrada
        self.nombre_input = QLineEdit(self)
        self.nombre_input.setPlaceholderText("Nombre del Producto")
        layout.addWidget(self.nombre_input)

        self.cantidad_input = QLineEdit(self)
        self.cantidad_input.setPlaceholderText("Cantidad")
        layout.addWidget(self.cantidad_input)

        self.precio_input = QLineEdit(self)
        self.precio_input.setPlaceholderText("Precio")
        layout.addWidget(self.precio_input)

        # Botón para Agregar Producto
        agregar_btn = QPushButton("Agregar Producto", self)
        agregar_btn.clicked.connect(self.agregar_producto)
        layout.addWidget(agregar_btn)

        # Configuración del contenedor principal
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def agregar_producto(self):
        nombre = self.nombre_input.text()
        cantidad = self.cantidad_input.text()
        precio = self.precio_input.text()

        if not (nombre and cantidad and precio):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return
        
        # Enviar datos al backend
        url = "http://127.0.0.1:5000/agregar_producto"
        response = requests.post(url, json={
            "nombre": nombre,
            "cantidad": int(cantidad),
            "precio": float(precio)
        })

        if response.status_code == 201:
            QMessageBox.information(self, "Éxito", "Producto agregado correctamente.")
            self.nombre_input.clear()
            self.cantidad_input.clear()
            self.precio_input.clear()
        else:
            QMessageBox.warning(self, "Error", "No se pudo agregar el producto.")

# Ejecutar la aplicación de PyQt
app = QApplication(sys.argv)
window = InventarioApp()
window.show()
sys.exit(app.exec_())

