# Notification Management API

A comprehensive Flask REST API for managing notifications, templates, and delivery tracking. This system allows users to register, create services, design message templates, and send email/SMS notifications with delivery status tracking.

## Features

- **User Registration**: Sign up with email/password and receive a unique API key
- **Service Management**: Create and manage notification services
- **Template System**: Design reusable message templates with subject and body
- **Multi-Channel Notifications**: Send both email and SMS notifications
- **Delivery Tracking**: Track message status with unique message IDs
- **Interactive Documentation**: Built-in web interface for API testing
- **In-Memory Storage**: Simple dictionary-based storage for quick deployment

## API Endpoints

### Authentication
All endpoints (except signup) require an API key in the `X-API-Key` header.

### User Management
- `POST /api/signup` - Register a new user and get API key

### Services
- `POST /api/services` - Create a new service
- `GET /api/services` - Get all user services

### Templates
- `POST /api/templates` - Create a message template
- `GET /api/templates` - Get all user templates

### Notifications
- `POST /api/notifications/email` - Send email notification
- `POST /api/notifications/sms` - Send SMS notification

### Message Tracking
- `GET /api/messages/{message_id}/status` - Get message delivery status
- `GET /api/messages` - Get all user messages

### Health Check
- `GET /api/health` - System health status

## Quick Start

### Prerequisites
- Python 3.11+
- Flask and dependencies (see requirements below)

### Installation

1. **Clone or download the project**
   ```bash
   # If using git
   git clone <repository-url>
   cd notification-api
   ```

2. **Install dependencies**
   ```bash
   pip install flask gunicorn werkzeug
   ```

3. **Set environment variables**
   ```bash
   export SESSION_SECRET="your-secret-key-here"
   ```

4. **Run the application**
   ```bash
   # Development mode
   python main.py
   
   # Production mode with Gunicorn
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

5. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Use the interactive documentation and testing interface

## Usage Example

### 1. Sign Up
```bash
curl -X POST http://localhost:5000/api/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword"}'
```

Response:
```json
{
  "message": "User created successfully",
  "email": "user@example.com",
  "api_key": "your-generated-api-key"
}
```

### 2. Create a Service
```bash
curl -X POST http://localhost:5000/api/services \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"name": "My App", "description": "User notifications"}'
```

### 3. Create a Template
```bash
curl -X POST http://localhost:5000/api/templates \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "name": "Welcome Email",
    "subject": "Welcome to Our Service!",
    "body": "Hello! Welcome to our amazing service.",
    "service_id": "your-service-id"
  }'
```

### 4. Send an Email
```bash
curl -X POST http://localhost:5000/api/notifications/email \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "template_id": "your-template-id",
    "recipient_email": "recipient@example.com"
  }'
```

### 5. Check Message Status
```bash
curl -X GET http://localhost:5000/api/messages/your-message-id/status \
  -H "X-API-Key: your-api-key"
```

## Project Structure

```
notification-api/
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── templates/
│   └── index.html      # Web interface
├── static/
│   └── style.css       # Custom styles
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

## Configuration

### Environment Variables
- `SESSION_SECRET`: Flask session secret key (required for production)

### Storage
Currently uses in-memory dictionaries for data storage. In production, consider:
- PostgreSQL/MySQL for persistent storage
- Redis for session management
- External email/SMS services (Twilio, SendGrid, etc.)

## Development

### Running in Development
```bash
python main.py
```
The application runs on `http://0.0.0.0:5000` with debug mode enabled.

### Production Deployment
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

## Running with Docker

1. **Build the Docker image**
   ```bash
   docker build -t notification-api .
   ```

2. **Run the Docker container**
   ```bash
   docker run -d -p 8080:8080 -e SESSION_SECRET=your-secret notification-api
   ```

   The API will be available at [http://localhost:8080](http://localhost:8080).

## Message Status Simulation

The API simulates message delivery with these statuses:
- `pending`: Initial status when message is sent
- `sent`: Message has been processed
- `delivered`: Message successfully delivered (60% probability)
- `failed`: Delivery failed (10% probability)

Status updates occur automatically after 5 seconds from sending.

## Web Interface

Visit the root URL (`/`) to access:
- Complete API documentation
- Interactive testing interface
- Real-time response viewer
- Quick action buttons for common workflows

## Security Notes

- API keys are generated using UUID4 for uniqueness
- Passwords are hashed using Werkzeug's security functions
- Input validation on all endpoints
- Proper error handling and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly using the web interface
5. Submit a pull request

## License

This project is open source and available under the MIT License.