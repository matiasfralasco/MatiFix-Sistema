import customtkinter as ctk
from datetime import date
from tkinter import messagebox, ttk
import base_datos
import generador_pdf
import webbrowser  # <--- Importamos esto para abrir el navegador

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# --- VENTANA EMERGENTE PARA COBRAR ---
class VentanaCobro(ctk.CTkToplevel):
    def __init__(self, parent, id_trabajo, callback_actualizar):
        super().__init__(parent)
        self.title("Detalles Financieros")
        self.geometry("400x350")
        self.id_trabajo = id_trabajo
        self.callback = callback_actualizar

        self.transient(parent)
        self.grab_set()

        ctk.CTkLabel(
            self, text="Cerrar Caja del Trabajo", font=("Arial", 18, "bold")
        ).pack(pady=20)

        ctk.CTkLabel(self, text="Costo Repuestos (Tuyo):").pack(pady=(10, 0))
        self.entry_costo = ctk.CTkEntry(self, placeholder_text="0")
        self.entry_costo.pack(pady=5)

        ctk.CTkLabel(self, text="Precio Final (Al Cliente):").pack(pady=(10, 0))
        self.entry_precio = ctk.CTkEntry(self, placeholder_text="0")
        self.entry_precio.pack(pady=5)

        self.check_pagado = ctk.CTkCheckBox(self, text="¿Está Pagado?")
        self.check_pagado.pack(pady=20)

        ctk.CTkButton(
            self, text="Guardar Cambios", fg_color="green", command=self.guardar
        ).pack(pady=20)

    def guardar(self):
        try:
            costo = float(self.entry_costo.get() or 0)
            precio = float(self.entry_precio.get() or 0)
            pagado = "SI" if self.check_pagado.get() == 1 else "NO"

            base_datos.actualizar_dinero(self.id_trabajo, costo, precio, pagado)
            messagebox.showinfo("Éxito", "Valores actualizados.")
            self.callback()
            self.destroy()
        except ValueError:
            messagebox.showerror(
                "Error", "Por favor ingresa solo números en los precios."
            )


