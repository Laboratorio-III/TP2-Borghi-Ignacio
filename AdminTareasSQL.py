from typing import List
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3
import json
from prettytable import PrettyTable

class TareaEliminada:
    def __init__(self, id_tarea, titulo, estado, creada, actualizada):
        self.id_tarea = id_tarea
        self.titulo = titulo
        self.estado = estado
        self.creada = creada
        self.actualizada = actualizada
        self.fechaEliminacion =datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      
class Tarea:
    def __init__(self, titulo, descripcion):
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
            SELECT titulo, descripcion, estado, creada, actualizada
            FROM tareas
            WHERE id = ?
        '''
        self.cursor.execute(tarea_query, (tarea_id,))
        tarea_row = self.cursor.fetchone()

        if tarea_row:
            tarea = Tarea(tarea_row[0], tarea_row[1])
            tarea.estado = tarea_row[2]
            tarea.creada = tarea_row[3]
            tarea.actualizada = tarea_row[4]
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
        
    def agruparActualizacionTareas(self):
    # Obtenga los datos de la consulta SQL
        self.cursor.execute('''SELECT Titulo, SUM(actualizada)
                            FROM tareas
                            GROUP BY Titulo''')
        data = self.cursor.fetchall()
        return data




    def traer_todas_tareas(self) -> List[Tarea]:
        tareas = []
        for tarea_dict in self.tareas.all():
            tarea = Tarea(tarea_dict["titulo"], tarea_dict["descripcion"])
            tarea.estado = tarea_dict["estado"]
            tarea.creada = tarea_dict["creada"]
            tarea.actualizada = tarea_dict["actualizada"]
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
def main():
    admin_tareas = AdminTarea("DBAdminTareas.db")
    while True:
        print('\n\nMenu Administrador de Tareas')
        print('1. Agregar tarea')
        print('2. Ver tarea')
        print('3. Actualizar estado de tarea')
        print('4. Eliminar tarea')
        print('5. Ver todas las tareas')
        print('6. Grafico')
        print('7. Ver tareas eliminadas')
        print('8. Salir')

        opcion = input('\nSeleccione una opción: ')
        if opcion.isdigit():
            option = int(opcion)
        else:
            print("Escriba un numero de entre las opciones")
            continue
        
        if option == 1:
            titulo = input("Escriba un título para la tarea, por favor: ")
            descripcion = input("podrias describirla brevemente?: ")
            tarea = Tarea(titulo, descripcion)
            admin_tareas.agregar_tarea(tarea)
            proximoId = admin_tareas.cursor.execute("SELECT MAX(id) FROM tareas").fetchone()[0] or 0
            traeTarea = admin_tareas.cursor.execute("SELECT * FROM tareas WHERE id = ?", (proximoId,))
            tarea_result = traeTarea.fetchone()
            if tarea_result:
                print('Título:', tarea_result[1])
                print('Descripción:', tarea_result[2])
                print('Estado:', tarea_result[5])
            input("Presione tecla enter para continuar...")
        elif option == 2:
            try:
                tarea_id = input("Ingrese el ID de la tarea que desea ver: ")
                if tarea_id == '':
                    print("Debe ingresar un ID válido.")
                    input("Presione tecla enter para continuar...")
                    continue

                tarea = admin_tareas.traer_tarea(int(tarea_id))
                if tarea is None:
                    print("No se encontró ninguna tarea con el ID proporcionado.")
                else:
                    print('Título:', tarea.titulo)
                    print('Descripción:', tarea.descripcion)
                    print('Estado:', tarea.estado)

                input("Presione tecla enter para continuar...")
                continue
                
            except TypeError:
                print("No se encontró ninguna tarea con el ID especificado.")
                input("Presione tecla enter para continuar...")
                continue
            
        elif option == 3:
            tarea_id = None
            while tarea_id is None:
                try:
                    tarea_id_input = input("Numero de ID de la tarea a actualizar: ")
                    if tarea_id_input.isdigit():
                        tarea_id = int(tarea_id_input)
                        tarea=admin_tareas.traer_tarea(tarea_id)
                        print('Título:', tarea.titulo)
                        print('Descripción:', tarea.descripcion)
                        print("Creada: ", tarea.creada)
                        print("Actualizada: ", tarea.actualizada)
                        print('Estado:', tarea.estado)
                        estado = input("Estado actual: ")
                        admin_tareas.actualizar_estado_tarea(tarea_id, estado)
                        tarea=admin_tareas.traer_tarea(tarea_id)
                        print('Nuevo Estado:', tarea.estado)
                        input("Presione tecla enter para continuar...")
                    else:
                        print("Por favor escriba un numero entero")
                    continue
                
                except TypeError:
                    print("No se encontró ninguna tarea con el ID especificado.")
                    input("Presione tecla enter para continuar...")
                    continue
                    
        elif option == 4:
            tarea_id = None
            while tarea_id is None:
                try:
                    tarea_id = input("Ingrese el ID de la tarea que desea eliminar: ")
                    if tarea_id.isdigit():
                        tarea_id = int(tarea_id)
                        tarea=admin_tareas.traer_tarea(tarea_id)
                    
                        print('Título:', tarea.titulo)
                        print('Descripción:', tarea.descripcion)
                        print("Creada: ", tarea.creada)
                        print('Estado:', "ELIMINADA")
                        admin_tareas.eliminar_tarea(tarea_id)
                        input("Presione tecla enter para continuar...")
                        continue
                    else:
                        print("Debe ingresar un ID válido.")
                        input("Presione tecla enter para continuar...")
                        continue
                    
                except TypeError:
                    print("No se encontró ninguna tarea con el ID especificado.")
                    input("Presione tecla enter para continuar...")
                    continue 

        elif option == 5:
            tarea_query = '''
                SELECT id, titulo, descripcion, creada, actualizada, estado
                FROM tareas
            '''
            admin_tareas.cursor.execute(tarea_query)
            tarea_rows = admin_tareas.cursor.fetchall()

            tabla = PrettyTable()
            tabla.field_names = ['id', 'Tarea', 'Descripcion', 'Creada', 'Actualizada', 'Estado']

            for tarea_row in tarea_rows:
                fila = [tarea_row[0], tarea_row[1], tarea_row[2], tarea_row[3], tarea_row[4], tarea_row[5]]
                tabla.add_row(fila)

            print(tabla)
            input("Presione tecla enter para continuar...")
            continue
        elif option == 6:
            data = admin_tareas.agruparActualizacionTareas()
            titles = [row[0] for row in data]
            values = [row[1] for row in data]
            plt.figure(figsize=(6, 6))
            plt.pie(values, labels=titles, autopct='%1.1f%%')
            plt.title("Porcentaje ocupado por determianda tarea")
            plt.show()
        elif option == 7:
            tarea_query = '''
                SELECT id, id_tarea, titulo, creada, actualizada, estado, fechaEliminacion
                FROM tareas_eliminadas
            '''
            admin_tareas.cursor.execute(tarea_query)
            tarea_rows = admin_tareas.cursor.fetchall()

            tabla = PrettyTable()
            tabla.field_names = ['id Elim', 'id_tarea', 'tarea', 'creada', 'actualizada', 'estado al eliminar', 'fechaEliminacion']

            for tarea_row in tarea_rows:
                fila = [tarea_row[0], tarea_row[1], tarea_row[2], tarea_row[3], tarea_row[4], tarea_row[5], tarea_row[6]]
                tabla.add_row(fila)

            print(tabla)
            input("Presione tecla enter para continuar...")
            continue
        elif option == 8:
            
            print('Que tengas un buen dia!!')
            break
               
        else:
            print("elija una de las opciones disponibles")
            pass

if __name__ == '__main__':
    main()
    
    
    
    
    
    



