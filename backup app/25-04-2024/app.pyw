from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, timedelta, date
from flask import session
from flask import jsonify
from werkzeug.security import generate_password_hash,check_password_hash
import pandas as pd
from contextlib import closing
from flask_sqlalchemy import SQLAlchemy
from flask import send_file
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'Admin12345*+'


#--------------------------INICIA SESSION LOGIN----------------------------

def connect_db():
    conn = sqlite3.connect('database.db')
    return conn

# def create_users_table():
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     cursor.execute('''CREATE TABLE IF NOT EXISTS users (
#                         id INTEGER PRIMARY KEY AUTOINCREMENT,
#                         username TEXT UNIQUE NOT NULL,
#                         password TEXT NOT NULL,
#                         role TEXT NOT NULL,
#                         first_login INTEGER DEFAULT 1
#                     )''')  # La columna first_login se inicializa en 1 por defecto, indicando que es la primera vez que el usuario inicia sesión
#     conn.commit()
#     conn.close()

# def insert_initial_data():
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     # Insertar usuarios de ejemplo con diferentes roles
#     users = [
#         ('medico1', 'password1', 'medico', 1),
#         ('medico2', 'password2', 'medico', 1),
#         ('aprendiz1', 'password3', 'aprendiz', 1),
#         ('admin', 'admin123', 'administrativo', 1)
#     ]
#     cursor.executemany('INSERT INTO users (username, password, role, first_login) VALUES (?, ?, ?, ?)', users)
#     conn.commit()
#     conn.close()



@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role, redirect_route, first_login = authenticate(username, password)
        if role:
            session['username'] = username
            session['role'] = role
            if first_login:
                flash('Es tu primera vez iniciando sesión. Por favor, cambia tu contraseña.')
                return redirect(url_for('change_password'))
            else:
                return redirect(url_for(redirect_route))
        else:
            error = 'Credenciales inválidas. Inténtalo de nuevo.'
            return render_template('login.html', error=error)
    return render_template('login.html')

