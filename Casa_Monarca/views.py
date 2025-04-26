# Funciones declaradas en __init__.py:
from Casa_Monarca import app, container, login_required
from flask import request, url_for, redirect, session, render_template, make_response
import traceback
from azure.cosmos import exceptions

@app.route('/')
def index():
    if "email" in session and "user_id" in session:
        return redirect(url_for('blank'))
    else:
        # Set headers to prevent cache on login page
        response = make_response(render_template("main.html"))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

@app.route('/blank')
@login_required
def blank():
    return render_template('blank.html')

# API endpoint for authentication
@app.route('/auth', methods=['POST'])
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
            # User found, redirect to success page
            return redirect(url_for('blank'))
        else:
            # User not found, redirect to main page with error
            return redirect(url_for('index', auth_error=True))
    
    except exceptions.CosmosHttpResponseError as ce:
        error_msg = f"Cosmos DB Error: {str(ce)}"
        print(error_msg)
        return redirect(url_for('index', auth_error=True))
    except Exception as e:
        error_msg = f"Authentication Error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return redirect(url_for('index', auth_error=True))

# Add route to logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))