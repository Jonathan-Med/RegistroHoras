# This Python file uses the following encoding: utf-8
from PySide6.QtWidgets import QLabel, QDoubleSpinBox, QTableWidgetItem, QTableWidget


def actualizar_total(tabla_horas, row):
    total = 0.0
    for col in range(1, 8):  # Columnas de los días de la semana
        spin_box = tabla_horas.cellWidget(row, col)
        if isinstance(spin_box, QDoubleSpinBox):
            total += spin_box.value()

    # Actualizar la columna de total (columna 8)
    total_item = tabla_horas.item(row, 8)
    if not total_item:
        total_item = QTableWidgetItem()
        tabla_horas.setItem(row, 8, total_item)
    total_item.setText(f"{total:.2f}")