# Función para autenticar al usuario
def authenticate(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role, first_login FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        role = user[0]  # Obtiene el rol del usuario
        first_login = user[1]  # Obtiene el estado de primer inicio de sesión
       
        if role == 'administrativo':
            return role, 'admin', first_login
        elif role == 'aprendiz':
            return role, 'aprendices', first_login
    else:
        return None, None, None

# Ruta para cambiar la contraseña
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' in session:
        if request.method == 'POST':
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            if new_password == confirm_password:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password=?, first_login=0 WHERE username=?", (new_password, session['username']))
                conn.commit()
                conn.close()
                flash('Contraseña cambiada exitosamente.')
                return redirect(url_for('login'))
            else:
                error = 'Las contraseñas no coinciden. Inténtalo de nuevo.'
                return render_template('change_password.html', error=error)
        return render_template('change_password.html')
    return redirect(url_for('login'))

# Ruta para el panel de control de los médicos
@app.route('/index')
def index():
    # Eliminamos la verificación de la sesión
    # Ahora cualquier usuario puede acceder a esta ruta
    return render_template('index.html')

# Ruta para el panel de control de los administrativos
@app.route('/admin')
def admin():
    if 'username' in session and session['role'] == 'administrativo':
        return render_template('admin.html', username=session['username'])
    return redirect(url_for('login'))

# Ruta para el panel de control de los aprendices
@app.route('/aprendices')
def aprendices():
    if 'username' in session and session['role'] == 'aprendiz':
        return render_template('aprendices.html', username=session['username'])
    return redirect(url_for('login'))

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

#---------------------FINALIZA SESSION LOGIN-------------------------------


@app.route('/')
def inicio():
    return render_template('index.html')

# --------------- INICIA REGISTRO DE PACIENTES---------------------

# def create_database():
#     conn = sqlite3.connect('usuarios.db')
#     c = conn.cursor()

#     # Crear tabla de formulario
#     c.execute('''CREATE TABLE IF NOT EXISTS pacientes
#                  (tipo_de_documento text, numero_de_documento text, fecha_de_atencion date, medico_quien_atiende text, fecha_envio text)''')
    
#     # Crear tabla para almacenar el conteo de formularios enviados
#     c.execute('''CREATE TABLE IF NOT EXISTS paciente
#                  (count integer)''')

#     # Inicializar el conteo de formularios enviados
#     c.execute('''INSERT INTO paciente (count) VALUES (0)''')

#     conn.commit()
#     conn.close()

# create_database()

# @app.route('/registro')
# def registro():
#     return render_template('registro.html')



# @app.route('/formulario1', methods=['POST'])
# def procesar_formulario1():
#     tipo_de_documento = request.form.get('tipo_de_documento')
#     numero_de_documento = request.form.get('numero_de_documento')
#     fecha_de_atencion = request.form.get('fecha_de_atencion')
#     medico_quien_atiende = request.form.get('medico_quien_atiende')
#     fecha_envio = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Obtener la fecha y hora actuales
#     conn = sqlite3.connect('usuarios.db')
#     c = conn.cursor()
#     c.execute("INSERT INTO pacientes (tipo_de_documento, numero_de_documento, fecha_de_atencion, medico_quien_atiende, fecha_envio) VALUES (?, ?, ?,?,?)", (tipo_de_documento, numero_de_documento, fecha_de_atencion, medico_quien_atiende, fecha_envio,))
#     conn.commit()
#     conn.close()

#     # Almacenar los valores de los campos del formulario en variables de sesión
    
#     session['fecha_de_atencion'] = fecha_de_atencion
#     session['medico_quien_atiende'] = medico_quien_atiende

#     return redirect(url_for('registro'))


@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/formulario1', methods=['POST'])
def procesar_formulario1():
    tipo_de_documento = request.form.get('tipo_de_documento')
    numero_de_documento = request.form.get('numero_de_documento')
    fecha_de_atencion = request.form.get('fecha_de_atencion')
    medico_quien_atiende = request.form.get('medico_quien_atiende')
    fecha_envio = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Obtener la fecha y hora actuales
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("INSERT INTO pacientes (tipo_de_documento, numero_de_documento, fecha_de_atencion, medico_quien_atiende, fecha_envio) VALUES (?, ?, ?, ?, ?)", (tipo_de_documento, numero_de_documento, fecha_de_atencion, medico_quien_atiende, fecha_envio,))
    conn.commit()
    conn.close()

    # Almacenar los valores de los campos del formulario en variables de sesión
    session['medico_quien_atiende'] = medico_quien_atiende
    session['fecha_de_atencion'] = fecha_de_atencion

    return redirect(url_for('registro'))

@app.route('/obtener_datos', methods=['GET'])
def obtener_datos():
    medico_quien_atiende = request.args.get('medico_quien_atiende')
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("SELECT tipo_de_documento, numero_de_documento, fecha_de_atencion,id FROM pacientes WHERE medico_quien_atiende = ?", (medico_quien_atiende,))
    data = c.fetchall()
    conn.close()
    return jsonify(data=data)

@app.route('/obtener_contadores/<medico_quien_atiende>')
def obtener_contadores(medico_quien_atiende):
    # Fecha actual
    fecha_envio = date.today()

    # Conexión a la base de datos
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Contador de datos ingresados hoy
    cursor.execute('SELECT COUNT(*) FROM pacientes WHERE DATE(fecha_envio) = ? AND medico_quien_atiende = ?', (fecha_envio, medico_quien_atiende))
    datos_hoy = cursor.fetchone()[0]

    # Contador de datos ingresados este mes
    inicio_mes = date(fecha_envio.year, fecha_envio.month, 1)
    cursor.execute('SELECT COUNT(*) FROM pacientes WHERE fecha_envio >= ? AND medico_quien_atiende = ?', (inicio_mes, medico_quien_atiende))
    datos_mes = cursor.fetchone()[0]

    conn.close()

    # Devuelve los contadores en formato JSON
    return jsonify({'datosHoy': datos_hoy, 'datosMes': datos_mes})



# ---------------------FINALIZA REGISTRO DE PACIENTES-----------------------------

# ------------------INICIA FORMULARIO REGISTRO DE ACTIVOS------------------------------
 
# crear una base de datos
def create_database():
    conn = sqlite3.connect('registro.db') 
    c = conn.cursor()

   
    c.execute('''CREATE TABLE IF NOT EXISTS registro
                 (nombres_completos text, cedula text, cargo text, numero_puesto text, extension text, ml_pc text, ml_pantalla text, mause text, guaya text, cargador text, diadema text, otros text, silla text, cubiculo text, descansapies text, observaciones text)''')

    conn.commit()
    conn.close()

create_database()


@app.route('/form')
def form():
    success_message = session.get('success_message', None)
    return render_template('form.html', success_message=success_message)
   

@app.route('/formulario2', methods=['POST'])
def procesar_formulario2():
    nombres_completos = request.form.get('nombres_completos')
    cedula = request.form.get('cedula')
    cargo = request.form.get('cargo')
    estado = request.form.get('estado')
    numero_puesto = request.form.get('numero_puesto')
    extension = request.form.get('extension')
    ml_pc = request.form.get('ml_pc')
    ml_pantalla = request.form.get('ml_pantalla')
    mause = "Sí" if request.form.get('mause')  == 'on' else "No"
    guaya = "Sí" if request.form.get('guaya')  == 'on' else "No"
    cargador = "Sí" if request.form.get('cargador')  == 'on' else "No"
    diadema =  "Sí" if request.form.get('diadema')  == 'on' else "No"
    fecha_envio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    silla = "Sí" if request.form.get('silla')  == 'on' else "No"
    cubiculo = "Sí" if request.form.get('cubiculo')  == 'on' else "No"
    descansapies = "Sí" if request.form.get('descansapies')  == 'on' else "No"
    observaciones = request.form.get('observaciones')
    

    conn = sqlite3.connect('registro.db')
    c = conn.cursor()
    c.execute("INSERT INTO registro (nombres_completos, cedula, cargo,estado, numero_puesto, extension, ml_pc, ml_pantalla, mause, guaya, cargador, diadema, fecha_envio, silla, cubiculo, descansapies, observaciones) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (nombres_completos, cedula, cargo,estado, numero_puesto, extension, ml_pc, ml_pantalla, mause, guaya, cargador,diadema,fecha_envio,silla,cubiculo,descansapies,observaciones))
    conn.commit()
    conn.close()
    
    session['success_message'] = "Formulario enviado correctamente!"

    # Redirect back to the form
    return redirect(url_for('inicio'))

    # return 'formulario registrado con éxito!'

# -------------------FINALIZA FORMULARIO DE REGISTRO DE ACTIVOS------------------------------------

# ---------------------INICIA FORMULARIO DE SOPORTE-----------------------------------

def create_database():
    conn = sqlite3.connect('soporte.db')
    c = conn.cursor()

    # Crear tabla de formulario
    # c.execute('''CREATE TABLE IF NOT EXISTS solicitar_soporte
    #              (nombre_medico text, tipo-de_inconveniente text, numero_cubiculo text, observaciones text, fecha_envio text)''')
    
    # Crear tabla para almacenar el conteo de formularios enviados
    c.execute('''CREATE TABLE IF NOT EXISTS conteo
                 (count integer)''')

    # Inicializar el conteo de formularios enviados
    c.execute('''INSERT INTO conteo (count) VALUES (0)''')

    conn.commit()
    conn.close()

create_database()


@app.route('/formulario3', methods=['POST'])
def procesar_formulario3():
    nombre_medico = request.form.get('nombre_medico')
    tipo_de_inconveniente = request.form.get('tipo_de_inconveniente')
    numero_de_cubiculo = request.form.get('numero_de_cubiculo')
    observaciones = request.form.get('observaciones')
    fecha_envio = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Obtener la fecha y hora actuales
    estado_de_solicitud = 'en gestion'
    conn = sqlite3.connect('soporte.db')
    c = conn.cursor()
    c.execute("INSERT INTO solicitar_soporte (nombre_medico, tipo_de_inconveniente, numero_cubiculo, observaciones, fecha_envio,estado_de_solicitud) VALUES (?, ?, ?,?,?,?)", (nombre_medico, tipo_de_inconveniente, numero_de_cubiculo, observaciones, fecha_envio, estado_de_solicitud))
    conn.commit()
    conn.close()

    return redirect(url_for('inicio'))

# @app.route('/estado_solicitud')
# def estado_solicitud():
#     today = datetime.now().strftime('%Y-%m-%d')  # Obtener la fecha actual

#     conn = sqlite3.connect('soporte.db')
#     c = conn.cursor()
#     c.execute("SELECT * FROM solicitar_soporte WHERE fecha_envio LIKE ?", (today + '%',))
#     rows = c.fetchall()
#     conn.close()
    
#     return render_template('estado_solicitud.html', rows=rows)


# ------------------------FINALIZA FORMULARIO DE SOPORTE--------------------------------------------

#
# -------------------------INICIA FORMULARIO DE NOVEDADES---------------------------------------------
 
@app.route('/registrar_novedad')
def registrar_novedad():
    return render_template('registrar_novedad.html')
 
 
# def create_database():
#     conn = sqlite3.connect('novedades.db') # Crea la base de datos si no existe
#     c = conn.cursor()

#     # Crea la tabla si no existe
#     c.execute('''CREATE TABLE IF NOT EXISTS novedades
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                  nombre TEXT NOT NULL,
#                  tipo_novedad TEXT NOT NULL,
#                  lider_a_cargo TEXT NOT NULL,
#                  fecha_inicio TEXT NOT NULL,
#                  fecha_fin TEXT NOT NULL,
#                  dias_novedad INTEGER NOT NULL,
#                  observaciones TEXT,
#                  archivo_pdf BLOB)''')

#     conn.commit()
#     conn.close()
# create_database()

@app.route('/formulario4', methods=['POST'])
def procesar_formulario4():
    # Extraer datos del formulario
    nombre = request.form['nombre']
    tipo_novedad = request.form['tipo_novedad']
    lider_a_cargo = request.form['lider_a_cargo']
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']
    dias_novedad = request.form['dias_novedad']
    observaciones = request.form['observaciones']
    archivo_pdf = request.files['archivo_pdf']
    fecha_envio = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    # Leer el archivo PDF y convertirlo en bytes
    pdf_data = archivo_pdf.read()

    # Conectar a la base de datos y guardar los datos
    conn = sqlite3.connect('novedades.db')
    c = conn.cursor()
    c.execute("INSERT INTO novedades (nombre, tipo_novedad, lider_a_cargo, fecha_inicio, fecha_fin, dias_novedad, observaciones, archivo_pdf,fecha_envio) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)",
              (nombre, tipo_novedad, lider_a_cargo, fecha_inicio, fecha_fin, dias_novedad, observaciones, sqlite3.Binary(pdf_data),fecha_envio))
    conn.commit()
    conn.close()
    
    flash('El formulario se guardó correctamente.', 'success')

    return redirect(url_for('admin'))




#-------------------------FINALIZA FORMULARIO NOVEDADES DE NOMINA------------------------------------------

#----------------------INICIA SESSION DE TALENTO HUMANO-------------------------
@app.route('/talento_humano')
def talento_humano():
     return render_template('talento_humano.html')
 
talento_humano = 'talento_humano.db'

# Función para establecer una conexión a la base de datos
def connect_db4():
    return sqlite3.connect(talento_humano)

@app.route('/personal')
def personal():
    with closing(connect_db4()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM personal")
        asignacionespersonal = cursor.fetchall()
        cursor.execute("SELECT NOMBRE_COMPLETO, cargo FROM personal")
        personal_info = cursor.fetchall()
    return render_template('personal.html', asignacionespersonal=asignacionespersonal, personal_info=personal_info)

# Ruta para actualizar un registro en la base de datos
@app.route('/update4', methods=['POST'])
def update4():
    NUMERO_CARPETA = request.form['NUMERO_CARPETA']
    NUMERO_CEDULA = request.form['NUMERO_CEDULA']
    CORREO_PERSONAL = request.form['CORREO_PERSONAL']
    CORREO_CORPORATIVO = request.form['CORREO_CORPORATIVO']
    NUMERO_CELULAR = request.form['NUMERO_CELULAR']
    NOMBRE_COMPLETO = request.form['NOMBRE_COMPLETO']
    CARGO = request.form['CARGO']
    PROCESO = request.form['PROCESO']
    FECHA_INGRESO = request.form['FECHA_INGRESO']
    ESTADO = request.form['ESTADO']
    FECHA_FIN = request.form['FECHA_FIN']

    with closing(connect_db4()) as db:
        cursor = db.cursor()
        cursor.execute("UPDATE personal SET NUMERO_CEDULA=?, CORREO_PERSONAL=?,CORREO_CORPORATIVO=?, NUMERO_CELULAR=?, NOMBRE_COMPLETO=?, CARGO=?, PROCESO=?,FECHA_INGRESO=?, ESTADO=?,FECHA_FIN=? WHERE NUMERO_CARPETA=?", 
                        (NUMERO_CEDULA, CORREO_PERSONAL, CORREO_CORPORATIVO, NUMERO_CELULAR, NOMBRE_COMPLETO, CARGO,PROCESO,FECHA_INGRESO,ESTADO,FECHA_FIN, NUMERO_CARPETA))
        db.commit()

    return redirect(url_for('personal'))

#-----------------------FINALIZA SESSION DE TALENTO HUMANO-------------------------
#------------------------INICIA SESSION DE NOMINA--------------------------

DATABASE = 'agenda.db'

def create_db(database_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS actividades
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, actividad TEXT, completada INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/nomina')
def nomina():
    create_db(DATABASE)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM actividades WHERE completada=0')
    actividades = c.fetchall()
    conn.close()
    return render_template('nomina.html', actividades=actividades)

@app.route('/show_data_of_the_day')
def show_data_of_the_day():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("SELECT * FROM pacientes")
    rows = c.fetchall()
    conn.close()
    return render_template('data_of_the_day.html', rows=rows)

@app.route('/plantilla_nomina')
def plantilla_nomina():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('novedades.db')
    c = conn.cursor()
    c.execute("SELECT * FROM novedades")
    novedades = c.fetchall()
    conn.close()
    return render_template('plantilla_nomina.html', novedades=novedades)

@app.route('/agregar', methods=['POST'])
def agregar():
    actividad = request.form['actividad']
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO actividades (actividad, completada) VALUES (?, 0)', (actividad,))
    conn.commit()
    conn.close()
    return redirect('/nomina')

@app.route('/completar/<int:id>')
def completar(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE actividades SET completada=1 WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/nomina')


#-------------------------FINALIZA SESSION DE NOMINA----------------------

#-------------------------INICIA SESSION DE OPERACIONES------------------------------------

DATA_BASE = 'operaciones.db'
@app.route('/operaciones')
def operaciones():
    create_db(DATA_BASE)
    conn = sqlite3.connect(DATA_BASE)
    c = conn.cursor()
    c.execute('SELECT * FROM actividades WHERE completada=0')
    actividades = c.fetchall()
    conn.close()
    return render_template('operaciones.html', actividades=actividades)

@app.route('/agregar1', methods=['POST'])
def agregar1():
    actividad = request.form['actividad']
    conn = sqlite3.connect(DATA_BASE)
    c = conn.cursor()
    c.execute('INSERT INTO actividades (actividad, completada) VALUES (?, 0)', (actividad,))
    conn.commit()
    conn.close()
    return redirect('/operaciones')

@app.route('/completar1/<int:id>')
def completar1(id):
    conn = sqlite3.connect(DATA_BASE)
    c = conn.cursor()
    c.execute('UPDATE actividades SET completada=1 WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/operaciones')

@app.route('/estado_solicitud')
def estado_solicitud1():
    conn = sqlite3.connect('soporte.db')
    c = conn.cursor()
    c.execute("SELECT * FROM solicitar_soporte")
    rows = c.fetchall()
    conn.close()
    return render_template('estado_solicitud.html', rows=rows)


#-------------------------------------inventario-----------------------------------
registro = 'registro.db'

# Función para establecer una conexión a la base de datos
def connect_db5():
    return sqlite3.connect(registro)

@app.route('/inventario')
def inventario():
    with closing(connect_db5()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM registro")
        asignacionesinventario = cursor.fetchall()
        cursor.execute("SELECT numero_puesto FROM registro")
        inventario_info = cursor.fetchall()
    return render_template('inventario.html', asignacionesinventario=asignacionesinventario, inventario_info=inventario_info)

# Ruta para actualizar un registro en la base de datos+
@app.route('/update5', methods=['POST'])
def update5():
    nombres_completos = request.form.get('nombres_completos')
    cedula = request.form.get('cedula')
    cargo = request.form.get('cargo')
    estado = request.form.get('estado')
    numero_puesto = request.form.get('numero_puesto')
    extension = request.form.get('extension')
    ml_pc = request.form.get('ml_pc')
    ml_pantalla = request.form.get('ml_pantalla')
    mause =  request.form.get('mause') 
    guaya =  request.form.get('guaya')
    cargador = request.form.get('cargador') 
    diadema = request.form.get('diadema') 
    fecha_envio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    silla =  request.form.get('silla') 
    cubiculo =  request.form.get('cubiculo') 
    descansapies = request.form.get('descansapies') 
    observaciones = request.form.get('observaciones')

    with closing(connect_db5()) as db:
        cursor = db.cursor()
        cursor.execute("UPDATE registro SET nombres_completos=?, cedula=?, cargo=?,estado=?, extension=?, ml_pc=?, ml_pantalla=?, mause=?, guaya=?, cargador=?, diadema=?, fecha_envio=?, silla=?, cubiculo=?, descansapies=?, observaciones=? WHERE numero_puesto=?", 
               (nombres_completos, cedula, cargo,estado, extension, ml_pc, ml_pantalla, mause, guaya, cargador, diadema, fecha_envio, silla, cubiculo, descansapies, observaciones, numero_puesto))

        db.commit()

    return redirect(url_for('inventario'))

#-------------------------------LINEAS-----------------------------------

BASE = 'lineas.db'

# Función para establecer una conexión a la base de datos
def connect_db2():
    return sqlite3.connect(BASE)

# Ruta para mostrar los registros de la base de datos
@app.route('/lineas')
def lineas():
    with closing(connect_db2()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM asignaciones")
        asignaciones = cursor.fetchall()
        cursor.execute("SELECT nombre, cargo FROM personal")
        personal_info = cursor.fetchall()
    return render_template('lineas.html', asignaciones=asignaciones, personal_info=personal_info)

# Ruta para actualizar un registro en la base de datos
@app.route('/update', methods=['POST'])
def update():
    # Obtener los datos del formulario
    data = {
        'linea': request.form.get('linea'),
        'imei': request.form.get('imei'),
        'nombre': request.form.get('nombre'),
        'estado': request.form.get('estado'),
        'cedula': request.form.get('cedula'),
        'detalle_entrega': request.form.get('detalle_entrega'),
        'fecha_entrega': request.form.get('fecha_entrega'),
        'observacion': request.form.get('observacion'),
        'id': request.form.get('id')
    }

    # Filtrar los campos que no son None
    data_to_update = {k: v for k, v in data.items() if v is not None}

    # Construir la consulta SQL dinámicamente
    set_clause = ', '.join(f"{key}=?" for key in data_to_update.keys())
    where_clause = f"WHERE id=?"
    query = f"UPDATE asignaciones SET {set_clause} {where_clause}"

    # Preparar los parámetros para la consulta
    params = list(data_to_update.values()) + [data['id']]

    with closing(connect_db2()) as db:
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()

    return redirect(url_for('lineas'))


# Función para insertar un nuevo registro en la base de datos
@app.route('/insert2', methods=['POST'])
def insert2():
    # Obtener los datos del formulario
    data = {
        'linea': request.form.get('linea'),
        'imei': request.form.get('imei'),
        'nombre': request.form.get('nombre'),
        'estado': request.form.get('estado'),
        'cedula': request.form.get('cedula'),
        'detalle_entrega': request.form.get('detalle_entrega'),
        'fecha_entrega': request.form.get('fecha_entrega'),
        'observacion': request.form.get('observacion')
    }

    # Construir la consulta SQL para insertar
    columns = ', '.join(data.keys())
    placeholders = ', '.join('?' for _ in data)
    query = f"INSERT INTO asignaciones ({columns}) VALUES ({placeholders})"

    # Preparar los parámetros para la consulta
    params = list(data.values())

    with closing(connect_db2()) as db:
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()

    return redirect(url_for('lineas'))

@app.route('/plano')
def plano():
    return render_template('plano.html')
#--------------------------FINALIZA SESSION OPERACIONES----------------------------------


#---------------------INICIA SESSION PRACTICANTES-----------------------------

@app.route('/gestionar_actividades', methods=['GET', 'POST'])
def gestionar_actividades():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        fecha_asignacion = request.form['fecha_asignacion']
        fecha_vencimiento = request.form['fecha_vencimiento']
        conn = sqlite3.connect('actividades_aprendices.db')
        c = conn.cursor()
        c.execute("INSERT INTO actividades_aprendices (nombre, descripcion, fecha_asignacion, fecha_vencimiento) VALUES (?, ?, ?, ?)",
                 (nombre, descripcion, fecha_asignacion, fecha_vencimiento))
        conn.commit()
        conn.close()
        flash('Actividad creada exitosamente.')
        return redirect(url_for('gestionar_actividades'))
    else:
        conn = sqlite3.connect('actividades_aprendices.db')
        c = conn.cursor()
        c.execute("SELECT * FROM actividades_aprendices")
        actividades = c.fetchall()
        conn.close()
        return render_template('gestionar_actividades.html', actividades=actividades)

@app.route('/asignar_actividad/<int:actividad_id>', methods=['POST'])
def asignar_actividad(actividad_id):
    usuario_id = request.form['usuario_id']
    observaciones = request.form['observaciones']
    conn = sqlite3.connect('actividades_aprendices.db')
    c = conn.cursor()
    c.execute("INSERT INTO asignaciones_aprendices (usuario_id, actividad_id, observaciones) VALUES (?, ?, ?)",
              (usuario_id, actividad_id, observaciones))
    conn.commit()
    conn.close()
    flash('Actividad asignada exitosamente.')
    return redirect(url_for('gestionar_actividades'))

@app.route('/modificar_actividad/<int:asignacion_id>', methods=['POST'])
def modificar_actividad(asignacion_id):
    observaciones = request.form['observaciones']
    conn = sqlite3.connect('actividades_aprendices.db')
    c = conn.cursor()
    c.execute("UPDATE asignaciones_aprendices SET observaciones=? WHERE id=?", (observaciones, asignacion_id))
    conn.commit()
    conn.close()
    flash('Observaciones actualizadas exitosamente.')
    return redirect(url_for('aprendices'))



#-------------------------FINALIZA SESSION PRACTICANTES--------------------------
#--------------------------INICIA SESSION DE CONTABILIDAD------------------------
 
@app.route('/registrar_incapacidad')
def registrar_incapacidad():
    return render_template('registrar_incapacidad.html')
 
 
# def crear_database():
#     conn = sqlite3.connect('incapacidades.db') # Crea la base de datos si no existe
#     c = conn.cursor()

#     # Crea la tabla si no existe
#     c.execute('''CREATE TABLE IF NOT EXISTS incapacidad
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                  lider_a_cargo TEXT NOT NULL,
#                  nombre TEXT NOT NULL,
#                  cedula TEXT NOT NULL,
#                  cargo TEXT NOT NULL,
#                  eps TEXT NOT NULL,
#                  eg_transito TEXT NOT NULL,
#                  nro_incapacidad TEXT NOT NULL,
#                  prorroga TEXT NOT NULL,
#                  fecha_inicio TEXT NOT NULL,
#                  fecha_final TEXT NOT NULL,
#                  dias_novedad INTEGER NOT NULL,
#                  diagnostico TEXT NOT NULL,
#                  profesional TEXT NOT NULL,
#                  observaciones TEXT,
#                  archivo_pdf BLOB)
#                  fecha_envio TEXT NOT NULL''')

#     conn.commit()
#     conn.close()

# crear_database()
@app.route('/formulario5', methods=['POST'])
def procesar_formulario5():
    # Extraer datos del formulario
    lider_a_cargo = request.form['lider_a_cargo']
    nombre = request.form['nombre']
    cedula = request.form['cedula']
    cargo = request.form['cargo']
    eps = request.form['eps']
    eg_transito = request.form['eg_transito']
    nro_incapacidad = request.form['nro_incapacidad']
    prorroga = request.form['prorroga']
    fecha_inicio = request.form['fecha_inicio']
    fecha_final = request.form['fecha_final']
    diagnostico = request.form['diagnostico']
    profesional = request.form['profesional']
    observaciones = request.form['observaciones']
    archivo_pdf = request.files['archivo_pdf']
    fecha_envio = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    # Calcular la diferencia de días entre las fechas de inicio y final
    fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d')-  timedelta(days=1)
    fecha_final_obj = datetime.strptime(fecha_final, '%Y-%m-%d')
    dias_novedad = (fecha_final_obj - fecha_inicio_obj).days

    # Leer el archivo PDF y convertirlo en bytes
    pdf_data = archivo_pdf.read()

    # Conectar a la base de datos y guardar los datos
    conn = sqlite3.connect('incapacidades.db')
    c = conn.cursor()
    c.execute("INSERT INTO incapacidad ( lider_a_cargo,nombre,cedula,cargo,eps,eg_transito,nro_incapacidad,prorroga, fecha_inicio, fecha_final, dias_novedad, dias_novedad, diagnostico, profesional, observaciones, archivo_pdf, fecha_envio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              ( lider_a_cargo, nombre, cedula, cargo, eps, eg_transito, nro_incapacidad, prorroga, fecha_inicio, fecha_final, dias_novedad, dias_novedad, diagnostico, profesional, observaciones, sqlite3.Binary(pdf_data), fecha_envio))
    conn.commit()
    conn.close()
    
    flash('El formulario se guardó correctamente.', 'success')

    return redirect(url_for('admin'))

@app.route('/plantilla_incapacidades')
def plantilla_incapacidades():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('incapacidades.db')
    c = conn.cursor()
    c.execute("SELECT * FROM incapacidad")
    novedades = c.fetchall()
    conn.close()
    return render_template('plantilla_incapacidades.html', novedades=novedades)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incapacidades.db'
db = SQLAlchemy(app)

def connect_db3():
    # Función para conectar a la base de datos
    return sqlite3.connect('incapacidades.db')

@app.route('/actualizar_incapacidad/<int:id>', methods=['POST'])
def actualizar_incapacidad(id):
    # Obtener el nuevo número de incapacidad del formulario
    nuevo_nro_incapacidad = request.form.get('nro_incapacidad')
    
    # Obtener la incapacidad de la base de datos por su ID
    with closing(connect_db3()) as db:
        cursor = db.cursor()
        cursor.execute("UPDATE incapacidad SET nro_incapacidad=? WHERE id=?", 
                       (nuevo_nro_incapacidad, id))
        db.commit()

    return redirect(url_for('plantilla_incapacidades'))

@app.route('/exportar_a_excel')
def exportar_a_excel():
    # Conectar a la base de datos y obtener los datos
    with sqlite3.connect('incapacidades.db') as conn:
        df = pd.read_sql_query("SELECT * FROM incapacidad", conn)

    # Crear un archivo Excel en memoria
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Incapacidades')
    writer._save()

    # Asegurarse de que el archivo Excel se cierre correctamente
    writer.close()

    # Crear un objeto de respuesta Flask que envía el archivo Excel
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='incapacidades.xlsx')

#--------------------------FINALIZA SESSION DE CONTABILIDAD----------------------
if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0', port=5000)
    
    