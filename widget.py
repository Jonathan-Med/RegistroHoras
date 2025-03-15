# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
from PySide6.QtWidgets import QApplication, QWidget, QTableWidget, QPushButton
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from Funcionalidades.gestion_empleados import *
from Funcionalidades.guardar_restaurar_horas import *


class Widget(QWidget):
    def __init__(self):
        super(Widget, self).__init__()
        self.load_ui()

        # Encontrar los botones y la tabla
        self.agregar_empleado = self.findChild(QPushButton, 'agregar_empleado')
        self.eliminar_empleado = self.findChild(QPushButton, 'eliminar_empleado')
        self.tabla_horas = self.findChild(QTableWidget, 'Tabla_horas')
        self.reiniciar_horas = self.findChild(QPushButton, 'restablecer_horas')
        self.calcular_pago = self.findChild(QPushButton, 'calcular_pago')

        # Configurar la tabla
        if self.tabla_horas:
            self.tabla_horas.setColumnCount(9)
            self.tabla_horas.setRowCount(0)
            self.tabla_horas.setHorizontalHeaderLabels(
                ["Nombre", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo", "Total"]
            )

        # Cargar los datos iniciales
        self.cargar_los_datos()

        # Conectar las señales
        if self.agregar_empleado:
            self.agregar_empleado.clicked.connect(self.agregar_empleado_funcion_externa)
        if self.eliminar_empleado:
            self.eliminar_empleado.clicked.connect(self.eliminar_empleado_funcion_externa)
        if self.reiniciar_horas:
            self.reiniciar_horas.clicked.connect(self.reiniciar_horas_funcion_externa)
        if self.calcular_pago:
            self.calcular_pago.clicked.connect(self.calcular_pago_funcion_externa)

    def agregar_empleado_funcion_externa(self):
        nombre = pedir_nombre(self)
        if nombre:  # Solo agrega si se ingresó un nombre
            agregar_empleados(self.tabla_horas, nombre)

    def eliminar_empleado_funcion_externa(self):
        empleados_a_eliminar = mostrar_empleados(self, self.tabla_horas)
        eliminar_empleados(self.tabla_horas, empleados_a_eliminar)

    def reiniciar_horas_funcion_externa(self):
        reiniciar_horas(self)

    def calcular_pago_funcion_externa(self):
        calcular_pago(self, self.tabla_horas)

    def closeEvent(self, event):
        self.empleados = extraer_datos(self)
        guardar_horas_csv(self.empleados)  # Guardar los datos antes de cerrar
        event.accept()  # Aceptar el evento de cierre

    def cargar_los_datos(self):
        cargar_datos_csv(self)

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        if not ui_file.exists():
            print(f"No se encontró el archivo {path}")
            sys.exit(1)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()


if __name__ == "__main__":
    os.environ["QT_QUICK_BACKEND"] = "software"
    os.environ["QT_OPENGL"] = "desktop"
    app = QApplication([])
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
