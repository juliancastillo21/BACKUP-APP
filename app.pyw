from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, timedelta, date
from flask import session
from flask import jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from contextlib import closing
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask import send_file
from io import BytesIO
import os
import csv
from werkzeug.utils import secure_filename
import io
# from flask_mail import Mail, Message
# import matplotlib.pyplot as plt



app = Flask(__name__)
app.secret_key = 'Admin12345*+'


#--------------------------INICIA SESSION LOGIN----------------------------

def connect_db():
    conn = sqlite3.connect('database.db')
    return conn

# The above code is a Python Flask application that implements a simple authentication system for different user roles (administrative, apprentice) with session management. Here is a breakdown of the main functionalities:

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

    return render_template('index.html')

@app.route('/manualmedicos')
def manualmedicos():
    return render_template('manualmedicos.html')

@app.route('/reglamento')
def reglamento():
    return render_template('reglamento.html')

@app.route('/Calculadora')
def Calculadora_IMC():
    return render_template('Calculadora_IMC.html')

@app.route('/Ayuda')
def Ayudapersonal():
    return render_template('Ayuda_personal.html')

@app.route('/pc')
def Entregapc():
    return render_template('Entrega_pc.html')


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

# The above code is a Python Flask application that serves as a backend for a web application related to patient registrations and data processing. Here is a breakdown of the main functionalities:

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
    c.execute("SELECT tipo_de_documento, numero_de_documento, fecha_de_atencion,id FROM pacientes WHERE medico_quien_atiende = ? ORDER BY fecha_de_atencion DESC", (medico_quien_atiende,))
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

@app.route('/exportar_a_excel3')
def exportar_a_excel3():
    # Conectar a la base de datos y obtener los datos
    with sqlite3.connect('usuarios.db') as conn:
        df = pd.read_sql_query("SELECT * FROM pacientes", conn)

    # Crear un archivo Excel en memoria
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='pacientes')
    writer._save()

    # Asegurarse de que el archivo Excel se cierre correctamente
    writer.close()

    # Crear un objeto de respuesta Flask que envía el archivo Excel
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='registro de ateciones.xlsx')

# ---------------------FINALIZA REGISTRO DE PACIENTES-----------------------------

# ------------------INICIA FORMULARIO REGISTRO DE ACTIVOS------------------------------
 
# The above code is a Python script that defines a Flask web application with routes for creating a database, rendering a form, processing form data, and exporting data to an Excel file. Here is a breakdown of the main functionalities:

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
    c.execute("INSERT INTO registro2 (nombres_completos, cedula, cargo,estado, numero_puesto, extension, ml_pc, ml_pantalla, mause, guaya, cargador, diadema, fecha_envio, silla, cubiculo, descansapies, observaciones) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (nombres_completos, cedula, cargo,estado, numero_puesto, extension, ml_pc, ml_pantalla, mause, guaya, cargador,diadema,fecha_envio,silla,cubiculo,descansapies,observaciones))
    conn.commit()
    conn.close()
    
    session['success_message'] = "Formulario enviado correctamente!"

    # Redirect back to the form
    return redirect(url_for('inicio'))

    # return 'formulario registrado con éxito!'

@app.route('/exportar_a_excel4')
def exportar_a_excel4():
    # Conectar a la base de datos y obtener los datos
    with sqlite3.connect('registro.db') as conn:
        df = pd.read_sql_query("SELECT * FROM registro", conn)

    # Crear un archivo Excel en memoria
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='registro')
    writer._save()
    writer.close()
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='registro inventario.xlsx')

# -------------------FINALIZA FORMULARIO DE REGISTRO DE ACTIVOS------------------------------------

# ---------------------INICIA FORMULARIO DE SOPORTE-----------------------------------

# The above code is a Python Flask application that defines two routes:

@app.route('/formulario3', methods=['POST'])
def procesar_formulario3():
    nombre_medico = request.form.get('nombre_medico')
    tipo_de_inconveniente = request.form.get('tipo_de_inconveniente')
    numero_de_cubiculo = request.form.get('numero_de_cubiculo')
    observaciones = request.form.get('observaciones')
    fecha_envio = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Obtener la fecha y hora actuales
    estado_de_solicitud = 'en gestion'

    # Insertar los datos en la base de datos
    conn = sqlite3.connect('soporte.db')
    c = conn.cursor()
    c.execute("INSERT INTO solicitar_soporte (nombre_medico, tipo_de_inconveniente, numero_cubiculo, observaciones, fecha_envio,estado_de_solicitud) VALUES (?, ?, ?,?,?,?)", (nombre_medico, tipo_de_inconveniente, numero_de_cubiculo, observaciones, fecha_envio, estado_de_solicitud))
    conn.commit()
    conn.close()

    return redirect(url_for('inicio'))  # Ajusta el nombre de la función de ruta según tu aplicación

@app.route('/actualizar_estado2/<fecha_envio>', methods=['POST'])
def actualizar_estado2(fecha_envio):
    # Obtener los datos del formulario
    estado_de_solicitud = request.form.get('estado_de_solicitud')
    observaciones2 = request.form.get('observaciones2')

    # Construir la consulta SQL para actualizar
    query = "UPDATE solicitar_soporte SET estado_de_solicitud=?, observaciones2=? WHERE fecha_envio=?"

    # Ejecutar la consulta SQL
    conn = sqlite3.connect('soporte.db')
    cursor = conn.cursor()
    cursor.execute(query, (estado_de_solicitud, observaciones2, fecha_envio))
    conn.commit()
    conn.close()

    return redirect(url_for('estado_solicitud1')) 



# ------------------------FINALIZA FORMULARIO DE SOPORTE--------------------------------------------

#
# -------------------------INICIA FORMULARIO DE NOVEDADES---------------------------------------------
 
# The above code is a Python Flask application that handles a form submission for registering a new entry in a database table called "novedades" which stores information about novelties or updates. Here is a breakdown of the key functionalities:

@app.route('/registrar_novedad')
def registrar_novedad():
    return render_template('registrar_novedad.html')

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

@app.route('/exportar_a_excel2')
def exportar_a_excel2():
    # Conectar a la base de datos y obtener los datos
    with sqlite3.connect('novedades.db') as conn:
        df = pd.read_sql_query("SELECT * FROM novedades", conn)

    # Crear un archivo Excel en memoria
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='novedades')
    writer._save()
    writer.close()
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='otras novedades.xlsx')

#-------------------------FINALIZA FORMULARIO NOVEDADES DE NOMINA------------------------------------------

#----------------------INICIA SESSION DE TALENTO HUMANO-------------------------

# The above code is a Python script using Flask framework to create a web application for managing human resources data. Here is a summary of what the code is doing:

# Función para establecer una conexión a la base de datos
def talento_humano_connection():
    return sqlite3.connect('talento_humano.db')