# --- APLICACIÓN PRINCIPAL ---
class AppTaller(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión - MATI-FIX")
        self.geometry("1100x650")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        base_datos.crear_tablas()

        # === MENU LATERAL ===
        self.sidebar_frame = ctk.CTkFrame(
            self, width=200, corner_radius=0, fg_color=("gray95", "gray10")
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            self.sidebar_frame,
            text="MATI-FIX\nService",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(30, 20))
        ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="gray40").grid(
            row=1, column=0, sticky="ew", padx=20, pady=(0, 20)
        )

        self.crear_boton_menu("  +  Nuevo Ingreso", self.mostrar_nuevo, 2)
        self.crear_boton_menu("  ≡  Historial", self.mostrar_historial, 3)
        self.crear_boton_menu("  $  Caja / Finanzas", self.mostrar_finanzas, 4)

        # === FRAMES ===
        self.frame_nuevo = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_historial = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.frame_finanzas = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )

        self.construir_vista_nuevo()
        self.construir_vista_historial()
        self.construir_vista_finanzas()

        self.estilar_tabla()
        self.mostrar_nuevo()

    def crear_boton_menu(self, texto, comando, fila):
        btn = ctk.CTkButton(
            self.sidebar_frame,
            text=texto,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40,
            command=comando,
        )
        btn.grid(row=fila, column=0, padx=10, pady=5, sticky="ew")

    # --- NAVEGACION ---
    def ocultar_todo(self):
        self.frame_nuevo.grid_forget()
        self.frame_historial.grid_forget()
        self.frame_finanzas.grid_forget()

    def mostrar_nuevo(self):
        self.ocultar_todo()
        self.frame_nuevo.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def mostrar_historial(self):
        self.ocultar_todo()
        self.frame_historial.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.cargar_tabla_historial()

    def mostrar_finanzas(self):
        self.ocultar_todo()
        self.frame_finanzas.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.actualizar_tablero_finanzas()

    # --- VISTA 1: NUEVO INGRESO ---
    def construir_vista_nuevo(self):
        ctk.CTkLabel(
            self.frame_nuevo, text="REGISTRAR NUEVO EQUIPO", font=("Arial", 20, "bold")
        ).pack(pady=20)
        frame_form = ctk.CTkFrame(self.frame_nuevo, fg_color="transparent")
        frame_form.pack(expand=True, fill="both", padx=20)

        # Campos
        self.crear_input(frame_form, "Nombre del Cliente (*):", 0, 0, "entry_nombre")
        self.crear_input(frame_form, "Teléfono:", 2, 0, "entry_tel")
        self.crear_input(
            frame_form,
            "Fecha:",
            4,
            0,
            "entry_fecha",
            default=date.today().strftime("%d/%m/%Y"),
        )
        self.crear_input(frame_form, "Equipo / Modelo:", 0, 1, "entry_equipo")

        ctk.CTkLabel(frame_form, text="Falla Declarada:", anchor="w").grid(
            row=2, column=1, sticky="w", pady=(10, 0)
        )
        self.entry_falla = ctk.CTkTextbox(frame_form, width=300, height=80)
        self.entry_falla.grid(row=3, column=1, pady=(5, 15))

        ctk.CTkLabel(frame_form, text="Estado Inicial:", anchor="w").grid(
            row=4, column=1, sticky="w", pady=(10, 0)
        )
        self.combo_estado = ctk.CTkComboBox(
            frame_form, values=["Pendiente", "En Revisión", "Presupuestado"], width=300
        )
        self.combo_estado.grid(row=5, column=1, pady=(5, 15))

        ctk.CTkButton(
            self.frame_nuevo,
            text="GUARDAR INGRESO",
            height=40,
            fg_color="green",
            hover_color="darkgreen",
            command=self.guardar_datos,
        ).pack(pady=30)

    def crear_input(self, parent, label, r, c, var_name, default=None):
        ctk.CTkLabel(parent, text=label, anchor="w").grid(
            row=r, column=c, sticky="w", pady=(10, 0)
        )
        entry = ctk.CTkEntry(parent, width=300)
        entry.grid(row=r + 1, column=c, padx=(0, 20) if c == 0 else 0, pady=(5, 15))
        if default:
            entry.insert(0, default)
        setattr(self, var_name, entry)

    # --- VISTA 2: HISTORIAL ---
    def construir_vista_historial(self):
        ctk.CTkLabel(
            self.frame_historial,
            text="HISTORIAL DE TRABAJOS",
            font=("Arial", 20, "bold"),
        ).pack(pady=(20, 10))

        # --- BARRA DE BÚSQUEDA ---
        frame_busqueda = ctk.CTkFrame(self.frame_historial, fg_color="transparent")
        frame_busqueda.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_busqueda = ctk.CTkEntry(
            frame_busqueda, placeholder_text="Buscar por Cliente, Equipo o Estado..."
        )
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(
            frame_busqueda, text="🔍 Buscar", width=100, command=self.filtrar_historial
        ).pack(side="left")
        ctk.CTkButton(
            frame_busqueda,
            text="Ver Todos",
            width=80,
            fg_color="gray",
            command=self.cargar_tabla_historial,
        ).pack(side="left", padx=5)

        # --- TABLA ---
        columns = (
            "id",
            "fecha",
            "cliente",
            "equipo",
            "falla",
            "estado",
            "pagado",
            "precio",
        )
        self.tabla = ttk.Treeview(
            self.frame_historial, columns=columns, show="headings", height=12
        )

        cabeceras = [
            "ID",
            "Fecha",
            "Cliente",
            "Equipo",
            "Falla",
            "Estado",
            "Pagado?",
            "Precio Final",
        ]
        anchos = [30, 80, 150, 150, 200, 100, 70, 90]

        for i, col in enumerate(columns):
            self.tabla.heading(col, text=cabeceras[i])
            self.tabla.column(
                col,
                width=anchos[i],
                anchor="center" if i != 2 and i != 3 and i != 4 else "w",
            )

        self.tabla.pack(expand=True, fill="both", padx=20, pady=(10, 20))

        # Panel de Acciones
        frame_acciones = ctk.CTkFrame(self.frame_historial, fg_color="transparent")
        frame_acciones.pack(fill="x", padx=20, pady=10)

        # Botones de Acción
        ctk.CTkButton(
            frame_acciones,
            text="X Eliminar",
            fg_color="#ef4444",
            width=80,
            command=self.eliminar_registro,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            frame_acciones,
            text="$$ Cotizar",
            fg_color="#10b981",
            width=80,
            command=self.abrir_ventana_cobro,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            frame_acciones,
            text="🖨️ PDF",
            fg_color="#3b82f6",
            width=80,
            command=self.imprimir_pdf,
        ).pack(side="left", padx=5)

        # BOTÓN WHATSAPP NUEVO
        ctk.CTkButton(
            frame_acciones,
            text="📞 WhatsApp",
            fg_color="#25D366",
            width=80,
            command=self.enviar_whatsapp,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_acciones,
            text="Actualizar ->",
            fg_color="#eab308",
            text_color="black",
            width=100,
            command=self.actualizar_estado_registro,
        ).pack(side="right", padx=5)
        self.combo_nuevo_estado = ctk.CTkComboBox(
            frame_acciones,
            values=[
                "Pendiente",
                "En Revisión",
                "Presupuestado",
                "Terminado",
                "Entregado",
            ],
            width=150,
        )
        self.combo_nuevo_estado.pack(side="right")

    def construir_vista_finanzas(self):
        ctk.CTkLabel(
            self.frame_finanzas, text="BALANCE Y CAJA", font=("Arial", 24, "bold")
        ).pack(pady=30)
        frame_cards = ctk.CTkFrame(self.frame_finanzas, fg_color="transparent")
        frame_cards.pack(fill="x", padx=20)

        self.card_ingresos = self.crear_tarjeta(
            frame_cards, "Ingresos Totales", "green", 0
        )
        self.card_gastos = self.crear_tarjeta(frame_cards, "Costo Repuestos", "red", 1)
        self.card_ganancia = self.crear_tarjeta(
            frame_cards, "GANANCIA NETA", "#10b981", 2
        )
        self.card_pendiente = self.crear_tarjeta(
            frame_cards, "Pendiente de Cobro", "orange", 3
        )

    def crear_tarjeta(self, parent, titulo, color, col):
        frame = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        frame.grid(row=0, column=col, padx=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(frame, text=titulo, text_color="white", font=("Arial", 14)).pack(
            pady=(15, 5)
        )
        lbl_valor = ctk.CTkLabel(
            frame, text="$0", text_color="white", font=("Arial", 24, "bold")
        )
        lbl_valor.pack(pady=(0, 15))
        return lbl_valor

    # --- LOGICA DEL NEGOCIO ---
    def guardar_datos(self):
        try:
            nombre = self.entry_nombre.get()
            equipo = self.entry_equipo.get()
            if not nombre:
                return messagebox.showerror(
                    "Faltan Datos", "El Nombre del cliente es obligatorio."
                )

            base_datos.guardar_trabajo(
                self.entry_fecha.get(),
                nombre,
                self.entry_tel.get(),
                equipo,
                self.entry_falla.get("1.0", "end-1c"),
                self.combo_estado.get(),
            )
            messagebox.showinfo("Éxito", "Guardado.")
            self.entry_nombre.delete(0, "end")
            self.entry_tel.delete(0, "end")
            self.entry_equipo.delete(0, "end")
            self.entry_falla.delete("1.0", "end")
        except:
            messagebox.showerror("Error", "Error al guardar.")

    def cargar_tabla_historial(self):
        self._llenar_tabla(base_datos.consultar_trabajos())

    def filtrar_historial(self):
        texto = self.entry_busqueda.get().lower()
        if not texto:
            return self.cargar_tabla_historial()

        todos = base_datos.consultar_trabajos()
        filtrados = [
            d
            for d in todos
            if texto in str(d[2]).lower()
            or texto in str(d[3]).lower()
            or texto in str(d[5]).lower()
        ]
        self._llenar_tabla(filtrados)

    def _llenar_tabla(self, datos):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for d in datos:
            precio_fmt = f"${d[7]:,.0f}" if d[7] else "$0"
            valores = (d[0], d[1], d[2], d[3], d[4], d[5], d[6], precio_fmt)
            self.tabla.insert("", "end", values=valores)

    def abrir_ventana_cobro(self):
        sel = self.tabla.selection()
        if not sel:
            return messagebox.showwarning("Ojo", "Selecciona un trabajo primero.")
        id_trabajo = self.tabla.item(sel)["values"][0]
        VentanaCobro(self, id_trabajo, self.cargar_tabla_historial)

    def imprimir_pdf(self):
        sel = self.tabla.selection()
        if not sel:
            return messagebox.showwarning("Ojo", "Selecciona un trabajo.")
        valores = self.tabla.item(sel)["values"]
        # Buscar el teléfono real en la base de datos (mejora para futuro)
        # Por ahora usamos el nombre para el archivo
        try:
            generador_pdf.generar_recibo(
                valores[0],
                valores[1],
                valores[2],
                "Registrado",
                valores[3],
                valores[4],
                valores[5],
                valores[7],
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error PDF: {e}")

    def enviar_whatsapp(self):
        """Abre WhatsApp Web con un mensaje pre-cargado."""
        sel = self.tabla.selection()
        if not sel:
            return messagebox.showwarning("Ojo", "Selecciona un cliente.")

        # Obtenemos los datos de la fila seleccionada
        valores = self.tabla.item(sel)["values"]
        nombre = valores[2]
        equipo = valores[3]
        estado = valores[5]

        # IMPORTANTE: Aquí deberíamos tener el teléfono real.
        # Como en la tabla no mostramos la columna teléfono, tenemos que buscarlo.
        # Por ahora, el programa te pedirá el número si no lo encuentra fácil.

        # Truco: Mensaje automático
        mensaje = f"Hola {nombre}, te escribo de Mati-Fix. Te aviso que tu equipo ({equipo}) está: {estado}."

        # Abrir WhatsApp Web (Esto abrirá tu navegador)
        webbrowser.open(f"https://web.whatsapp.com/send?text={mensaje}")

        # Nota: Para que mande al número directo, necesitamos guardar el teléfono en la tabla oculta.
        # Por ahora te abre la lista de contactos para que elijas a quién mandar.

    def actualizar_tablero_finanzas(self):
        ingreso, gastos, ganancia, pendiente = base_datos.obtener_balance_total()
        self.card_ingresos.configure(text=f"${ingreso:,.0f}")
        self.card_gastos.configure(text=f"${gastos:,.0f}")
        self.card_ganancia.configure(text=f"${ganancia:,.0f}")
        self.card_pendiente.configure(text=f"${pendiente:,.0f}")

    def eliminar_registro(self):
        sel = self.tabla.selection()
        if sel and messagebox.askyesno("Confirmar", "¿Borrar?"):
            base_datos.eliminar_trabajo(self.tabla.item(sel)["values"][0])
            self.cargar_tabla_historial()

    def actualizar_estado_registro(self):
        sel = self.tabla.selection()
        if sel:
            base_datos.actualizar_estado(
                self.tabla.item(sel)["values"][0], self.combo_nuevo_estado.get()
            )
            self.cargar_tabla_historial()

    def estilar_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=30,
        )
        style.map("Treeview", background=[("selected", "#1f538d")])
        style.configure("Treeview.Heading", background="#1f538d", foreground="white")


if __name__ == "__main__":
    app = AppTaller()
    app.mainloop()
