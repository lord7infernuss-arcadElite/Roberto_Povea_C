import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import random

# ==========================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ==========================================
# Cambia estos datos por los de tu MySQL local
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysqlpassword', # <--- CAMBIAR ESTO
    'database': 'agencia_vehiculos'
}

def crear_conexion():
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        return conexion
    except mysql.connector.Error as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la BD: {e}")
        return None

# ==========================================
# FUNCIONES CRUD (Lógica de Negocio)
# ==========================================

def inicializar_tabla():
    """Crea la tabla si no existe."""
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Vehiculos (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                Marca VARCHAR(50) NOT NULL,
                Modelo VARCHAR(50) NOT NULL,
                Año INT,
                Combustible VARCHAR(20),
                Disponible BOOLEAN DEFAULT TRUE
            )
        """)
        conexion.commit()
        cursor.close()
        conexion.close()

def agregar_vehiculo(marca, modelo, anio, combustible):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            sql = "INSERT INTO Vehiculos (Marca, Modelo, Año, Combustible) VALUES (%s, %s, %s, %s)"
            valores = (marca, modelo, anio, combustible)
            cursor.execute(sql, valores)
            conexion.commit()
            messagebox.showinfo("Éxito", "Vehículo agregado correctamente.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al insertar: {e}")
        finally:
            cursor.close()
            conexion.close()

def obtener_vehiculos():
    conexion = crear_conexion()
    vehiculos = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT ID, Marca, Modelo, Año, Combustible, Disponible FROM Vehiculos")
            vehiculos = cursor.fetchall()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al leer: {e}")
        finally:
            cursor.close()
            conexion.close()
    return vehiculos

def actualizar_disponibilidad(id_vehiculo, nuevo_estado):
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            sql = "UPDATE Vehiculos SET Disponible = %s WHERE ID = %s"
            cursor.execute(sql, (nuevo_estado, id_vehiculo))
            conexion.commit()
            messagebox.showinfo("Éxito", "Estado actualizado correctamente.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error al actualizar: {e}")
        finally:
            cursor.close()
            conexion.close()

# ==========================================
# INTERFAZ GRÁFICA (Tkinter)
# ==========================================

class AgenciaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agencia de Alquiler de Vehículos - Evaluación Final")
        self.root.geometry("800x600")
        
        # Inicializar BD
        inicializar_tabla()

        # --- Frame de Formulario ---
        frame_form = tk.LabelFrame(root, text="Registrar Nuevo Vehículo", padx=10, pady=10)
        frame_form.pack(padx=10, pady=10, fill="x")

        tk.Label(frame_form, text="Marca:").grid(row=0, column=0, sticky="e", pady=5)
        self.entry_marca = tk.Entry(frame_form, width=30)
        self.entry_marca.grid(row=0, column=1, pady=5)

        tk.Label(frame_form, text="Modelo:").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_modelo = tk.Entry(frame_form, width=30)
        self.entry_modelo.grid(row=1, column=1, pady=5)

        tk.Label(frame_form, text="Año:").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_anio = tk.Entry(frame_form, width=30)
        self.entry_anio.grid(row=2, column=1, pady=5)

        tk.Label(frame_form, text="Combustible:").grid(row=3, column=0, sticky="e", pady=5)
        self.combo_combustible = ttk.Combobox(frame_form, values=["Gasolina", "Diésel", "Híbrido", "Eléctrico"], width=27)
        self.combo_combustible.grid(row=3, column=1, pady=5)
        self.combo_combustible.current(0)

        btn_agregar = tk.Button(frame_form, text="Agregar Vehículo", command=self.agregar, bg="green", fg="white")
        btn_agregar.grid(row=4, column=0, columnspan=2, pady=10)

        # --- Frame de Lista (Treeview) ---
        frame_lista = tk.LabelFrame(root, text="Lista de Vehículos", padx=10, pady=10)
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(frame_lista, columns=("ID", "Marca", "Modelo", "Año", "Combustible", "Disponible"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Marca", text="Marca")
        self.tree.heading("Modelo", text="Modelo")
        self.tree.heading("Año", text="Año")
        self.tree.heading("Combustible", text="Combustible")
        self.tree.heading("Disponible", text="Disponible")
        
        self.tree.column("ID", width=50)
        self.tree.column("Marca", width=100)
        self.tree.column("Modelo", width=100)
        self.tree.column("Año", width=60)
        self.tree.column("Combustible", width=100)
        self.tree.column("Disponible", width=80)
        
        self.tree.pack(fill="both", expand=True)

        # --- Frame de Acciones ---
        frame_acciones = tk.Frame(root)
        frame_acciones.pack(pady=10)

        btn_mostrar = tk.Button(frame_acciones, text="Mostrar Vehículos", command=self.cargar_vehiculos, bg="blue", fg="white")
        btn_mostrar.pack(side="left", padx=5)

        btn_cambiar_estado = tk.Button(frame_acciones, text="Cambiar Disponibilidad", command=self.cambiar_disponibilidad, bg="orange", fg="black")
        btn_cambiar_estado.pack(side="left", padx=5)

        btn_salir = tk.Button(frame_acciones, text="Salir", command=root.quit, bg="red", fg="white")
        btn_salir.pack(side="left", padx=5)

        # Cargar datos al inicio
        self.cargar_vehiculos()

    def agregar(self):
        marca = self.entry_marca.get()
        modelo = self.entry_modelo.get()
        anio = self.entry_anio.get()
        combustible = self.combo_combustible.get()

        if not marca or not modelo or not anio:
            messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos.")
            return

        try:
            anio = int(anio)
        except ValueError:
            messagebox.showerror("Error", "El año debe ser un número entero.")
            return

        agregar_vehiculo(marca, modelo, anio, combustible)
        self.limpiar_campos()
        self.cargar_vehiculos()

    def cargar_vehiculos(self):
        # Limpiar tabla
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        vehiculos = obtener_vehiculos()
        for v in vehiculos:
            # Convertir booleano a texto para mostrar
            disponible_txt = "Sí" if v[5] else "No"
            self.tree.insert("", "end", values=(v[0], v[1], v[2], v[3], v[4], disponible_txt))

    def cambiar_disponibilidad(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Por favor, seleccione un vehículo de la lista.")
            return
        
        item = self.tree.item(seleccion)
        id_vehiculo = item['values'][0]
        estado_actual = item['values'][5]
        
        # Cambiar estado
        nuevo_estado = not (estado_actual == "Sí")
        actualizar_disponibilidad(id_vehiculo, nuevo_estado)
        self.cargar_vehiculos()

    def limpiar_campos(self):
        self.entry_marca.delete(0, tk.END)
        self.entry_modelo.delete(0, tk.END)
        self.entry_anio.delete(0, tk.END)
        self.combo_combustible.current(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AgenciaApp(root)
    root.mainloop()