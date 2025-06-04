import os
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import time
import random

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# In-memory storage
users = {}  # email -> {password_hash, api_key, created_at}
services = {}  # service_id -> {name, description, user_api_key, created_at}
templates = {}  # template_id -> {name, subject, body, service_id, created_at}
messages = {}  # message_id -> {template_id, recipient, type, status, sent_at, delivered_at}

def generate_api_key():
    """Generate a unique API key"""
    return str(uuid.uuid4())

def generate_message_id():
    """Generate a unique message ID"""
    return str(uuid.uuid4())

def simulate_message_delivery():
    """Simulate message delivery status changes"""
    statuses = ['pending', 'sent', 'delivered', 'failed']
    weights = [0.1, 0.2, 0.6, 0.1]  # Higher chance of delivery
    return random.choices(statuses, weights=weights)[0]

def get_user_by_api_key(api_key):
    """Find user by API key"""
    for email, user_data in users.items():
        if user_data['api_key'] == api_key:
            return email, user_data
    return None, None

def validate_api_key():
    """Validate API key from request headers"""
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return None, jsonify({'error': 'API key required in X-API-Key header'}), 401
    
    email, user_data = get_user_by_api_key(api_key)
    if not user_data:
        return None, jsonify({'error': 'Invalid API key'}), 401
    
    return email, None, None

# Routes