# Rutas relacionadas con la gestión del personal
@app.route('/personal')
def personal():
    with closing(talento_humano_connection()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM personal")
        asignacionespersonal = cursor.fetchall()
        cursor.execute("SELECT NOMBRE_COMPLETO, cargo FROM personal")
        personal_info = cursor.fetchall()
    return render_template('personal.html', asignacionespersonal=asignacionespersonal, personal_info=personal_info)

@app.route('/update4', methods=['POST'])
def update4():
    # Obtener los datos del formulario
    data = {
        'NUMERO_CARPETA': request.form['NUMERO_CARPETA'],
        'NUMERO_CEDULA': request.form['NUMERO_CEDULA'],
        'CORREO_PERSONAL': request.form['CORREO_PERSONAL'],
        'CORREO_CORPORATIVO': request.form['CORREO_CORPORATIVO'],
        'NUMERO_CELULAR': request.form['NUMERO_CELULAR'],
        'NOMBRE_COMPLETO': request.form['NOMBRE_COMPLETO'],
        'CARGO': request.form['CARGO'],
        'PROCESO': request.form['PROCESO'],
        'FECHA_INGRESO': request.form['FECHA_INGRESO'],
        'ESTADO': request.form['ESTADO'],
        'FECHA_FIN': request.form['FECHA_FIN']
    }

    # Construir la consulta SQL para actualizar
    query = ("UPDATE personal SET NUMERO_CARPETA=?, NUMERO_CEDULA=?, CORREO_PERSONAL=?, CORREO_CORPORATIVO=?, "
             "NUMERO_CELULAR=?, NOMBRE_COMPLETO=?, CARGO=?, PROCESO=?, FECHA_INGRESO=?, "
             "ESTADO=?, FECHA_FIN=? WHERE NUMERO_CARPETA=?")

    # Preparar los parámetros para la consulta
    params = [data[key] for key in data] + [data['NUMERO_CARPETA']]

    with closing(talento_humano_connection()) as db:
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()

    return redirect(url_for('personal'))

@app.route('/insert3', methods=['POST'])
def insert3():
    # Obtener los datos del formulario
    data = {
        'NUMERO_CARPETA': request.form.get('NUMERO_CARPETA'),
        'NUMERO_CEDULA': request.form.get('NUMERO_CEDULA'),
        'CORREO_PERSONAL': request.form.get('CORREO_PERSONAL'),
        'CORREO_CORPORATIVO': request.form.get('CORREO_CORPORATIVO'),
        'NUMERO_CELULAR': request.form.get('NUMERO_CELULAR'),
        'NOMBRE_COMPLETO': request.form.get('NOMBRE_COMPLETO'),
        'CARGO': request.form.get('CARGO'),
        'PROCESO': request.form.get('PROCESO'),
        'FECHA_INGRESO': request.form.get('FECHA_INGRESO'),
        'ESTADO': request.form.get('ESTADO'),
        'FECHA_FIN': request.form.get('FECHA_FIN')
    }
       
    # Construir la consulta SQL para insertar
    columns = ', '.join(data.keys())
    placeholders = ', '.join('?' for _ in data)
    query = f"INSERT INTO personal ({columns}) VALUES ({placeholders})"

    # Preparar los parámetros para la consulta
    params = list(data.values())

    with closing(talento_humano_connection()) as db:
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()

    return redirect(url_for('personal'))

# Rutas relacionadas con la gestión de talento humano
@app.route('/talento_humano')
def talento_humano_page():
    with closing(talento_humano_connection()) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM actividades3 WHERE completada=0')
        actividades3 = c.fetchall()
    return render_template('talento_humano.html', actividades3=actividades3)

@app.route('/agregar3', methods=['POST'])
def agregar_actividad():
    actividad = request.form['actividad']
    with closing(talento_humano_connection()) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO actividades3 (actividad, completada) VALUES (?, 0)', (actividad,))
        conn.commit()
    return redirect(url_for('talento_humano_page'))

@app.route('/completar3/<int:id>')
def completar_actividad(id):
    with closing(talento_humano_connection()) as conn:
        c = conn.cursor()
        c.execute('UPDATE actividades3 SET completada=1 WHERE id=?', (id,))
        conn.commit()
    return redirect(url_for('talento_humano_page'))


@app.route('/exportar_a_excel6')
def exportar_a_excel6():
    # Conectar a la base de datos y obtener los datos
    with sqlite3.connect('talento_humano.db') as conn:
        df = pd.read_sql_query("SELECT * FROM personal", conn)

    # Crear un archivo Excel en memoria
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='personal')
    writer._save()

    # Asegurarse de que el archivo Excel se cierre correctamente
    writer.close()

    # Crear un objeto de respuesta Flask que envía el archivo Excel
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='personal activo.xlsx')

#-----------------------FINALIZA SESSION DE TALENTO HUMANO-------------------------

#------------------------INICIA SESSION DE NOMINA----------------------------------

# The above code is a Python script that defines routes for a Flask web application. Here is a summary of what each function does:

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
    c.execute("SELECT * FROM pacientes ORDER BY fecha_envio DESC")
    rows = c.fetchall()
    conn.close()
    return render_template('data_of_the_day.html', rows=rows)

