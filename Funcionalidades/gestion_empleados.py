from PySide6.QtWidgets import (
    QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QDialog,
    QGridLayout, QLineEdit, QDoubleSpinBox, QCheckBox, QDialogButtonBox)
from PySide6.QtGui import QFont, Qt
from Funcionalidades.calcular_horas import actualizar_total
from functools import partial


def pedir_nombre(self):
    agregar_empleado = QDialog(self)
    agregar_empleado.setWindowTitle("Ingrese el nombre del empleado:")

    ventana = QVBoxLayout()
    etiqueta = QLabel("Nombre:")
    entrada_nombre = QLineEdit()
    ventana.addWidget(etiqueta)
    ventana.addWidget(entrada_nombre)

    boton_aceptar = QPushButton("Aceptar", agregar_empleado)
    ventana.addWidget(boton_aceptar)

    agregar_empleado.setLayout(ventana)

    boton_aceptar.clicked.connect(lambda: agregar_empleado.accept())

    if agregar_empleado.exec_() == QDialog.Accepted:
        return entrada_nombre.text()

    return None


def agregar_empleados(tabla_horas, nombre):
    row_position = tabla_horas.rowCount()
    tabla_horas.insertRow(row_position)

    nombre_item = QTableWidgetItem(nombre)
    nombre_item.setTextAlignment(Qt.AlignCenter)
    nombre_item.setFlags(nombre_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    tabla_horas.setItem(row_position, 0, nombre_item)

    total_horas_label = QTableWidgetItem("0.0")
    # total_horas_label.setFont(QFont("Time New Roman", 11))

    # Añadir los QDoubleSpinBox para los días
    for columna in range(1, 8):
        spin_box = QDoubleSpinBox()
        spin_box.setDecimals(2)
        spin_box.setRange(0, 24)
        spin_box.setSingleStep(0.50)
        tabla_horas.setCellWidget(row_position, columna, spin_box)

        # Conectar el valor cambiado a la función para actualizar el total
        spin_box.valueChanged.connect(lambda _, row=row_position: actualizar_total(tabla_horas, row))

    total_horas_label.setTextAlignment(Qt.AlignTop | Qt.AlignCenter)
    tabla_horas.setItem(row_position, 8, total_horas_label)


def mostrar_empleados(self, tabla_horas):
    nombres = []
    total_rows = tabla_horas.rowCount()
    for row in range(total_rows):
        nombre_item = tabla_horas.item(row, 0)
        if nombre_item:
            nombres.append(nombre_item.text())

    # Crear un diálogo para mostrar los checkboxes
    dialogo = QDialog(self)
    dialogo.setWindowTitle("Selecciona empleados a eliminar")

    # Layout vertical para los checkboxes
    layout_vertical = QVBoxLayout()

    # Lista para almacenar los checkboxes
    checkboxes = []

    for nombre in nombres:
        checkbox = QCheckBox(nombre)
        layout_vertical.addWidget(checkbox)
        checkboxes.append(checkbox)

    # Botones para aceptar o cancelar la acción
    botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    botones.accepted.connect(dialogo.accept)
    botones.rejected.connect(dialogo.reject)
    layout_vertical.addWidget(botones)

    dialogo.setLayout(layout_vertical)

    # Mostrar el diálogo
    if dialogo.exec():
        # Devolver los nombres seleccionados si el usuario acepta
        seleccionados = [checkbox.text() for checkbox in checkboxes if checkbox.isChecked()]
        print(seleccionados)
        return seleccionados
    else:
        return []


def eliminar_empleados(tabla_horas, empleados_a_eliminar):
    total_rows = tabla_horas.rowCount()
    for row in range(total_rows - 1, -1, -1):  # Recorremos en orden inverso
        nombre_item = tabla_horas.item(row, 0)
        if nombre_item and nombre_item.text() in empleados_a_eliminar:
            tabla_horas.removeRow(row)  # Eliminamos la fila correspondiente

    # Reasignamos las conexiones de los spinboxes restantes
    for row in range(tabla_horas.rowCount()):
        for columna in range(1, 8):  # Columnas de los spinboxes
            spin_box = tabla_horas.cellWidget(row, columna)
            if spin_box:
                spin_box.valueChanged.disconnect()  # Desconectamos cualquier conexión previa
                spin_box.valueChanged.connect(
                    lambda _, row=row: actualizar_total(tabla_horas, row)
                )


def calcular_pago(self, tabla_horas):
    """Calcula el pago basado en las horas trabajadas."""
    nombres, horas_totales = _obtener_datos_empleados(tabla_horas)
    dialogo, layout_principal, checkbox_todos, spin_todos = _crear_dialogo_principal(self)
    checkboxes, sueldo_spinboxes, total_labels = _crear_layout_empleados(
        layout_principal, nombres, horas_totales
    )
    resultados_label = QLabel()
    layout_principal.addWidget(resultados_label)

    _conectar_eventos(
        checkbox_todos, spin_todos, checkboxes, sueldo_spinboxes,
        total_labels, horas_totales, resultados_label, dialogo
    )
    dialogo.exec()


def _obtener_datos_empleados(tabla_horas):
    """Obtiene los nombres y horas totales de la tabla de horas."""
    nombres = []
    horas_totales = []
    total_rows = tabla_horas.rowCount()

    for row in range(total_rows):
        nombre_item = tabla_horas.item(row, 0)
        total_item = tabla_horas.item(row, 8)
        if nombre_item and total_item:
            nombres.append(nombre_item.text())
            try:
                horas_totales.append(float(total_item.text()))
            except (ValueError, AttributeError):
                horas_totales.append(0.0)
    return nombres, horas_totales


def _crear_dialogo_principal(parent):
    """Crea y configura el diálogo principal."""
    dialogo = QDialog(parent)
    dialogo.setWindowTitle("Calcular pagos a empleados")
    dialogo.setMinimumWidth(800)

    layout_principal = QVBoxLayout(dialogo)
    layout_principal.setContentsMargins(10, 10, 10, 10)
    layout_principal.setSpacing(15)

    layout_select_all = QHBoxLayout()
    checkbox_todos = QCheckBox("Seleccionar todos")
    spin_todos = QDoubleSpinBox()
    spin_todos.setRange(0, 500)
    spin_todos.setSingleStep(5)
    spin_todos.setValue(60.0)
    layout_select_all.addWidget(checkbox_todos)
    layout_select_all.addWidget(spin_todos)
    layout_principal.addLayout(layout_select_all)

    return dialogo, layout_principal, checkbox_todos, spin_todos


def _crear_layout_empleados(layout_principal, nombres, horas_totales):
    """Crea el layout para los empleados."""
    layout_empleados = QGridLayout()
    checkboxes = []
    sueldo_spinboxes = []
    total_labels = []

    for i, nombre in enumerate(nombres):
        checkbox = QCheckBox(nombre)
        horas_label = QLabel(f"{horas_totales[i]} Horas")
        spin_sueldo = QDoubleSpinBox()
        spin_sueldo.setRange(0, 500)
        spin_sueldo.setSingleStep(5)
        spin_sueldo.setValue(60.0)
        total_label = QLabel("0.00")

        layout_empleados.addWidget(checkbox, i, 0)
        layout_empleados.addWidget(horas_label, i, 1)
        layout_empleados.addWidget(spin_sueldo, i, 2)
        layout_empleados.addWidget(total_label, i, 3)

        checkboxes.append(checkbox)
        sueldo_spinboxes.append(spin_sueldo)
        total_labels.append(total_label)

    layout_principal.addLayout(layout_empleados)
    return checkboxes, sueldo_spinboxes, total_labels


def _conectar_eventos(
    checkbox_todos, spin_todos, checkboxes, sueldo_spinboxes,
    total_labels, horas_totales, resultados_label, dialogo
):
    """Configura las conexiones de eventos."""
    def actualizar_estado_spinboxes():
        if checkbox_todos.isChecked():
            # Si la opción principal está seleccionada
            for checkbox in checkboxes:
                checkbox.blockSignals(True)  # Evita disparar señales innecesarias
                checkbox.setChecked(False)  # Desmarca los checkboxes individuales
                checkbox.blockSignals(False)
            spin_todos.setEnabled(True)
            for spinbox in sueldo_spinboxes:
                spinbox.setEnabled(False)
        else:
            # Si se selecciona cualquier otra opción, desmarcar la principal
            for checkbox, spinbox in zip(checkboxes, sueldo_spinboxes):
                if checkbox.isChecked():
                    checkbox_todos.blockSignals(True)  # Evita recursividad
                    checkbox_todos.setChecked(False)  # Desmarcar principal
                    checkbox_todos.blockSignals(False)
                    break  # Salir del bucle, ya no es necesario continuar

            # Habilitar los spinboxes de acuerdo a los checkboxes seleccionados
            spin_todos.setEnabled(False)
            for checkbox, spinbox in zip(checkboxes, sueldo_spinboxes):
                spinbox.setEnabled(checkbox.isChecked())

    def calcular_totales():
        if checkbox_todos.isChecked():
            for i, nombre in enumerate(checkboxes):
                total = horas_totales[i] * spin_todos.value()
                total_labels[i].setText(f"{total:.2f}")
        else:
            for i, checkbox in enumerate(checkboxes):
                if checkbox.isChecked():
                    sueldo_por_hora = sueldo_spinboxes[i].value()
                    total = horas_totales[i] * sueldo_por_hora
                    total_labels[i].setText(f"{total:.2f}")

    checkbox_todos.stateChanged.connect(actualizar_estado_spinboxes)
    for checkbox in checkboxes:
        checkbox.stateChanged.connect(actualizar_estado_spinboxes)

    botones = QDialogButtonBox()
    boton_calcular = QPushButton("Calcular")
    boton_cerrar = QPushButton("Cerrar")
    botones.addButton(boton_calcular, QDialogButtonBox.ActionRole)
    botones.addButton(boton_cerrar, QDialogButtonBox.RejectRole)
    boton_calcular.clicked.connect(calcular_totales)
    boton_cerrar.clicked.connect(dialogo.reject)
    layout_principal = resultados_label.parent().layout()
    layout_principal.addWidget(botones)

    actualizar_estado_spinboxes()