@app.route('/')
def index():
    """Serve the documentation and testing interface"""
    return render_template('index.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    """User sign-up endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        if email in users:
            return jsonify({'error': 'User already exists'}), 409
        
        # Generate API key and hash password
        api_key = generate_api_key()
        password_hash = generate_password_hash(password)
        
        # Store user
        users[email] = {
            'password_hash': password_hash,
            'api_key': api_key,
            'created_at': datetime.utcnow().isoformat()
        }
        
        app.logger.info(f"New user registered: {email}")
        
        return jsonify({
            'message': 'User created successfully',
            'email': email,
            'api_key': api_key
        }), 201
        
    except Exception as e:
        app.logger.error(f"Error in signup: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/services', methods=['POST'])
def create_service():
    """Create a service linked to user's API key"""
    try:
        email, error_response, status_code = validate_api_key()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Service name is required'}), 400
        
        service_id = str(uuid.uuid4())
        service_data = {
            'id': service_id,
            'name': data['name'],
            'description': data.get('description', ''),
            'user_api_key': users[email]['api_key'],
            'user_email': email,
            'created_at': datetime.utcnow().isoformat()
        }
        
        services[service_id] = service_data
        
        app.logger.info(f"Service created: {service_id} by {email}")
        
        return jsonify({
            'message': 'Service created successfully',
            'service': service_data
        }), 201
        
    except Exception as e:
        app.logger.error(f"Error in create_service: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/services', methods=['GET'])
def get_services():
    """Get all services for the authenticated user"""
    try:
        email, error_response, status_code = validate_api_key()
        if error_response:
            return error_response, status_code
        
        user_api_key = users[email]['api_key']
        user_services = [service for service in services.values() 
                        if service['user_api_key'] == user_api_key]
        
        return jsonify({
            'services': user_services
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in get_services: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/templates', methods=['POST'])
def create_template():
    """Create a template linked to a service"""
    try:
        email, error_response, status_code = validate_api_key()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        required_fields = ['name', 'subject', 'body', 'service_id']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Name, subject, body, and service_id are required'}), 400
        
        service_id = data['service_id']
        
        # Check if service exists and belongs to user
        if service_id not in services:
            return jsonify({'error': 'Service not found'}), 404
        
        user_api_key = users[email]['api_key']
        if services[service_id]['user_api_key'] != user_api_key:
            return jsonify({'error': 'Service does not belong to user'}), 403
        
        template_id = str(uuid.uuid4())
        template_data = {
            'id': template_id,
            'name': data['name'],
            'subject': data['subject'],
            'body': data['body'],
            'service_id': service_id,
            'created_at': datetime.utcnow().isoformat()
        }
        
        templates[template_id] = template_data
        
        app.logger.info(f"Template created: {template_id} by {email}")
        
        return jsonify({
            'message': 'Template created successfully',
            'template': template_data
        }), 201
        
    except Exception as e:
        app.logger.error(f"Error in create_template: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all templates for the authenticated user's services"""
    try:
        email, error_response, status_code = validate_api_key()
        if error_response:
            return error_response, status_code
        
        user_api_key = users[email]['api_key']
        user_service_ids = [service_id for service_id, service in services.items() 
                           if service['user_api_key'] == user_api_key]
        
        user_templates = [template for template in templates.values() 
                         if template['service_id'] in user_service_ids]
        
        return jsonify({
            'templates': user_templates
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in get_templates: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/notifications/email', methods=['POST'])
def send_email_notification():
    """Send an email notification using a template"""
    try:
        email, error_response, status_code = validate_api_key()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        if not data or 'template_id' not in data or 'recipient_email' not in data:
            return jsonify({'error': 'Template ID and recipient email are required'}), 400
        
        template_id = data['template_id']
        recipient_email = data['recipient_email']
        
        # Check if template exists
        if template_id not in templates:
            return jsonify({'error': 'Template not found'}), 404
        
        template = templates[template_id]
        service_id = template['service_id']
        
        # Check if service belongs to user
        user_api_key = users[email]['api_key']
        if services[service_id]['user_api_key'] != user_api_key:
            return jsonify({'error': 'Template does not belong to user'}), 403
        
        # Validate recipient email
        if '@' not in recipient_email or '.' not in recipient_email:
            return jsonify({'error': 'Invalid recipient email format'}), 400
        
        # Generate message ID and simulate sending
        message_id = generate_message_id()
        initial_status = 'pending'
        
        message_data = {
            'id': message_id,
            'template_id': template_id,
            'recipient': recipient_email,
            'type': 'email',
            'status': initial_status,
            'sent_at': datetime.utcnow().isoformat(),
            'subject': template['subject'],
            'body': template['body']
        }
        
        messages[message_id] = message_data
        
        app.logger.info(f"Email notification sent: {message_id} to {recipient_email}")
        
        return jsonify({
            'message': 'Email notification sent successfully',
            'message_id': message_id,
            'status': initial_status
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in send_email_notification: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/notifications/sms', methods=['POST'])
def send_sms_notification():
    """Send an SMS notification using a template"""
    try:
        email, error_response, status_code = validate_api_key()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        
        if not data or 'template_id' not in data or 'recipient_phone' not in data:
            return jsonify({'error': 'Template ID and recipient phone are required'}), 400
        
        template_id = data['template_id']
        recipient_phone = data['recipient_phone']
        
        # Check if template exists
        if template_id not in templates:
            return jsonify({'error': 'Template not found'}), 404
        
        template = templates[template_id]
        service_id = template['service_id']
        
        # Check if service belongs to user
        user_api_key = users[email]['api_key']
        if services[service_id]['user_api_key'] != user_api_key:
            return jsonify({'error': 'Template does not belong to user'}), 403
        
        # Basic phone validation
        clean_phone = ''.join(filter(str.isdigit, recipient_phone))
        if len(clean_phone) < 10:
            return jsonify({'error': 'Invalid phone number format'}), 400
        
        # Generate message ID and simulate sending
        message_id = generate_message_id()
        initial_status = 'pending'
        
        message_data = {
            'id': message_id,
            'template_id': template_id,
            'recipient': recipient_phone,
            'type': 'sms',
            'status': initial_status,
            'sent_at': datetime.utcnow().isoformat(),
            'body': template['body']
        }
        
        messages[message_id] = message_data
        
        app.logger.info(f"SMS notification sent: {message_id} to {recipient_phone}")
        
        return jsonify({
            'message': 'SMS notification sent successfully',
            'message_id': message_id,
            'status': initial_status
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in send_sms_notification: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/messages/<message_id>/status', methods=['GET'])
def get_message_status(message_id):
    """Get the status of a previously sent message"""
    try:
        email, error_response, status_code = validate_api_key()
        if error_response:
            return error_response, status_code
        
        # Check if message exists
        if message_id not in messages:
            return jsonify({'error': 'Message not found'}), 404
        
        message = messages[message_id]
        template_id = message['template_id']
        
        # Check if message belongs to user (through template -> service -> user)
        if template_id not in templates:
            return jsonify({'error': 'Message not found'}), 404
        
        template = templates[template_id]
        service_id = template['service_id']
        
        user_api_key = users[email]['api_key']
        if services[service_id]['user_api_key'] != user_api_key:
            return jsonify({'error': 'Message does not belong to user'}), 403
        
        # Simulate status progression
        current_time = time.time()
        sent_time = datetime.fromisoformat(message['sent_at']).timestamp()
        time_elapsed = current_time - sent_time
        
        # Update status based on time elapsed (simulate delivery)
        if message['status'] == 'pending' and time_elapsed > 5:  # 5 seconds
            message['status'] = simulate_message_delivery()
            if message['status'] in ['delivered', 'failed']:
                message['delivered_at'] = datetime.utcnow().isoformat()
        
        return jsonify({
            'message_id': message_id,
            'status': message['status'],
            'type': message['type'],
            'recipient': message['recipient'],
            'sent_at': message['sent_at'],
            'delivered_at': message.get('delivered_at')
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in get_message_status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all messages for the authenticated user"""
    try:
        email, error_response, status_code = validate_api_key()
        if error_response:
            return error_response, status_code
        
        user_api_key = users[email]['api_key']
        user_service_ids = [service_id for service_id, service in services.items() 
                           if service['user_api_key'] == user_api_key]
        
        user_template_ids = [template_id for template_id, template in templates.items() 
                            if template['service_id'] in user_service_ids]
        
        user_messages = [message for message in messages.values() 
                        if message['template_id'] in user_template_ids]
        
        return jsonify({
            'messages': user_messages
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in get_messages: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'users_count': len(users),
        'services_count': len(services),
        'templates_count': len(templates),
        'messages_count': len(messages)
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
