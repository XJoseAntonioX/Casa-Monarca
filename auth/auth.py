from flask import Flask, request, url_for, redirect, session, render_template, jsonify, make_response
import os
import traceback
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, exceptions
import secrets
from functools import wraps

# Inicializa Flask con la carpeta actual como ubicación de archivos estáticos y plantillas
app = Flask(__name__, static_folder='static', template_folder='templates')
# Configura una clave secreta para firmar las cookies de sesión
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(16))

# Carga variables de entorno desde el archivo db.env
load_dotenv('auth/db.env')  # Asegura la ruta correcta al archivo

# Obtiene los detalles de conexión a Cosmos DB
url = os.getenv("url")
key = os.getenv("key")
database_name = os.getenv("database_name")
container_name = os.getenv("container_name")

# Decorador para requerir autenticación y prevenir navegación hacia atrás
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session or "user_id" not in session:
            return redirect(url_for('index'))
        response = make_response(f(*args, **kwargs))
        # Agregar encabezados para prevenir caché
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function

# Ruta para servir la página principal
@app.route('/')
def index():
    if "email" in session and "user_id" in session:
        return redirect(url_for('blank'))
    else:
        # Establecer encabezados para prevenir caché en la página de login
        response = make_response(render_template("main.html"))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

@app.route('/blank')
@login_required
def blank():
    return render_template('blank.html')

# Endpoint de API para autenticación
@app.route('/auth', methods=['POST'])
def auth():
    try:
        # Obtiene email y password del formulario y sanitiza las entradas
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Inicializa el cliente de CosmosDB
        client = CosmosClient(url, credential=key)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        # Consulta usando el campo correcto (ajusta según tu esquema real)
        query = "SELECT * FROM c WHERE c.email = @email AND c.password = @password"

        parameters = [
            {"name": "@email", "value": email},
            {"name": "@password", "value": password}
        ]
        
        # Ejecuta la consulta
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
                
        if items:
            # Guarda el ID de usuario en la sesión
            session['user_id'] = items[0].get('id')
            # Guarda información del usuario en la sesión
            session['email'] = email
            # Usuario encontrado, redirecciona a la página de éxito
            return redirect(url_for('blank'))
        else:
            # Usuario no encontrado, redirecciona a la página principal con error
            return redirect(url_for('index', auth_error=True))
    
    except exceptions.CosmosHttpResponseError as ce:
        error_msg = f"Error de Cosmos DB: {str(ce)}"
        print(error_msg)
        return redirect(url_for('index', auth_error=True))
    except Exception as e:
        error_msg = f"Error de autenticación: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return redirect(url_for('index', auth_error=True))

# Añade una ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Inicia el servidor Flask en modo de depuración
if __name__ == '__main__':
    app.run(debug=True)
