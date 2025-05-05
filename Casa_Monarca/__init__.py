from flask import Flask
import os
import secrets
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
from functools import wraps
from flask import request, url_for, redirect, session, render_template, make_response

# Initialize Flask with current folder as static and template location
app = Flask(__name__, 
            static_folder='static',  # Root level static folder for common assets
            static_url_path='/static',  # URL path for the common static folder
            template_folder='auth/templates')
# Set secret key for signing session cookies
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(16))

# Load environment variables from db.env file
load_dotenv('Casa_Monarca/db.env')  # Updated path to the new location

# Get Cosmos DB connection details
url = os.getenv("url")
key = os.getenv("key")
database_name = os.getenv("database_name")
container_name = os.getenv("container_name")

# Add some basic error handling
if not url or not key:
    raise ValueError("Cosmos DB credentials not found in environment variables")

# Initialize Cosmos DB client - pass key as second positional argument
client = CosmosClient(url, key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

# Decorator for requiring authentication and preventing back navigation
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session or "user_id" not in session:
            return redirect(url_for('auth.index'))
        response = make_response(f(*args, **kwargs))
        # Add headers to prevent cache
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function

# Register the auth blueprint
from Casa_Monarca.auth.auth import auth_bp
app.register_blueprint(auth_bp)

# Register the user blueprint
from Casa_Monarca.user.user import user_bp
app.register_blueprint(user_bp, url_prefix='/user')

# Register the components blueprint
from Casa_Monarca.components.components import components_bp
app.register_blueprint(components_bp, url_prefix='/components')