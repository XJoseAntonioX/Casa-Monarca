from flask import Blueprint, render_template
from Casa_Monarca import login_required

# Create a user blueprint
user_bp = Blueprint('user', __name__,
                   template_folder='templates',
                   static_folder='static',
                   static_url_path='/user/static')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """Render the main user dashboard with navigation bar"""
    return render_template('NavBar.html')
