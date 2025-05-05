from flask import Blueprint

# Create a blueprint for shared components
components_bp = Blueprint('components', __name__,
                         static_folder='static',
                         static_url_path='/components/static')