@app.route('/plantilla_nomina')
def plantilla_nomina():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('novedades.db')
    c = conn.cursor()
    c.execute("SELECT * FROM novedades ORDER BY fecha_envio DESC")
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

# The above code is a Python Flask application that defines several routes for handling operations related to tasks and support requests. Here is a summary of what each route does:

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
    c.execute("SELECT * FROM solicitar_soporte ORDER BY fecha_envio DESC")
    rows = c.fetchall()
    conn.close()
    return render_template('estado_solicitud.html', rows=rows)

@app.route('/soporte_medicos')
def soporte_medicos():
    conn = sqlite3.connect('soporte.db')
    c = conn.cursor()
    c.execute("SELECT * FROM solicitar_soporte ORDER BY fecha_envio DESC")
    rows = c.fetchall()
    conn.close()
    return render_template('soporte_medicos.html', rows=rows)

#--------------------------inventario milenio-------------------------------------------------
# Función para establecer la conexión con la base de datos
def inventario_milenio_connection():
    return sqlite3.connect('registro.db')

# Ruta para mostrar el inventario
@app.route('/inventario_milenio')
def inventario_milenio():
    with inventario_milenio_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM inventario_milenio ORDER BY id DESC")
        rowi = c.fetchall()
    return render_template('inventario_milenio.html', rowsi=rowi)

# Ruta para procesar el formulario de inserción
@app.route('/formulario_inv', methods=['POST'])

def procesar_formulario_inv():
    serial = request.form.get('serial')
    descripcionserial = request.form.get('descripcionserial')
    descripcionlineal = request.form.get('descripcionlineal')
    tarifa = request.form.get('tarifa')
    facturable = request.form.get('facturable')
    fecha_envio = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    estado = 'vigente'

    with inventario_milenio_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO inventario_milenio (serial, descripcionserial, descripcionlineal, tarifa, facturable, fecha_envio, estado) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                  (serial, descripcionserial, descripcionlineal, tarifa, facturable, fecha_envio, estado))
        conn.commit()

    return redirect(url_for('inventario_milenio'))
@app.route('/updateinv', methods=['POST'])

def updateinv():
    # Obtener los datos del formulario
    id_ = request.form.get('id')
    estado = request.form.get('estado')
    observaciones = request.form.get('observaciones')
    fecha_fin = datetime.now().strftime('%Y-%m-%d - %H:%M')

    # Construir la consulta SQL para actualizar
    query = "UPDATE inventario_milenio SET estado=?, observaciones=?, fecha_fin=? WHERE id=?"

    # Preparar los parámetros para la consulta
    params = (estado, observaciones, fecha_fin, id_)

    with closing(inventario_milenio_connection()) as db:
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()

    return redirect(url_for('inventario_milenio'))

@app.route('/exportar_a_excelinv')
def exportar_a_excelinv():
    # Conectar a la base de datos y obtener los datos
    with sqlite3.connect('registro.db') as conn:
        df = pd.read_sql_query("SELECT * FROM inventario_milenio", conn)

    # Crear un archivo Excel en memoria
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='inventario_milenio')
    writer._save()

    # Asegurarse de que el archivo Excel se cierre correctamente
    writer.close()

    # Crear un objeto de respuesta Flask que envía el archivo Excel
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='inventario_milenio.xlsx')
#-------------------------------------inventario-----------------------------------
# The above code is a Python script that defines a Flask web application with routes for displaying inventory information and updating records in a SQLite database. Here is a breakdown of the main components:
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
# # The above code is a Python script that defines a Flask web application with several routes for interacting with a SQLite database. Here is a summary of what the code is doing:

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

        data = {
        'cantidad_total': [100, 120, 150, 180],
        'cantidad_ocupadas': [50, 60, 70, 90],
        'cantidad_disponible': [50, 60, 80, 90],
        'fecha': ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01']
    }
    df = pd.DataFrame(data)
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Graficar
    # plt.figure(figsize=(10, 6))

    # plt.plot(df['fecha'], df['cantidad_total'], marker='o', label='Total de líneas')
    # plt.plot(df['fecha'], df['cantidad_ocupadas'], marker='o', label='Líneas ocupadas')
    # plt.plot(df['fecha'], df['cantidad_disponible'], marker='o', label='Líneas disponibles')

    # plt.title('Estado de líneas')
    # plt.xlabel('Fecha')
    # plt.ylabel('Cantidad de líneas')
    # plt.legend()
    # plt.grid(True)
    # plt.xticks(rotation=45)

    # plt.tight_layout()
    # plt.savefig('static/lineas_plot.png')  # Guardar la imagen del gráfico
    
    return render_template('lineas.html', asignaciones=asignaciones, personal_info=personal_info)
    return send_file('static/lineas_plot.png', mimetype='image/png')

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
        'audifonos': request.form.get('audifonos'),
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
        'observacion': request.form.get('observacion'),
        'audifonos': request.form.get('audifonos')
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
    # Aquí puedes pasar datos dinámicos a la plantilla
    return render_template('plano.html', title='Plano HolaDr', iframe_src='https://www.canva.com/design/DAGCranO9II/jqxD1juKahpc3WvTqbUAfw/view?embed', link_href='https://www.canva.com/design/DAGCranO9II/jqxD1juKahpc3WvTqbUAfw/view?utm_content=DAGCranO9II&utm_campaign=designshare&utm_medium=embeds&utm_source=link', link_text='A-01')



