from flask import Flask, render_template, request,redirect, url_for, flash
import sqlite3
from datetime import datetime
from flask import session
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
import mysql.connector


app = Flask(__name__)


app.secret_key = 'holadr'

def create_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="atenciones.db"
    )
    return conn

@app.route('/')
def inicio():
    return render_template('index.html')

# --------------- INICIA REGISTRO DE PACIENTES---------------------

def create_database():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()

    # Crear tabla de formulario
    c.execute('''CREATE TABLE IF NOT EXISTS pacientes
                 (tipo_de_documento text, numero_de_documento text, fecha_de_atencion date, medico_quien_atiende text, fecha_envio text)''')
    
    # Crear tabla para almacenar el conteo de formularios enviados
    c.execute('''CREATE TABLE IF NOT EXISTS paciente
                 (count integer)''')

    # Inicializar el conteo de formularios enviados
    c.execute('''INSERT INTO paciente (count) VALUES (0)''')

    conn.commit()
    conn.close()

create_database()

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
    c.execute("INSERT INTO pacientes (tipo_de_documento, numero_de_documento, fecha_de_atencion, medico_quien_atiende, fecha_envio) VALUES (?, ?, ?,?,?)", (tipo_de_documento, numero_de_documento, fecha_de_atencion, medico_quien_atiende, fecha_envio,))
    conn.commit()
    conn.close()

    # Almacenar los valores de los campos del formulario en variables de sesión
    
    session['fecha_de_atencion'] = fecha_de_atencion
    session['medico_quien_atiende'] = medico_quien_atiende

    return redirect(url_for('registro'))

@app.route('/show_data_of_the_day')
def show_data_of_the_day():
    today = datetime.now().strftime('%Y-%m-%d')  # Obtener la fecha actual

    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("SELECT * FROM pacientes WHERE fecha_envio LIKE ?", (today + '%',))
    rows = c.fetchall()
    conn.close()

    return render_template('data_of_the_day.html', rows=rows)

# ---------------------FINALIZA REGISTRO DE PACIENTES-----------------------------

# ---------INICIA FORMULARIO REGISTRO DE ACTIVOS------------------------------
 
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
    return render_template('form.html')

@app.route('/formulario2', methods=['POST'])
def procesar_formulario2():
    nombres_completos = request.form.get('nombres_completos')
    cedula = request.form.get('cedula')
    cargo = request.form.get('cargo')
    numero_puesto = request.form.get('numero_puesto')
    extension = request.form.get('extension')
    ml_pc = request.form.get('ml_pc')
    ml_pantalla = request.form.get('ml_pantalla')
    mause = request.form.get('mause')
    guaya = request.form.get('guaya')
    cargador = request.form.get('cargador')
    diadema = request.form.get('diadema')
    otros = request.form.get('otros')
    silla = request.form.get('silla')
    cubiculo = request.form.get('cubiculo')
    descansapies = request.form.get('descansapies')
    observaciones = request.form.get('observaciones')

    conn = sqlite3.connect('registro.db')
    c = conn.cursor()
    c.execute("INSERT INTO registro (nombres_completos, cedula, cargo, numero_puesto, extension, ml_pc, ml_pantalla, mause, guaya, cargador, diadema, otros, silla, cubiculo, descansapies, observaciones) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (nombres_completos, cedula, cargo, numero_puesto, extension, ml_pc, ml_pantalla, mause, guaya, cargador,diadema,otros,silla,cubiculo,descansapies,observaciones))
    conn.commit()
    conn.close()

    return 'formulario registrado con éxito!'

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

@app.route('/estado_solicitud')
def estado_solicitud():
    today = datetime.now().strftime('%Y-%m-%d')  # Obtener la fecha actual

    conn = sqlite3.connect('soporte.db')
    c = conn.cursor()
    c.execute("SELECT * FROM solicitar_soporte WHERE fecha_envio LIKE ?", (today + '%',))
    rows = c.fetchall()
    conn.close()
    
    return render_template('estado_solicitud.html', rows=rows)


# ------------------------FINALIZA FORMULARIO DE SOPORTE--------------------------------------------

#-------------------------INICIA FORMULARIO DE NOVEDADES---------------------------------------------

def create_database():
    conn = sqlite3.connect('novedades.db') # Crea la base de datos si no existe
    c = conn.cursor()

    # Crea la tabla si no existe
    c.execute('''CREATE TABLE IF NOT EXISTS novedades
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 nombre TEXT NOT NULL,
                 tipo_novedad TEXT NOT NULL,
                 lider_a_cargo TEXT NOT NULL,
                 fecha_inicio TEXT NOT NULL,
                 fecha_fin TEXT NOT NULL,
                 dias_novedad INTEGER NOT NULL,
                 observaciones TEXT,
                 archivo_pdf BLOB)''')

    conn.commit()
    conn.close()
create_database()

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

    # Leer el archivo PDF y convertirlo en bytes
    pdf_data = archivo_pdf.read()

    # Conectar a la base de datos y guardar los datos
    conn = sqlite3.connect('novedades.db')
    c = conn.cursor()
    c.execute("INSERT INTO novedades (nombre, tipo_novedad, lider_a_cargo, fecha_inicio, fecha_fin, dias_novedad, observaciones, archivo_pdf) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (nombre, tipo_novedad, lider_a_cargo, fecha_inicio, fecha_fin, dias_novedad, observaciones, sqlite3.Binary(pdf_data)))
    conn.commit()
    conn.close()

    return redirect(url_for('inicio'))




#-------------------------FINALIZA FORMULARIO NOVEDADES DE NOMINA------------------------------------------

if __name__ == '__main__':
    
    app.run(debug=True,  host='0.0.0.0', port=8080)
