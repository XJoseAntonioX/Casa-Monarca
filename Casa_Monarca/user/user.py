from flask import Blueprint, render_template
from Casa_Monarca import login_required, container
from datetime import datetime

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

@user_bp.route('/document_history')
@login_required
def document_history():
    """Render the document history page with data from Cosmos DB"""
    try:
        # Query all documents from Cosmos DB (using a simple select all query)
        query = "SELECT * FROM c"
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        # Process the records for display
        documents = []
        for item in items:
            # Format date from timestamp (if available)
            date_display = "N/A"
            if 'timestamp' in item:
                try:
                    # Parse the timestamp and format as day/month/year
                    dt = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                    date_display = dt.strftime('%d/%m/%Y')
                except (ValueError, TypeError):
                    date_display = "Invalid date"
            
            # Determine signed status
            sign_status = "Firmado" if item.get('is_signed', False) else "Pendiente"
            
            # Create a document record for the template
            doc = {
                'id': item.get('id', 'Unknown'),
                'name': item.get('document_name', 'Unknown'),
                'document': item.get('document_name', 'No document'),
                'sign': sign_status,
                'date': date_display
            }
            documents.append(doc)
        
        return render_template('document_history.html', documents=documents)
    
    except Exception as e:
        # Log the error and return an error message
        print(f"Error fetching document history: {str(e)}")
        return render_template('document_history.html', 
                              documents=[],
                              error="Error loading document history")
