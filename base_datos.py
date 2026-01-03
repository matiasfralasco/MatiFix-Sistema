import sqlite3

DB_NAME = "taller_pc.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trabajos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_ingreso TEXT,
            cliente_nombre TEXT,
            cliente_tel TEXT,
            equipo TEXT,
            falla_declarada TEXT,
            estado TEXT DEFAULT 'Pendiente',
            costo_repuestos REAL DEFAULT 0,
            precio_final REAL DEFAULT 0,
            pagado TEXT DEFAULT 'NO'
        )
    """
    )

    # Intentamos agregar la columna 'pagado' si es una base de datos vieja que no la tenía
    try:
        cursor.execute("ALTER TABLE trabajos ADD COLUMN pagado TEXT DEFAULT 'NO'")
    except:
        pass  # Si ya existe, no pasa nada

    conexion.commit()
    conexion.close()


def guardar_trabajo(fecha, nombre, tel, equipo, falla, estado):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO trabajos (fecha_ingreso, cliente_nombre, cliente_tel, equipo, falla_declarada, estado, pagado, costo_repuestos, precio_final)
        VALUES (?, ?, ?, ?, ?, ?, 'NO', 0, 0)
    """,
        (fecha, nombre, tel, equipo, falla, estado),
    )
    conexion.commit()
    conexion.close()


def consultar_trabajos():
    conexion = conectar()
    cursor = conexion.cursor()
    # Traemos todo, incluyendo el dinero
    cursor.execute(
        "SELECT id, fecha_ingreso, cliente_nombre, equipo, falla_declarada, estado, pagado, precio_final FROM trabajos ORDER BY id DESC"
    )
    datos = cursor.fetchall()
    conexion.close()
    return datos


def eliminar_trabajo(id_trabajo):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM trabajos WHERE id = ?", (id_trabajo,))
    conexion.commit()
    conexion.close()


def actualizar_estado(id_trabajo, nuevo_estado):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE trabajos SET estado = ? WHERE id = ?", (nuevo_estado, id_trabajo)
    )
    conexion.commit()
    conexion.close()


# --- NUEVAS FUNCIONES DE DINERO ---


def actualizar_dinero(id_trabajo, costo, precio, pagado):
    """Guarda los datos financieros de un trabajo específico."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        UPDATE trabajos 
        SET costo_repuestos = ?, precio_final = ?, pagado = ? 
        WHERE id = ?
    """,
        (costo, precio, pagado, id_trabajo),
    )
    conexion.commit()
    conexion.close()


def obtener_balance_total():
    """Calcula los totales para la pestaña de Finanzas."""
    conexion = conectar()
    cursor = conexion.cursor()

    # Sumar todo lo que está marcado como PAGADO = SI
    cursor.execute(
        "SELECT SUM(precio_final), SUM(costo_repuestos) FROM trabajos WHERE pagado = 'SI'"
    )
    resultado_pagado = cursor.fetchone()  # Devuelve (Total Ingreso, Total Costo)

    ingreso_bruto = resultado_pagado[0] if resultado_pagado[0] else 0
    gastos = resultado_pagado[1] if resultado_pagado[1] else 0
    ganancia_neta = ingreso_bruto - gastos

    # Sumar lo que falta cobrar (PAGADO = NO pero con precio puesto)
    cursor.execute("SELECT SUM(precio_final) FROM trabajos WHERE pagado = 'NO'")
    resultado_pendiente = cursor.fetchone()
    pendiente = resultado_pendiente[0] if resultado_pendiente[0] else 0

    conexion.close()
    return ingreso_bruto, gastos, ganancia_neta, pendiente


if __name__ == "__main__":
    crear_tablas()
