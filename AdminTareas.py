from typing import List
from tinydb import TinyDB, Query
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


import json
from prettytable import PrettyTable

class Tarea:
    def __init__(self, titulo, descripcion):
        self.titulo = titulo
        self.descripcion = descripcion
        self.estado = "pendiente"
        self.creada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.actualizada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class AdminTarea:
    
    def __init__(self, db_path: str):
        self.db = TinyDB("DBAdminTareas.json")
        self.tareas = self.db.table('tareas')

    def agregar_tarea(self, tarea: Tarea) -> int:
        tarea_dict = {"titulo": tarea.titulo, "descripcion": tarea.descripcion, "estado": tarea.estado, 
                      "creada": tarea.creada, "actualizada": tarea.actualizada}
        tarea_id = self.tareas.insert(tarea_dict)
        return tarea_id

    def traer_tarea(self, tarea_id: int) -> Tarea:
        tarea_dict = self.tareas.get(doc_id=tarea_id)
        tarea = Tarea(tarea_dict["titulo"], tarea_dict["descripcion"])
        tarea.estado = tarea_dict["estado"]
        tarea.creada = tarea_dict["creada"]
        tarea.actualizada = tarea_dict["actualizada"]
        return tarea

    def actualizar_estado_tarea(self, tarea_id: int, estado: str):
        tarea_dict = {"estado": estado, "actualizada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.tareas.update(tarea_dict, doc_ids=[tarea_id])

    def eliminar_tarea(self, tarea_id: int):
        self.tareas.remove(doc_ids=[tarea_id])

    def traer_todas_tareas(self) -> List[Tarea]:
        tareas = []
        for tarea_dict in self.tareas.all():
            tarea = Tarea(tarea_dict["titulo"], tarea_dict["descripcion"])
            tarea.estado = tarea_dict["estado"]
            tarea.creada = tarea_dict["creada"]
            tarea.actualizada = tarea_dict["actualizada"]
            tareas.append(tarea)
        return tareas
def main():
    admin_tareas = AdminTarea("DBAdminTareas.json")
    while True:
        print('\n\nMenu Administrador de Tareas')
        print('1. Agregar tarea')
        print('2. Ver tarea')
        print('3. Actualizar estado de tarea')
        print('4. Eliminar tarea')
        print('5. Ver todas las tareas')
        print('6. Salir')

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
            proximoId = admin_tareas.tareas._get_next_id()-1
            traeTarea=admin_tareas.traer_tarea(int(proximoId))
            print('Título:', traeTarea.titulo)
            print('Descripción:', traeTarea.descripcion)
            print('Estado:', traeTarea.estado)
            input("Presione tecla enter para continuar...")
        elif option == 2:
            try:
                tarea_id = input("Ingrese el ID de la tarea que desea ver: ")
                if tarea_id == '':
                        print("Debe ingresar un ID válido.")
                        input("Presione tecla enter para continuar...")
                        continue
                tarea=admin_tareas.traer_tarea(tarea_id)
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
            
            with open("DBAdminTareas.json") as f:
                data_dict = json.load(f)

            tareas_dict = data_dict['tareas'] 
            tabla = PrettyTable()
            tabla.field_names = ['id', 'Tarea', 'Descripcion', 'Creada', 'Actualizada', 'Estado']

            for id_tarea, tarea in tareas_dict.items(): 
                fila = [int(id_tarea), tarea['titulo'], tarea['descripcion'], tarea['creada'], tarea['actualizada'], tarea['estado']]
                tabla.add_row(fila)

            print(tabla)
            input("Presione tecla enter para continuar...")
            continue
        elif option == 6:
            
            print('Que tengas un buen dia!!')
            break
        
        
        else:
            print("elija una de las opciones disponibles")
            pass

if __name__ == '__main__':
    main()
    
    
    
    
    
    