@app.route('/exportar_a_excel5')
def exportar_a_excel5():
    # Conectar a la base de datos y obtener los datos
    with sqlite3.connect('lineas.db') as conn:
        df = pd.read_sql_query("SELECT * FROM asignaciones", conn)

    # Crear un archivo Excel en memoria
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='asignaciones')
    writer._save()

    # Asegurarse de que el archivo Excel se cierre correctamente
    writer.close()

    # Crear un objeto de respuesta Flask que envía el archivo Excel
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='asignacion de lineas.xlsx')





#--------------------------FINALIZA SESSION OPERACIONES----------------------------------


#---------------------INICIA SESSION PRACTICANTES-----------------------------
# The above code is a Python Flask application that manages activities for apprentices. Here is a breakdown of the main functionalities:

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

@app.route('/cambiar_estado/<int:actividad_id>', methods=['POST'])
def cambiar_estado(actividad_id):
    nuevo_estado = request.form['estado']  # Corregido: la clave es 'estado'
    conn = sqlite3.connect('actividades_aprendices.db')
    c = conn.cursor()
    c.execute("UPDATE actividades_aprendices SET estado=? WHERE id=?", (nuevo_estado, actividad_id))
    conn.commit()
    conn.close()
    flash('Estado de la actividad actualizado exitosamente.')
    return redirect(url_for('gestionar_actividades'))


#-------------------------FINALIZA SESSION PRACTICANTES--------------------------
#--------------------------INICIA SESSION DE CONTABILIDAD------------------------
 
# The code provided is a Python Flask application that handles the registration and management of incapacity records. Here is a breakdown of the main functionalities:
@app.route('/registrar_incapacidad')
def registrar_incapacidad():
    return render_template('registrar_incapacidad.html')
 
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
    c.execute("SELECT * FROM incapacidad ORDER BY fecha_envio DESC")
    novedades = c.fetchall()
    conn.close()
    return render_template('plantilla_incapacidades.html', novedades=novedades)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incapacidades.db, usuarios.db'
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

def obtener_novedad_por_id(novedad_id):
    # Conectar a la base de datos y obtener el nombre de la novedad
    conn = sqlite3.connect('incapacidades.db')
    c = conn.cursor()
    c.execute("SELECT nombre FROM incapacidad WHERE id=?", (novedad_id,))
    novedad = c.fetchone()
    conn.close()
    if novedad:
        return {'nombre': novedad[0]}
    else:
        return None

