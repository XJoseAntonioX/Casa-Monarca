from flask import Flask, send_from_directory
from auth.auth import authenticate, sanitize_input
import webbrowser
import threading
import time
import os

app = Flask(__name__)

# Configurar rutas estáticas
@app.route('/')
def index():
    return send_from_directory('auth/templates', 'main.html')

@app.route('/styles.css')
def styles():
    return send_from_directory('auth/static_files', 'styles.css')

@app.route('/scripts.js')
def scripts():
    return send_from_directory('auth', 'scripts.js')

@app.route('/images/<path:filename>')
def images(filename):
    return send_from_directory('auth/images', filename)

@app.route('/blank.html')
def blank():
    return send_from_directory('.', 'blank.html')

# Endpoint para autenticación
@app.route('/api/auth', methods=['POST'])
def auth():
    return authenticate()

def open_browser():
    """Abrir el navegador automáticamente después de iniciar Flask"""
    time.sleep(1)
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Iniciar navegador en un hilo separado
    threading.Thread(target=open_browser).start()
    app.run(debug=True)