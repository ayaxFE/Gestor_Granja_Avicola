import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import db_local

class AppGranjaPando:
    def __init__(self, root):
        self.root = root
        self.root.title("Granja Pando - Sistema de Gestión")
        self.root.geometry("400x500")
        self.root.configure(bg="#f4f6f9") # Color de fondo moderno y limpio
        
        # Configurar estilos modernos
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Arial', 11, 'bold'), padding=10)
        self.style.configure('TLabel', background="#f4f6f9", font=('Arial', 10))
        self.style.configure('Titulo.TLabel', font=('Arial', 16, 'bold'), foreground="#2c3e50")
        
        self.usuario_actual = None
        self.pantalla_login()

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==========================================
    # 1. PANTALLA DE LOGIN (CONECTADA A SQLITE)
    # ==========================================
    def pantalla_login(self):
        self.limpiar_ventana()
        self.root.geometry("350x450")

        ttk.Label(self.root, text="🐔 GRANJA AVICOLA", style='Titulo.TLabel').pack(pady=(40, 10))
        ttk.Label(self.root, text="Control Operativo").pack(pady=(0, 30))
        
        ttk.Label(self.root, text="(respetar mayúsculas y minúsculas)\nUsuario:").pack(anchor="w", padx=50)
        self.ent_user = ttk.Entry(self.root, font=('Arial', 12))
        self.ent_user.pack(fill="x", padx=50, pady=5)
        
        ttk.Label(self.root, text="Contraseña:").pack(anchor="w", padx=50, pady=(10,0))
        self.ent_pw = ttk.Entry(self.root, show="*", font=('Arial', 12))
        self.ent_pw.pack(fill="x", padx=50, pady=5)
        
        btn_login = ttk.Button(self.root, text="INGRESAR", command=self.validar_acceso)
        btn_login.pack(fill="x", padx=50, pady=30)
        
        btn_registro = ttk.Button(self.root, text="📝 Crear Cuenta Nueva", command=self.abrir_ventana_registro)
        btn_registro.pack(fill="x", padx=50, pady=(0, 20))

    def validar_acceso(self):
        u = self.ent_user.get()
        p = self.ent_pw.get()
        
        # Conexión real a la base de datos local
        conn = db_local.conectar_local()
        res = conn.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (u, p)).fetchone()
        conn.close()
        
        if res:
            self.usuario_actual = dict(res) # Guardamos los datos de la sesión
            self.pantalla_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    # ==========================================
    # 2. MENÚ PRINCIPAL (ENRUTADOR POR ROL)
    # ==========================================
    def pantalla_principal(self):
        self.limpiar_ventana()
        self.root.geometry("450x650")

        rol = self.usuario_actual['rol']
        nombre = self.usuario_actual['username']

        ttk.Label(self.root, text=f"Panel de Control", style='Titulo.TLabel').pack(pady=(20, 5))
        ttk.Label(self.root, text=f"👤 Usuario: {nombre} | Rol: {rol.upper()}").pack(pady=(0, 20))

        frame_botones = tk.Frame(self.root, bg="#f4f6f9")
        frame_botones.pack(fill="both", expand=True, padx=40)

        # --- MENÚ SUPERVISOR ---
        if rol == 'supervisor':
            ttk.Button(frame_botones, text="🏢 Gestionar Dueños y Granjas", 
                       command=self.abrir_ventana_infraestructura).pack(fill="x", pady=8)
            
            ttk.Button(frame_botones, text="🏗️ Administrar Galpones", 
                       command=self.abrir_ventana_galpones).pack(fill="x", pady=8)
            
            ttk.Button(frame_botones, text="📊 Ver Reportes Analíticos", 
                       command=self.abrir_ventana_reportes).pack(fill="x", pady=8)

        # --- MENÚ GRANJERO ---
        elif rol == 'granjero':
            ttk.Label(frame_botones, text="Operaciones Diarias:", font=('Arial', 10, 'bold'), background="#f4f6f9").pack(anchor="w", pady=5)
            
            # Conectados a las ventanas reales
            ttk.Button(frame_botones, text="🐣 Registrar Ingreso de Lote", 
                       command=self.abrir_ventana_lote).pack(fill="x", pady=8)
            
            ttk.Button(frame_botones, text="💀 Registrar Mortandad Diaria", 
                       command=self.abrir_ventana_mortandad).pack(fill="x", pady=8)
            
            ttk.Button(frame_botones, text="🌾 Registrar Ingreso de Alimento", 
                       command=self.abrir_ventana_alimento).pack(fill="x", pady=8)
            
            ttk.Label(frame_botones, text="Consultas:", font=('Arial', 10, 'bold'), background="#f4f6f9").pack(anchor="w", pady=(15,5))
            
            ttk.Button(frame_botones, text="📊 Ver Mis Reportes", 
                       command=self.abrir_ventana_reportes).pack(fill="x", pady=8)

        ttk.Button(self.root, text="🚪 Cerrar Sesión", command=self.pantalla_login).pack(pady=20)

    # ==========================================
    # 3. MÓDULOS OPERATIVOS DEL GRANJERO
    # ==========================================
    def abrir_ventana_lote(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Nuevo Lote de Aves")
        ventana.geometry("350x450")
        ventana.configure(bg="#f4f6f9")

        id_g = self.usuario_actual['id_granja']
        ttk.Label(ventana, text="🐣 INGRESO DE AVES", style='Titulo.TLabel').pack(pady=15)

        # Lógica de negocio: Solo galpones VACÍOS de su granja
        galpones = db_local.obtener_galpones_por_granja(id_g, solo_vacios=True)
        if not galpones:
            messagebox.showwarning("Aviso", "No hay galpones vacíos disponibles en su granja.")
            ventana.destroy()
            return

        ttk.Label(ventana, text="Seleccione Galpón Libre:").pack(anchor="w", padx=40)
        opciones = [f"{g['id_galpon']} - Galpón {g['numero_galpon']} (Cap: {g['capacidad']})" for g in galpones]
        combo_gal = ttk.Combobox(ventana, values=opciones, state="readonly", font=('Arial', 11))
        combo_gal.pack(fill="x", padx=40, pady=5)
        if opciones: combo_gal.current(0)

        ttk.Label(ventana, text="Cantidad de Aves:").pack(anchor="w", padx=40, pady=(10,0))
        ent_cant = ttk.Entry(ventana, font=('Arial', 11))
        ent_cant.pack(fill="x", padx=40, pady=5)

        def guardar():
            if not ent_cant.get().isdigit():
                messagebox.showerror("Error", "La cantidad debe ser un número entero.")
                return
            
            id_gal = combo_gal.get().split(" - ")[0]
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            db_local.registrar_lote(id_gal, fecha_hoy, int(ent_cant.get()))
            
            messagebox.showinfo("Éxito", "Lote iniciado. El galpón ahora está ACTIVO.")
            ventana.destroy()

        ttk.Button(ventana, text="🚀 Iniciar Ciclo", command=guardar).pack(pady=25)

    def abrir_ventana_mortandad(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Reporte de Mortandad")
        ventana.geometry("350x500") 
        ventana.configure(bg="#f4f6f9")
        
        id_g = self.usuario_actual['id_granja']
        ttk.Label(ventana, text="💀 CARGA DE MORTANDAD", style='Titulo.TLabel').pack(pady=15)

        # Lógica: Solo galpones ACTIVOS
        galpones = db_local.obtener_galpones_por_granja(id_g)
        activos = [f"{g['id_galpon']} - Galpón {g['numero_galpon']}" for g in galpones if g['estado'] == 'activo']

        if not activos:
            messagebox.showwarning("Aviso", "No tiene galpones con lotes activos actualmente.")
            ventana.destroy()
            return

        ttk.Label(ventana, text="Seleccione Galpón:").pack(anchor="w", padx=40)
        combo_gal = ttk.Combobox(ventana, values=activos, state="readonly", font=('Arial', 11))
        combo_gal.pack(fill="x", padx=40, pady=5)
        if activos: combo_gal.current(0)

        # Campo de Fecha Manual
        ttk.Label(ventana, text="Fecha del suceso (AAAA-MM-DD):").pack(anchor="w", padx=40, pady=(10,0))
        ent_fecha = ttk.Entry(ventana, font=('Arial', 11))
        ent_fecha.insert(0, datetime.now().strftime("%Y-%m-%d")) 
        ent_fecha.pack(fill="x", padx=40, pady=5)
        
        ttk.Label(ventana, text="Aves muertas en esa fecha:").pack(anchor="w", padx=40, pady=(10,0))
        ent_m = ttk.Entry(ventana, font=('Arial', 11))
        ent_m.pack(fill="x", padx=40, pady=5)

        def guardar():
            fecha_txt = ent_fecha.get().strip()
            muertes_txt = ent_m.get().strip()

            if not muertes_txt.isdigit():
                messagebox.showerror("Error", "La cantidad de muertes debe ser un número entero.")
                return

            try:
                # 1. Validamos formato y convertimos a objeto Date
                fecha_ingresada = datetime.strptime(fecha_txt, "%Y-%m-%d").date()
                fecha_hoy = datetime.now().date()
                
                # 2. REGLA DE NEGOCIO: Bloqueo de fechas futuras
                if fecha_ingresada > fecha_hoy:
                    messagebox.showwarning("Atención", "No se pueden registrar datos con fechas futuras.")
                    return
                    
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use AAAA-MM-DD (ej: 2026-04-26)")
                return

            id_gal = combo_gal.get().split(" - ")[0]
            lote = db_local.obtener_lote_activo(id_gal)
            
            if lote:
                db_local.registrar_mortalidad(lote['id_lote'], fecha_txt, int(muertes_txt))
                messagebox.showinfo("Éxito", f"Mortandad del día {fecha_txt} registrada correctamente.")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se encontró un lote activo en este galpón.")

        ttk.Button(ventana, text="💾 Guardar Registro", command=guardar).pack(pady=25)
        
    def abrir_ventana_alimento(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Ingreso de Alimento")
        ventana.geometry("350x500")
        ventana.configure(bg="#f4f6f9")

        id_g = self.usuario_actual['id_granja']
        ttk.Label(ventana, text="🌾 RECEPCIÓN DE ALIMENTO", style='Titulo.TLabel').pack(pady=15)

        # 1. Fecha
        ttk.Label(ventana, text="Fecha de Recepción (AAAA-MM-DD):").pack(anchor="w", padx=40, pady=(10,0))
        ent_fecha = ttk.Entry(ventana, font=('Arial', 11))
        ent_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ent_fecha.pack(fill="x", padx=40, pady=5)

        # 2. Fase de Alimentación (F1 a F5)
        ttk.Label(ventana, text="Fase de Alimentación:").pack(anchor="w", padx=40, pady=(10,0))
        combo_fase = ttk.Combobox(ventana, values=["F1", "F2", "F3", "F4", "F5"], state="readonly", font=('Arial', 11))
        combo_fase.pack(fill="x", padx=40, pady=5)
        combo_fase.current(0) # Selecciona F1 por defecto

        # 3. Kilos Recibidos
        ttk.Label(ventana, text="Cantidad Recibida (Kg):").pack(anchor="w", padx=40, pady=(10,0))
        ent_kg = ttk.Entry(ventana, font=('Arial', 11))
        ent_kg.pack(fill="x", padx=40, pady=5)

        # 4. Número de Remito (Comprobante)
        ttk.Label(ventana, text="Nro. de Remito:").pack(anchor="w", padx=40, pady=(10,0))
        ent_remito = ttk.Entry(ventana, font=('Arial', 11))
        ent_remito.pack(fill="x", padx=40, pady=5)

        def guardar():
            fecha_txt = ent_fecha.get().strip()
            fase_txt = combo_fase.get()
            kg_txt = ent_kg.get().strip()
            remito_txt = ent_remito.get().strip()

            if not kg_txt or not remito_txt:
                messagebox.showwarning("Atención", "Complete la cantidad y el Nro. de Remito.")
                return

            try:
                # Validamos que los Kg sean un número (permite decimales)
                kg_float = float(kg_txt)
            except ValueError:
                messagebox.showerror("Error", "La cantidad de Kg debe ser un número (use punto para decimales).")
                return

            try:
                # Reutilizamos la lógica de validación de fechas
                fecha_ingresada = datetime.strptime(fecha_txt, "%Y-%m-%d").date()
                fecha_hoy = datetime.now().date()
                if fecha_ingresada > fecha_hoy:
                    messagebox.showwarning("Atención", "No se pueden registrar remitos con fechas futuras.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use AAAA-MM-DD")
                return

            # Llamada a la base de datos
            exito = db_local.registrar_ingreso_alimento(id_g, fecha_txt, fase_txt, kg_float, remito_txt)
            
            if exito:
                messagebox.showinfo("Éxito", f"Se ingresaron correctamente {kg_float} Kg de la fase {fase_txt}.")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "Ocurrió un problema al guardar el registro en la base de datos.")

        ttk.Button(ventana, text="💾 Guardar Ingreso", command=guardar).pack(pady=25)

    # ==================================================
    # 4. MÓDULO DE REPORTES (Vista Supervisor/Granjero)
    # ==================================================

    def abrir_ventana_reportes(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Reportes de Producción")
        ventana.geometry("750x650")
        ventana.configure(bg="#f4f6f9")

        ttk.Label(ventana, text="📊 Reportes de Mortandad y Alimento", style='Titulo.TLabel').pack(pady=15)

        # --- CREACIÓN DEL NOTEBOOK (PESTAÑAS) ---
        notebook = ttk.Notebook(ventana)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # ======================
        # PESTAÑA 1: MORTANDAD 
        # ======================
        tab_mortandad = ttk.Frame(notebook)
        notebook.add(tab_mortandad, text="💀 Mortandad por Galpón")

        # --- PANEL DE FILTROS ---
        frame_filtros = ttk.LabelFrame(tab_mortandad, text=" Filtros de Búsqueda ", padding=10)
        frame_filtros.pack(fill="x", padx=20, pady=10)

        # 1. Filtro de Granja
        tk.Label(frame_filtros, text="Seleccione Granja:", bg="#f4f6f9").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        combo_granja = ttk.Combobox(frame_filtros, state="readonly", width=30)
        combo_granja.grid(row=0, column=1, padx=5, pady=5)

        # 2. Filtro de Galpón
        tk.Label(frame_filtros, text="Seleccione Galpón:", bg="#f4f6f9").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        combo_galpon = ttk.Combobox(frame_filtros, state="readonly", width=20)
        combo_galpon.grid(row=0, column=3, padx=5, pady=5)

        # Lógica de carga de datos según el Rol
        def cargar_galpones(event=None):
            # Limpiar el combo de galpones cada vez que cambia la granja
            combo_galpon.set("")
            if not combo_granja.get(): return
            
            id_g = combo_granja.get().split(" - ")[0]
            galpones_db = db_local.obtener_galpones_por_granja(id_g)
            combo_galpon.config(values=[f"{g['id_galpon']} - Galpón {g['numero_galpon']}" for g in galpones_db])

        if self.usuario_actual['rol'] == 'supervisor':
            # El supervisor ve todas las granjas
            granjas_db = db_local.obtener_granjas()
            opciones_g = [f"{g['id_granja']} - {g['nombre_granja']}" for g in granjas_db]
            combo_granja.config(values=opciones_g)
            # Evento: cuando el supervisor elige una granja, se cargan sus galpones
            combo_granja.bind("<<ComboboxSelected>>", cargar_galpones)
        else:
            # El granjero solo ve su propia granja
            id_g_fija = self.usuario_actual['id_granja']
            # Buscamos el nombre para mostrarlo
            conn = db_local.conectar_local()
            g_nombre = conn.execute("SELECT nombre_granja FROM granjas WHERE id_granja = ?", (id_g_fija,)).fetchone()
            conn.close()
            
            combo_granja.set(f"{id_g_fija} - {g_nombre['nombre_granja']}")
            combo_granja.config(state="disabled") # Bloqueado
            
            # Cargamos sus galpones directamente
            cargar_galpones()

        # --- TABLA DE RESULTADOS ---
        frame_tabla = tk.Frame(tab_mortandad, bg="#f4f6f9")
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        columnas = ("Fecha", "Detalle", "Mortalidad")
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, anchor="center")
        
        # Scrollbar agregado a tu tabla original
        scrollbar_mort = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar_mort.set)
        tabla.pack(side="left", fill="both", expand=True)
        scrollbar_mort.pack(side="right", fill="y")

        # --- LÓGICA DEL BOTÓN GENERAR ---
        def generar():
            if not combo_galpon.get():
                messagebox.showwarning("Atención", "Seleccione un galpón.")
                return
            
            for item in tabla.get_children(): tabla.delete(item)
            
            id_gal = combo_galpon.get().split(" - ")[0]
            datos = db_local.generar_estadisticas_mortandad(id_gal)
            
            if datos:
                lbl_resumen.config(text=f"Población Inicial: {datos['cantidad_inicial']} | "
                                        f"Muertes: {datos['total_muertes']} | "
                                        f"Tasa: {datos['porcentaje_mortandad']}%",
                                   fg="red" if datos['porcentaje_mortandad'] > 5 else "green")
                
                for fila in datos['detalle_diario']:
                    tabla.insert("", "end", values=(fila['fecha'], "Registro Diario", f"{fila['mortalidad']} aves"))
            else:
                lbl_resumen.config(text="Galpón sin lotes activos.", fg="gray")

        ttk.Button(frame_filtros, text="🔍 Generar", command=generar).grid(row=0, column=4, padx=10)

        lbl_resumen = tk.Label(tab_mortandad, text="Seleccione un galpón para ver el análisis.", 
                              font=('Arial', 11, 'bold'), bg="#f4f6f9")
        lbl_resumen.pack(pady=20)


        # ================================
        # PESTAÑA 2: INGRESO DE ALIMENTO 
        # ================================
        tab_alimento = ttk.Frame(notebook)
        notebook.add(tab_alimento, text="🌾 Recepción de Alimento")

        # --- PANEL DE FILTROS ALIMENTO ---
        frame_filtros_alim = ttk.LabelFrame(tab_alimento, text=" Filtros de Búsqueda ", padding=10)
        frame_filtros_alim.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_filtros_alim, text="Seleccione Granja:", bg="#f4f6f9").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        combo_granja_alim = ttk.Combobox(frame_filtros_alim, state="readonly", width=30)
        combo_granja_alim.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_filtros_alim, text="Fase de Alimento:", bg="#f4f6f9").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        combo_fase = ttk.Combobox(frame_filtros_alim, values=["F1", "F2", "F3", "F4", "F5"], state="readonly", width=15)
        combo_fase.grid(row=0, column=3, padx=5, pady=5)
        combo_fase.current(0) # F1 por defecto

        # Replicamos la lógica de roles para la granja en esta pestaña
        if self.usuario_actual['rol'] == 'supervisor':
            combo_granja_alim.config(values=opciones_g) # Usa las opciones que ya cargamos arriba
        else:
            combo_granja_alim.set(f"{id_g_fija} - {g_nombre['nombre_granja']}")
            combo_granja_alim.config(state="disabled")

        # --- TABLA DE RESULTADOS ALIMENTO ---
        frame_tabla_alim = tk.Frame(tab_alimento, bg="#f4f6f9")
        frame_tabla_alim.pack(fill="both", expand=True, padx=20, pady=10)

        columnas_alim = ("Fecha de Ingreso", "Cantidad Recibida", "Nro. Remito")
        tabla_alim = ttk.Treeview(frame_tabla_alim, columns=columnas_alim, show="headings")
        for col in columnas_alim:
            tabla_alim.heading(col, text=col)
            tabla_alim.column(col, anchor="center")
        
        scrollbar_alim = ttk.Scrollbar(frame_tabla_alim, orient="vertical", command=tabla_alim.yview)
        tabla_alim.configure(yscrollcommand=scrollbar_alim.set)
        tabla_alim.pack(side="left", fill="both", expand=True)
        scrollbar_alim.pack(side="right", fill="y")

        # 1. PRIMERO definimos la etiqueta (Adiós a la línea amarilla)
        lbl_resumen_alim = tk.Label(tab_alimento, text="Seleccione Fase para ver el stock ingresado.",
                                   font=('Arial', 11, 'bold'), bg="#f4f6f9")
        lbl_resumen_alim.pack(pady=20)

        # 2. LUEGO definimos la función (Se irá el color gris al conectarla abajo)
        def generar_alim():
            if not combo_granja_alim.get():
                messagebox.showwarning("Atención", "Seleccione una granja.")
                return

            for item in tabla_alim.get_children(): tabla_alim.delete(item)

            id_g = combo_granja_alim.get().split(" - ")[0]
            fase = combo_fase.get()
            
            # Consultas a la base de datos
            datos_alim = db_local.obtener_reporte_alimento(id_g, fase)
            proyeccion = db_local.obtener_proyeccion_alimento(id_g, fase)

            # Llenar la tabla
            if datos_alim['detalle']:
                for fila in datos_alim['detalle']:
                    tabla_alim.insert("", "end", values=(fila['fecha'], f"{fila['cantidad_recibida_kg']} Kg", fila['remito']))
            
            # Actualizar el panel de resumen
            if proyeccion['poblacion_total'] > 0:
                texto_proyeccion = (
                    f"Aves Totales: {proyeccion['poblacion_total']} | "
                    f"Necesario: {proyeccion['kilos_requeridos']} Kg | "
                    f"Recibido: {proyeccion['kilos_recibidos']} Kg\n"
                    f"🚨 FALTAN ENVIAR: {proyeccion['kilos_faltantes']} Kg para completar la fase {fase}"
                )
                lbl_resumen_alim.config(text=texto_proyeccion, fg="#E65100" if proyeccion['kilos_faltantes'] > 0 else "#2E7D32")
            else:
                lbl_resumen_alim.config(text="No hay lotes activos para calcular proyección.", fg="gray")

        # 3. FINALMENTE creamos el botón y lo conectamos a la función
        ttk.Button(frame_filtros_alim, text="🔍 Generar", command=generar_alim).grid(row=0, column=4, padx=10)
        
    # ==========================================
    # 5. PANTALLA DE REGISTRO DE USUARIO
    # ==========================================
    def abrir_ventana_registro(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Registro de Usuario")
        ventana.geometry("350x450")
        ventana.configure(bg="#f4f6f9")

        ttk.Label(ventana, text="NUEVO USUARIO", style='Titulo.TLabel').pack(pady=15)

        ttk.Label(ventana, text="Nombre de Usuario:").pack(anchor="w", padx=40)
        ent_user = ttk.Entry(ventana, font=('Arial', 11))
        ent_user.pack(fill="x", padx=40, pady=5)

        ttk.Label(ventana, text="Contraseña:").pack(anchor="w", padx=40)
        ent_pw = ttk.Entry(ventana, show="*", font=('Arial', 11))
        ent_pw.pack(fill="x", padx=40, pady=5)

        ttk.Label(ventana, text="Rol del Usuario:").pack(anchor="w", padx=40)
        combo_rol = ttk.Combobox(ventana, values=["supervisor", "granjero"], state="readonly", font=('Arial', 11))
        combo_rol.pack(fill="x", padx=40, pady=5)

        frame_granja = tk.Frame(ventana, bg="#f4f6f9")
        ttk.Label(frame_granja, text="Asignar Granja:").pack(anchor="w")
        
        # Obtenemos las granjas reales de la base de datos local
        granjas_db = db_local.obtener_granjas()
        opciones_granjas = [f"{g['id_granja']} - {g['nombre_granja']}" for g in granjas_db]
        
        combo_granja = ttk.Combobox(frame_granja, values=opciones_granjas, state="readonly", font=('Arial', 11))
        combo_granja.pack(fill="x", pady=5)

        def al_cambiar_rol(event):
            if combo_rol.get() == "granjero":
                frame_granja.pack(fill="x", padx=40, pady=10)
            else:
                frame_granja.pack_forget()
                combo_granja.set("") 

        combo_rol.bind("<<ComboboxSelected>>", al_cambiar_rol)

        def registrar():
            u = ent_user.get().strip()
            p = ent_pw.get().strip()
            r = combo_rol.get()
            
            g_seleccionada = combo_granja.get()
            id_g = g_seleccionada.split(" - ")[0] if r == "granjero" and g_seleccionada else None

            if not u or not p or not r:
                messagebox.showwarning("Atención", "Complete Usuario, Contraseña y Rol.")
                return

            if r == "granjero" and not id_g:
                messagebox.showwarning("Atención", "Un granjero debe tener una granja asignada.")
                return

            # Inserción real mediante db_local
            exito = db_local.registrar_usuario(u, p, r, id_g)
            
            if exito:
                messagebox.showinfo("Éxito", f"Usuario '{u}' creado correctamente.")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear el usuario.")

        ttk.Button(ventana, text="💾 Guardar Usuario", command=registrar).pack(pady=25)
        
    # ==========================================
    # 6. GESTIÓN DE INFRAESTRUCTURA (SUPERVISOR)
    # ==========================================
    def abrir_ventana_infraestructura(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Gestión de Infraestructura")
        ventana.geometry("400x450")
        ventana.configure(bg="#f4f6f9")

        ttk.Label(ventana, text="DUEÑOS Y GRANJAS", style='Titulo.TLabel').pack(pady=15)

        # Usamos un Notebook para crear pestañas
        notebook = ttk.Notebook(ventana)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # --- PESTAÑA 1: DUEÑOS ---
        tab_dueño = ttk.Frame(notebook)
        notebook.add(tab_dueño, text="👤 Nuevo Dueño")

        ttk.Label(tab_dueño, text="Nombre:").pack(anchor="w", padx=20, pady=(15,0))
        ent_nom = ttk.Entry(tab_dueño, font=('Arial', 11)); ent_nom.pack(fill="x", padx=20, pady=5)

        ttk.Label(tab_dueño, text="Apellido:").pack(anchor="w", padx=20)
        ent_ape = ttk.Entry(tab_dueño, font=('Arial', 11)); ent_ape.pack(fill="x", padx=20, pady=5)

        ttk.Label(tab_dueño, text="Contacto (Tel/Email):").pack(anchor="w", padx=20)
        ent_con = ttk.Entry(tab_dueño, font=('Arial', 11)); ent_con.pack(fill="x", padx=20, pady=5)

        def guardar_dueño():
            if ent_nom.get() and ent_ape.get():
                db_local.registrar_dueño(ent_nom.get(), ent_ape.get(), ent_con.get())
                messagebox.showinfo("Éxito", "Dueño registrado correctamente.")
                # Limpiar campos
                ent_nom.delete(0, 'end'); ent_ape.delete(0, 'end'); ent_con.delete(0, 'end')
                actualizar_combo_dueños() # Refresca la otra pestaña
            else:
                messagebox.showwarning("Atención", "Nombre y Apellido son obligatorios.")

        ttk.Button(tab_dueño, text="💾 Guardar Dueño", command=guardar_dueño).pack(pady=20)

        # --- PESTAÑA 2: GRANJAS ---
        tab_granja = ttk.Frame(notebook)
        notebook.add(tab_granja, text="🏠 Nueva Granja")

        ttk.Label(tab_granja, text="Nombre de la Granja:").pack(anchor="w", padx=20, pady=(15,0))
        ent_granja = ttk.Entry(tab_granja, font=('Arial', 11)); ent_granja.pack(fill="x", padx=20, pady=5)

        ttk.Label(tab_granja, text="Ubicación:").pack(anchor="w", padx=20)
        ent_ubi = ttk.Entry(tab_granja, font=('Arial', 11)); ent_ubi.pack(fill="x", padx=20, pady=5)

        ttk.Label(tab_granja, text="Asignar Dueño:").pack(anchor="w", padx=20)
        combo_dueño = ttk.Combobox(tab_granja, state="readonly", font=('Arial', 11))
        combo_dueño.pack(fill="x", padx=20, pady=5)

        def actualizar_combo_dueños():
            dueños_db = db_local.obtener_dueños()
            opciones = [f"{d['id_dueño']} - {d['nombre_completo']}" for d in dueños_db]
            combo_dueño.config(values=opciones)

        actualizar_combo_dueños()

        def guardar_granja():
            if ent_granja.get() and combo_dueño.get():
                id_d = combo_dueño.get().split(" - ")[0]
                db_local.registrar_granja(id_d, ent_granja.get(), ent_ubi.get())
                messagebox.showinfo("Éxito", "Granja creada correctamente.")
                ent_granja.delete(0, 'end'); ent_ubi.delete(0, 'end'); combo_dueño.set("")
            else:
                messagebox.showwarning("Atención", "El nombre y el dueño son obligatorios.")

        ttk.Button(tab_granja, text="💾 Guardar Granja", command=guardar_granja).pack(pady=20)

    # ==========================================
    # 7. GESTIÓN DE GALPONES (SUPERVISOR)
    # ==========================================
    def abrir_ventana_galpones(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Gestión de Galpones")
        ventana.geometry("350x450")
        ventana.configure(bg="#f4f6f9")

        ttk.Label(ventana, text="NUEVO GALPÓN", style='Titulo.TLabel').pack(pady=15)

        ttk.Label(ventana, text="Seleccionar Granja:").pack(anchor="w", padx=40)
        granjas_db = db_local.obtener_granjas()
        opciones_g = [f"{g['id_granja']} - {g['nombre_granja']}" for g in granjas_db]
        
        combo_granja = ttk.Combobox(ventana, values=opciones_g, state="readonly", font=('Arial', 11))
        combo_granja.pack(fill="x", padx=40, pady=5)

        ttk.Label(ventana, text="Número o Identificador:").pack(anchor="w", padx=40, pady=(10,0))
        ent_num = ttk.Entry(ventana, font=('Arial', 11)); ent_num.pack(fill="x", padx=40, pady=5)

        ttk.Label(ventana, text="Capacidad (Cant. Aves):").pack(anchor="w", padx=40)
        ent_cap = ttk.Entry(ventana, font=('Arial', 11)); ent_cap.pack(fill="x", padx=40, pady=5)

        def guardar_galpon():
            if not combo_granja.get() or not ent_num.get() or not ent_cap.get():
                messagebox.showwarning("Atención", "Complete todos los campos.")
                return
            
            if not ent_cap.get().isdigit():
                messagebox.showerror("Error", "La capacidad debe ser un número entero.")
                return

            id_g = combo_granja.get().split(" - ")[0]
            db_local.registrar_galpon(id_g, ent_num.get(), int(ent_cap.get()))
            messagebox.showinfo("Éxito", f"Galpón {ent_num.get()} registrado correctamente.")
            ventana.destroy()

        ttk.Button(ventana, text="💾 Guardar Galpón", command=guardar_galpon).pack(pady=30)
        
if __name__ == "__main__":
    db_local.inicializar_db() # Aseguramos que las tablas existan al abrir
    root = tk.Tk()
    app = AppGranjaPando(root)
    root.mainloop()