@app.route('/descargar_pdf/<int:novedad_id>')
def descargar_pdf(novedad_id):
    try:
        print(f'Intentando descargar PDF con id: {novedad_id}')  # Depuración

        # Conectar a la base de datos
        conn = sqlite3.connect('incapacidades.db')
        c = conn.cursor()
        
        # Seleccionar el BLOB del PDF
        c.execute("SELECT archivo_pdf FROM incapacidad WHERE id=?", (novedad_id,))
        pdf_data = c.fetchone()
        
        # Verificar si se obtuvo algún resultado
        if pdf_data is None:
            flash('No se encontró el archivo PDF solicitado.', 'danger')
            print('No se encontró el archivo PDF solicitado.')  # Depuración
            return redirect(url_for('admin'))
        
        print('PDF encontrado, preparando para enviar...')  # Depuración
        
        # Obtener el nombre de la novedad
        novedad = obtener_novedad_por_id(novedad_id)
        if not novedad:
            flash('No se encontró la novedad solicitada.', 'danger')
            return redirect(url_for('admin'))
        
        novedad_nombre = novedad['nombre']
        
        # Convertir los datos del PDF en bytes y enviarlos al cliente
        return send_file(io.BytesIO(pdf_data[0]), 
                         mimetype='application/pdf', 
                         as_attachment=True, 
                         download_name=f'INCAPACIDAD_{novedad_nombre}.pdf')
    
    except sqlite3.Error as e:
        flash(f'Ocurrió un error al acceder a la base de datos: {str(e)}', 'danger')
        print(f'Ocurrió un error al acceder a la base de datos: {str(e)}')  # Depuración
        return redirect(url_for('admin'))
    
    except Exception as e:
        flash(f'Ocurrió un error al intentar descargar el PDF: {str(e)}', 'danger')
        print(f'Ocurrió un error al intentar descargar el PDF: {str(e)}')  # Depuración
        return redirect(url_for('admin'))
    
    finally:
        if conn:
            conn.close()
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

#------------------agenda-----------------------------

contabilidad = 'contabilidad.db'

@app.route('/contabilidad')
def contabilidad_view():
    create_db(contabilidad)
    conn = sqlite3.connect(contabilidad)
    c = conn.cursor()
    c.execute('SELECT * FROM agenda WHERE completada=0')
    actividades4 = c.fetchall()
    conn.close()
    return render_template('contabilidad.html', actividades4=actividades4)

@app.route('/agregar4', methods=['POST'])
def agregar_actividad4():
    actividad = request.form['actividad']
    conn = sqlite3.connect(contabilidad)
    c = conn.cursor()
    c.execute('INSERT INTO agenda (actividad, completada) VALUES (?, 0)', (actividad,))
    conn.commit()
    conn.close()
    return redirect(url_for('contabilidad_view'))

