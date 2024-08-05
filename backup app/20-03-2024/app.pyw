from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import sqlite3
from datetime import datetime
from flask import session
from flask import jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from contextlib import closing


app = Flask(__name__)
app.secret_key = 'Admin12345*+'


#--------------------------inicia session de login----------------------------

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
        if role == 'medico':
            return role, 'index', first_login
        elif role == 'administrativo':
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
    if 'username' in session and session['role'] == 'medico':
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

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

#---------------------fin login-------------------------------


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


# @app.route('/show_data_of_the_day')
# def show_data_of_the_day():
#     today = datetime.now().strftime('%Y-%m-%d')  # Obtener la fecha actual

#     conn = sqlite3.connect('usuarios.db')
#     c = conn.cursor()
#     c.execute("SELECT * FROM pacientes WHERE fecha_envio LIKE ?", (today + '%',))
#     rows = c.fetchall()
#     conn.close()

#     return render_template('data_of_the_day.html', rows=rows)

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
    success_message = session.get('success_message', None)
    return render_template('form.html', success_message=success_message)
   

@app.route('/formulario2', methods=['POST'])
def procesar_formulario2():
    nombres_completos = request.form.get('nombres_completos')
    cedula = request.form.get('cedula')
    cargo = request.form.get('cargo')
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
    c.execute("INSERT INTO registro (nombres_completos, cedula, cargo, numero_puesto, extension, ml_pc, ml_pantalla, mause, guaya, cargador, diadema, fecha_envio, silla, cubiculo, descansapies, observaciones) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (nombres_completos, cedula, cargo, numero_puesto, extension, ml_pc, ml_pantalla, mause, guaya, cargador,diadema,fecha_envio,silla,cubiculo,descansapies,observaciones))
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

#----------------------inicia talento humano-------------------------
@app.route('/talento_humano')
def talento_humano():
     return render_template('talento_humano.html')

# @app.route('/talento_humano')
# def talento_humano():
#     conn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM personal")
#     personal = cursor.fetchall()
#     conn.close()
#     return render_template('talento_humano.html', personal=personal)

# # Ruta para agregar un nuevo registro
# @app.route('/add', methods=['POST'])
# def add_personal():
#     if request.method == 'POST':
#         nombre = request.form['nombre']
#         apellido = request.form['apellido']
#         estado = request.form['estado']
#         # Agrega validaciones u otros campos según sea necesario
#         conn = connect_db()
#         cursor = conn.cursor()
#         cursor.execute("INSERT INTO personal (nombre, apellido, estado) VALUES (?, ?, ?)", (nombre, apellido, estado))
#         conn.commit()
#         conn.close()
#         flash('Personal agregado exitosamente.')
#     return redirect(url_for('talento_humano'))

# # Ruta para eliminar un registro
# @app.route('/delete/<int:id>')
# def delete_personal(id):
#     conn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM personal WHERE id=?", (id,))
#     conn.commit()
#     conn.close()
#     flash('Personal eliminado exitosamente.')
#     return redirect(url_for('talento_humano'))

# # Ruta para editar un registro
# @app.route('/edit/<int:id>', methods=['GET', 'POST'])
# def edit_personal(id):
#     conn = connect_db()
#     cursor = conn.cursor()
#     if request.method == 'POST':
#         nuevo_estado = request.form['nuevo_estado']
#         cursor.execute("UPDATE personal SET estado=? WHERE id=?", (nuevo_estado, id))
#         conn.commit()
#         conn.close()
#         flash('Estado actualizado exitosamente.')
#         return redirect(url_for('talento_humano'))
#     else:
#         cursor.execute("SELECT * FROM personal WHERE id=?", (id,))
#         personal = cursor.fetchone()
#         conn.close()
#         return render_template('edit.html', personal=personal)

#-----------------------finaliza talento humano-------------------------
#------------------------inicia session nomina--------------------------

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

#-------------------------finaliza session nomina-----------------------

#-------------------------OPERACIONES------------------------------------

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
#-------------------lineas---------------------




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
    id = request.form['id']
    linea = request.form['linea']
    imei = request.form['imei']
    nombre = request.form['nombre']
    cargo = request.form['cargo']
    cedula = request.form['cedula']
    detalle_entrega = request.form['detalle_entrega']
    fecha_entrega = request.form['fecha_entrega']
    observacion = request.form['observacion']

    with closing(connect_db2()) as db:
        cursor = db.cursor()
        cursor.execute("UPDATE asignaciones SET linea=?, imei=?,cedula=?, detalle_entrega=?, fecha_entrega=?, observacion=? WHERE id=?", 
                        (linea, imei, cedula, detalle_entrega, fecha_entrega, observacion, id))
        db.commit()

    return redirect(url_for('lineas'))

#--------------------------FIN OPERACIONES----------------------------------
if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0', port=5000)
    
    23