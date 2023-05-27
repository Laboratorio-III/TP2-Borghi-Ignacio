from typing import List
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3
from PyQt6.QtWidgets import QApplication, QTableView, QVBoxLayout, QWidget, QPushButton, QLineEdit
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
import sys

class TareaEliminada:
    def __init__(self, id_tarea, titulo, estado, creada, actualizada):
        self.id_tarea = id_tarea
        self.titulo = titulo
        self.estado = estado
        self.creada = creada
        self.actualizada = actualizada
        self.fechaEliminacion =datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      
class Tarea:
    def __init__(self, id, titulo, descripcion):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.estado = "pendiente"
        self.creada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.actualizada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class AdminTarea:

    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT,
                descripcion TEXT,
                creada DATE,
                actualizada DATE,
                estado TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas_eliminadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_tarea INTEGER,
                titulo TEXT,
                creada DATE,
                actualizada DATE,
                estado TEXT,
                fechaEliminacion DATE,
                FOREIGN KEY (id_tarea) REFERENCES tareas (id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS estados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estado TEXT
            )
        ''')

        self.cursor.execute("INSERT INTO estados (estado) VALUES ('pendiente')")
        self.cursor.execute("INSERT INTO estados (estado) VALUES ('comenzado')")
        self.cursor.execute("INSERT INTO estados (estado) VALUES ('50[%] completado')")
        self.cursor.execute("INSERT INTO estados (estado) VALUES ('finalizado')")

        self.connection.commit()

    def agregar_tarea(self, tarea):
        tarea_query = '''
            INSERT INTO tareas (titulo, descripcion, creada, actualizada, estado)
            VALUES (?, ?, ?, ?, ?)
        '''
        tarea_data = (tarea.titulo, tarea.descripcion, tarea.creada, tarea.actualizada, tarea.estado)
        self.cursor.execute(tarea_query, tarea_data)
        self.connection.commit()
        tarea_id = self.cursor.lastrowid
        return tarea_id

    def traer_tarea(self, tarea_id: int) -> Tarea:
        tarea_query = '''
            SELECT id, titulo, descripcion, estado, creada, actualizada
            FROM tareas
            WHERE id = ?
        '''
        self.cursor.execute(tarea_query, (tarea_id,))
        tarea_row = self.cursor.fetchone()

        if tarea_row is not None:
            tarea_id, titulo, descripcion, estado, creada, actualizada = tarea_row
            tarea = Tarea(tarea_id, titulo, descripcion)
            tarea.estado = estado
            tarea.creada = creada
            tarea.actualizada = actualizada
            return tarea
        else:
            return None
    def actualizar_estado_tarea(self, tarea_id: int, estado: str):
        self.cursor.execute('''
            UPDATE tareas SET estado=?, actualizada=? WHERE id=?
            ''', (estado, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tarea_id))
        self.connection.commit()

    
    
    def eliminar_tarea(self, tarea_id: int):
        tarea = self.traer_tarea(tarea_id)
        self.cursor.execute('''
            INSERT INTO tareas_eliminadas (
                id_tarea,
                titulo,
                creada,
                actualizada,
                estado,
                fechaEliminacion) VALUES (?, ?, ?, ?, ?, ?)
        ''', (tarea_id, tarea.titulo, tarea.creada, tarea.actualizada, tarea.estado, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.connection.commit()
        self.cursor.execute('''
            DELETE FROM tareas WHERE id=?
            ''', (tarea_id,))
        self.connection.commit()
        
        
    def tareaXactualizacion(self):
    
        self.cursor.execute('''SELECT Titulo, SUM(actualizada)
                            FROM tareas
                            GROUP BY Titulo''')
        data = self.cursor.fetchall()
        return data

    def traer_todas_tareas(self) -> List[Tarea]:
        tareas = []
        self.cursor.execute('SELECT id, titulo, descripcion, estado, creada, actualizada FROM tareas')
        rows = self.cursor.fetchall()
        for row in rows:
            tarea = Tarea(row[0], row[1], row[2])  
            tarea.estado = row[3]
            tarea.creada = row[4]
            tarea.actualizada = row[5]
            tareas.append(tarea)
        return tareas
    def traer_tareas_eliminadas(self) -> List[TareaEliminada]:
        tareas = []
        for tarea_dict in self.tareas.all():
            tarea = TareaEliminada(tarea_dict["id_tarea"], tarea_dict["titulo"], tarea_dict["estado"], tarea_dict["creada"],tarea_dict["actualizada"])
            tarea.id_tarea = tarea_dict["id_tarea"]
            tarea.titulo = tarea_dict["titulo"]
            tarea.estado = tarea_dict["estado"]
            tarea.creada = tarea_dict["creada"]
            tarea.actualizada = tarea_dict["actualizada"]
            tareas.append(tarea)
        return tareas
class MiTabla(QAbstractTableModel):
    def __init__(self, datos=None):
        QAbstractTableModel.__init__(self)
        self._datos = datos

    def rowCount(self, parent=None):
        return len(self._datos)

    def columnCount(self, parent=None):
        return len(self._datos[0])

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._datos[index.row()][index.column()])
        return None
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ("Titulo", "Descripción", "Estado", "Creada", "Actualizada", "Accion")[col]
        return QAbstractTableModel.headerData(self, col, orientation, role)
class TareaTableModel(QAbstractTableModel):
        def __init__(self, data = None):
            QAbstractTableModel.__init__(self)
            self.data = data
            self.columns = ["Titulo", "Descripcion", "Estado", "Creada", "Actualizada", "Accion"]
    
        def rowCount(self, parent=None):
            return len(self.data)
    
        def columnCount(self, parent=None):
            return len(self.columns)
    
        def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
            if index.isValid():
                if role == QtCore.Qt.DisplayRole:
                    return str(self.data[index.row()][index.column()])
            return None
    
        def headerData(self, col, orientation, role):
            if orientation == Qt.Horizontal and role == Qt.DisplayRole:
                return self.columns[col]
            return QAbstractTableModel.headerData(self, col, orientation, role)
  

class VentanaPrincipal(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.admin_tareas = AdminTarea("DBAdminTareas.db")
        self.setupUi()
        self.llenarTabla()
        

    def setupUi(self):
        self.resize(850, 600)
        self.move(300, 300)
        self.setWindowTitle("Tareas")

        # Textbox
        self.titulo_textbox = QLineEdit(self)
        self.titulo_textbox.resize(180, 21)
        self.titulo_textbox.move(20, 20)
        self.titulo_textbox.setPlaceholderText("Titulo")

        self.descripcion_textbox = QLineEdit(self)
        self.descripcion_textbox.resize(540, 21)
        self.descripcion_textbox.move(20, 60)
        self.descripcion_textbox.setPlaceholderText("Descripción")

        # Boton
        self.boton_aceptar = QPushButton("Aceptar", self)
        self.boton_aceptar.move(740, 100)
        self.boton_aceptar.clicked.connect(self.click_boton_aceptar)

        self.boton_eliminadas = QPushButton("Ver tareas eliminadas", self)
        self.boton_eliminadas.move(20, 580)
        self.boton_eliminadas.setToolTip("Ver solo las eliminadas")

        self.boton_todas = QPushButton("Ver todas las tareas", self)
        self.boton_todas.setToolTip("Ver todas las tareas incluidas las eliminadas")
        # TableView
        self.model = QStandardItemModel(self)
        self.tableView = QTableView(self)
        self.tableView.move(20, 140)
        self.tableView.resize(760, 440)
        self.tableView.setModel(self.model)

    def llenarTabla(self):
        self.model.clear()  # Limpiar la tabla antes de llenarla nuevamente
        self.model.setHorizontalHeaderLabels(("ID", "Titulo", "Descripción", "Estado", "Creada", "Actualizada", "Acción"))

        lista_tareas = self.admin_tareas.traer_todas_tareas()
        for i, tarea in enumerate(lista_tareas):
            self.model.setItem(i, 0, QStandardItem(str(tarea.id)))
            self.model.setItem(i, 1, QStandardItem(tarea.titulo))
            self.model.setItem(i, 2, QStandardItem(tarea.descripcion))
            self.model.setItem(i, 3, QStandardItem(tarea.estado))
            self.model.setItem(i, 4, QStandardItem(tarea.creada))
            self.model.setItem(i, 5, QStandardItem(tarea.actualizada))
            self.tableView.setColumnWidth(0, 40)
            self.tableView.setColumnWidth(1, 100)
            self.tableView.setColumnWidth(2, 200)
            self.tableView.setColumnWidth(3, 100)
            self.tableView.setColumnWidth(4, 130)
            self.tableView.setColumnWidth(5, 130)
            index = self.model.index(i, 6)
            botonEliminar = QPushButton("Eliminar")
            botonEliminar.clicked.connect(lambda checked, tarea_id=tarea.id: self.eliminarTarea(tarea_id))
            self.tableView.setIndexWidget(index, botonEliminar)
    
    def eliminarTarea(self, tarea_id):
        self.admin_tareas.eliminar_tarea(tarea_id)
        self.llenarTabla()
    def click_boton_aceptar(self):
        titulo = self.titulo_textbox.text()
        descripcion = self.descripcion_textbox.text()
        tarea = Tarea(None, titulo, descripcion)  # None para el ID, se generará automáticamente en la base de datos
        tarea_id = self.admin_tareas.agregar_tarea(tarea)
        self.llenarTabla()


if __name__ == '__main__':
    app = QApplication([])
    form = VentanaPrincipal()
    form.show()
    sys.exit(app.exec())
    
    
    
    
    
    