@app.route('/completar4/<int:id>')
def completar_actividad4(id):
    conn = sqlite3.connect(contabilidad)
    c = conn.cursor()
    c.execute('UPDATE agenda SET completada=1 WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('contabilidad_view'))

#---------------------------INICIA SESSION DE CALIDAD----------------------------

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'sistematizacionholadr@gmail.com'
app.config['MAIL_PASSWORD'] = 'pbwd niad rizh oryg'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

app.config['DATABASE'] = 'soporte.db'

# mail = Mail(app)

def conectar_db():
    try:
        conexion = sqlite3.connect(app.config['DATABASE'])
        return conexion
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def obtener_registros_mantenimiento():
    try:
        with conectar_db() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM mantenimiento_locativo")
            registros = cursor.fetchall()
            return registros
    except Exception as e:
        print(f"Error al obtener los registros: {e}")
        return []

def guardar_solicitud(lider_a_cargo, ubicacion, detalle_solicitud, prioridad, fecha_envio, estado):
    try:
        with conectar_db() as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO mantenimiento_locativo (lider_a_cargo, ubicacion, detalle_solicitud, prioridad, fecha_envio,estado)
                VALUES (?,?,?,?,?,?)
            """, (lider_a_cargo, ubicacion, detalle_solicitud, prioridad, fecha_envio, estado))
            conexion.commit()
    except Exception as e:
        print(f"Error al guardar la solicitud: {e}")

# def enviar_correo(lider_a_cargo, ubicacion, detalle_solicitud, prioridad, fecha_envio, estado):
#     try:
#         destino = ''
#         mensaje = Message('Nueva Solicitud de Mantenimiento Locativo',
#                           sender=app.config['MAIL_USERNAME'],
#                           recipients=[destino])
#         mensaje.body = f"Lider a cargo: {lider_a_cargo}\nUbicación: {ubicacion}\nDetalle de la Solicitud: {detalle_solicitud}\nPrioridad: {prioridad}\nFecha de envio: {fecha_envio}\nEstado: {estado}"
#         mail.send(mensaje)
#     except Exception as e:
#         print(f"Error al enviar el correo: {e}")

@app.route('/mantenimiento_locativo', methods=['GET', 'POST'])
def mantenimiento_locativo():
    if request.method == 'POST':
        lider_a_cargo = request.form.get('lider_a_cargo')
        ubicacion = request.form.get('ubicacion')
        detalle_solicitud = request.form.get('detalle_solicitud')
        prioridad = request.form.get('prioridad')
        fecha_envio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        estado = 'pendiente'
        guardar_solicitud(lider_a_cargo, ubicacion, detalle_solicitud, prioridad, fecha_envio, estado)
        # enviar_correo(lider_a_cargo, ubicacion, detalle_solicitud, prioridad, fecha_envio, estado)
        return render_template('admin.html')
    else:
        return render_template('plantilla_mantenimiento.html')

@app.route('/plantilla_mantenimiento', methods=['GET', 'POST'])
def plantilla_mantenimiento():
    if request.method == 'POST':
        observaciones = request.form.get('observaciones')
        estado = request.form.get('estado')
        fecha_finalizacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return redirect(url_for('plantilla_mantenimiento'))
    else:
        registros = obtener_registros_mantenimiento()
        return render_template('plantilla_mantenimiento.html', registros=registros)

@app.route('/updatemant', methods=['POST'])
def updatemant():
    id_ = request.form.get('id')
    observaciones = request.form.get('observaciones')
    estado = request.form.get('estado')
    fecha_finalizacion = datetime.now().strftime('%Y-%m-%d - %H:%M')
    query = 'UPDATE mantenimiento_locativo SET observaciones=?, estado=?, fecha_finalizacion=? WHERE id=?'
    params = (observaciones, estado , fecha_finalizacion, id_)
    with closing(conectar_db()) as db:
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()
    return redirect(url_for('plantilla_mantenimiento'))

@app.route('/exportar_a_excel_mantenimientos')
def exportar_a_excel_mantenimientos():
    with sqlite3.connect('soporte.db') as conn:
        df = pd.read_sql_query("SELECT * FROM mantenimiento_locativo", conn)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='mantenimientos')
    writer._save()
    writer.close()
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='consolidado_mantenimientos.xlsx')

#---------------------------FINALIZA SESSION DE CALIDAD--------------------------
@app.route('/boletines')
def boletines():

    return render_template('boletines.html')

@app.route('/politicas_internas')
def politicas_internas():

    return render_template('politicas_internas.html')



#-------------------actas---------------------------------------------------------
# 
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
DATABASE2 = 'registro.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE2)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/actas2')
def actas2():
    conn = get_db_connection()
    actas = conn.execute("SELECT * FROM registro2 ORDER BY fecha_envio DESC").fetchall()
    conn.close()
    return render_template('actas2.html', actas=actas)

@app.route('/descargar_acta_pdf/<int:acta_cedula>')
def descargar_acta_pdf(acta_cedula):
    conn = get_db_connection()
    acta = conn.execute('SELECT * FROM registro2 WHERE cedula = ?', (acta_cedula,)).fetchone()
    conn.close()

    if acta:
        # Generar el PDF
        nombre_pdf = f'acta_puesto_{acta_cedula}.pdf'
        pdf_path = os.path.join(app.root_path, 'static', nombre_pdf)
        generar_pdf_desde_datos(acta, pdf_path)

        return send_file(pdf_path, as_attachment=True, download_name=nombre_pdf)
    else:
        return 'Acta no encontrada'

def generar_pdf_desde_datos(acta, pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=letter)

    # Insertar imagen en la esquina superior derecha
    img_path = os.path.join(app.root_path, 'logo2.jpg')
    c.drawImage(img_path, letter[0]-3.3*inch, letter[1]-1*inch, width=3*inch, height=1*inch)

    # Definir el contenido estático y dinámico de la plantilla
    contenido = [
        f"ACTA DE ENTREGA Y RETIRO DE PUESTOS DE TRABAJO",
        f"",
        f"Fecha: {acta['fecha_envio']}",
        f"Nombre Completo: {acta['nombres_completos']}",
        f"Cedula: {acta['cedula']}",
        f"Cargo: {acta['cargo']}",
        f"Numero Puesto: {acta['numero_puesto']}",
        f"Celular Corporativo: {acta['extension']}",
        
        f"Estado: {acta['estado']}",
    ]

    # Configurar el tamaño de la página y la posición inicial del texto
    x, y = 50, 750

    # Escribir el contenido en el PDF
    for line in contenido:
        c.drawString(x, y, line)
        y -= 25  # Espacio entre líneas

    # Tabla de elementos de computadora
    elementos_computadora = [
        ["Portatil", acta['ml_pc']],
        ["Guaya", acta['guaya']],
        ["Monitor", acta['ml_pantalla']],
        ["Mouse", acta['mause']],
        ["Diadema", acta['diadema']]
    ]
    c.drawString(x, y-50, "Elementos de Computadora:")
    draw_table(c, x, y-75, elementos_computadora)

    # Tabla de elementos de oficina
    elementos_oficina = [
        ["Silla", acta['silla']],
        ["Cubiculo", acta['cubiculo']],
        ["Descansapies", acta['descansapies']],
        ["Observaciones", acta['observaciones']]
    ]
    c.drawString(x, y-200, "Elementos de Oficina:")
    draw_table(c, x, y-225, elementos_oficina)

    # Espacio para las firmas y cargos
    y -= 300  # Espacio adicional para separar la tabla del área de firmas

    # Primera firma y cargo
    c.drawString(x, y-50,  f"Firma: {acta['nombres_completos']}")
    c.line(x + 50, y-60, x + 250, y-60)  # Línea para la primera firma
    c.drawString(x, y-100, f"Cargo: {acta['cargo']}",)
    c.drawString(x + 50, y-100, "______")  # Línea para el cargo 1

    # Segunda firma y cargo
    c.drawString(x + 300, y-50, "Entrega: Milena echavarria henao")
    c.line(x + 350, y-60, x + 550, y-60)  # Línea para la segunda firma
    c.drawString(x + 300, y-100, "Cargo: Lider operaciones holadr")
    c.drawString(x + 350, y-100, "________")  # Línea para el cargo 2

    c.save()

def draw_table(c, x, y, data):
    table = Table(data, colWidths=[180, 180])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0, 0, 0)),  # Color del texto
        ('INNERGRID', (0, 0), (-1, -1), 0.25, (0, 0, 0)),  # Borde interno
        ('BOX', (0, 0), (-1, -1), 0.25, (0, 0, 0)),  # Borde externo
    ]))
    width, height = table.wrapOn(c, 400, 200)
    table.drawOn(c, x + (400 - width) / 2, y - height)
    
    
@app.route('/exportar_a_excel_actas')
def exportar_a_excel_actas():
    # Conectar a la base de datos y obtener los datos
    with sqlite3.connect('registro.db') as conn:
        df = pd.read_sql_query("SELECT * FROM registro2", conn)

    # Crear un archivo Excel en memoria
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='actas')
    writer._save()

    # Asegurarse de que el archivo Excel se cierre correctamente
    writer.close()

    # Crear un objeto de respuesta Flask que envía el archivo Excel
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='actas de ingreso y retiro.xlsx')
# -------------------FINALIZA FORMULARIO DE REGISTRO DE ACTIVOS------------------------------------

#--------------------------FINALIZA SESSION DE CONTABILIDAD----------------------
if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0', port=5000)
    