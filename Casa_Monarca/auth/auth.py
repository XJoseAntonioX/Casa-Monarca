from flask import Blueprint, request, url_for, redirect, session, render_template, make_response
import traceback
from azure.cosmos import exceptions
from Casa_Monarca import container, login_required

# Create a blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, 
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='/auth/static')

@auth_bp.route('/')
def index():
    if "email" in session and "user_id" in session:
        return redirect(url_for('user.dashboard'))
    else:
        # Set headers to prevent cache on login page
        response = make_response(render_template("main.html"))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

# API endpoint for authentication
@auth_bp.route('/auth', methods=['POST'])
def auth():
    try:
        # Get email and password from form and sanitize inputs
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Query using the correct field (adjust according to your actual schema)
        query = "SELECT * FROM c WHERE c.email = @email AND c.password = @password"

        parameters = [
            {"name": "@email", "value": email},
            {"name": "@password", "value": password}
        ]
        
        # Execute the query
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
                
        if items:
            # Save user ID in session
            session['user_id'] = items[0].get('id')
            # Save user information in session
            session['email'] = email
            # User found, redirect to user dashboard with NavBar
            return redirect(url_for('user.dashboard'))
        else:
            # User not found, redirect to main page with error
            return redirect(url_for('auth.index', auth_error=True))
    
    except exceptions.CosmosHttpResponseError as ce:
        error_msg = f"Cosmos DB Error: {str(ce)}"
        print(error_msg)
        return redirect(url_for('auth.index', auth_error=True))
    except Exception as e:
        error_msg = f"Authentication Error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return redirect(url_for('auth.index', auth_error=True))

# Add route to logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))