# This Python file uses the following encoding: utf-8
import csv
import sys

from PySide6.QtWidgets import (
    QGridLayout, QPushButton, QTableWidgetItem, QLabel, QVBoxLayout, QDialog, QLineEdit,
    QDoubleSpinBox)
from Funcionalidades.calcular_horas import *
from PySide6.QtGui import QFont, Qt


def extraer_datos(self):
    empleados = []
    print("Extrayendo datos...")
    for row in range(0, self.tabla_horas.rowCount()):  # Saltamos la primera fila que tiene los títulos
        empleado = []

        # Obtener el nombre del empleado
        nombre_item = self.tabla_horas.item(row, 0)
        nombre = nombre_item.text()

        empleado.append(nombre)
        print(f"Nombre extraído: {nombre}")  # Verificar qué nombres se están extrayendo

        # Obtener las horas trabajadas (columnas 1 a 7)
        for col in range(1, 8):
            spin_box = self.tabla_horas.cellWidget(row, col)
            if spin_box:
                empleado.append(spin_box.value())
            else:
                empleado.append(0.0)  # Valor predeterminado si no hay SpinBox

        # Obtener el total de horas
        total_item = self.tabla_horas.item(row, 8)
        total = total_item.text() if total_item else "0"
        empleado.append(float(total))

        print(f"Empleado completo extraído: {empleado}")  # Verificar la extracción completa

        empleados.append(empleado)

    return empleados


def guardar_horas_csv(empleados):
    with open("horas_trabajadas.csv", mode="w", newline="") as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        # Escribir la cabecera
        escritor_csv.writerow(["Nombre", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo", "Total"])
        # Escribir los datos de cada empleado
        for empleado in empleados:
            escritor_csv.writerow(empleado)


def cargar_datos_csv(self):
    try:
        with open("horas_trabajadas.csv", newline="") as archivo_csv:
            lector_csv = csv.reader(archivo_csv)
            next(lector_csv)  # Saltar los encabezados
            print("Cargando datos desde CSV...")  # Log de carga

            for i, fila in enumerate(lector_csv):
                # Asegúrate de que la fila tenga el número esperado de columnas
                if len(fila) < 9:
                    print(f"Fila {i + 1} tiene un número inesperado de columnas: {fila}")
                    continue  # Salta esta fila y pasa a la siguiente

                nombre = fila[0]
                horas = [float(h) if h else 0.0 for h in fila[1:8]]
                total = float(fila[8]) if fila[8] else 0.0

                # Agregar una fila a la tabla
                row_position = self.tabla_horas.rowCount()
                self.tabla_horas.insertRow(row_position)

                # Agregar el nombre
                nombre_item = QTableWidgetItem(nombre)
                nombre_item.setTextAlignment(Qt.AlignCenter)
                nombre_item.setFlags(nombre_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabla_horas.setItem(row_position, 0, nombre_item)

                # Agregar las horas con QDoubleSpinBox
                for col, hora in enumerate(horas, start=1):
                    spin_box = QDoubleSpinBox()
                    spin_box.setDecimals(2)
                    spin_box.setRange(0, 24)
                    spin_box.setSingleStep(0.50)
                    spin_box.setValue(hora)
                    self.tabla_horas.setCellWidget(row_position, col, spin_box)

                    # Conectar el cambio de valor para actualizar el total
                    spin_box.valueChanged.connect(lambda _, row=row_position: actualizar_total(self.tabla_horas, row))

                # Agregar el total
                total_item = QTableWidgetItem(f"{total:.2f}")
                total_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_horas.setItem(row_position, 8, total_item)

    except FileNotFoundError:
        print("El archivo horas_trabajadas.csv no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error al cargar los datos: {e}")


def reiniciar_horas(self):
    print("Funcion llamada")
    for row in range(0, self.tabla_horas.rowCount()):
        for col in range(1, 8):
            celda = self.tabla_horas.cellWidget(row, col)
            if isinstance(celda, QDoubleSpinBox):
                print(f"Valor antes: {celda.value()}")
                celda.setValue(0.0)
