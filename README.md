# Admin Server API

A FastAPI-based administrative server for managing users, clients, tickets, packages, and subscriptions. This application provides a comprehensive admin interface with authentication, user management, customer management, ticket system, and package/subscription management.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database Configuration](#database-configuration)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)

## Overview

The Admin Server is a RESTful API service built with FastAPI that provides administrative functionality for managing:

- **Admin Users**: User authentication, creation, updates, and management
- **Clients/Customers**: Customer information, subscriptions, and settings
- **Tickets**: Support ticket creation, tracking, and updates
- **Packages**: Subscription package management
- **Updates**: Tracking and sending updates to client devices

## Architecture

The application follows a modular architecture with clear separation of concerns, similar to the apiServer project:

- **Core Module** (`core/`): Centralized configuration, database setup, security, and logging
- **API Layer** (`app/`): FastAPI routers handling HTTP requests
- **Data Access Layer** (`database/`): SQLAlchemy ORM models and session management
- **Schema Layer** (`schema/`): Pydantic models for request/response validation
- **Middleware** (`middleware/`): Centralized error handling and request processing

### Database Architecture

The application uses **two separate MySQL databases**:

1. **POS Database** (`pos`): Contains client/customer data
   - BusinessDetails
   - Customers
   - BusinessSettings
   - BusinessSubscription

2. **Admin Database** (`posAdmin`): Contains administrative data
   - AdminUsers
   - client_tickets
   - client_ticket_updates
   - packages
   - TrackUpdates

## Technology Stack

- **Framework**: FastAPI 0.x
- **Database**: MySQL (via PyMySQL)
- **ORM**: SQLAlchemy
- **Authentication**: OAuth2 with token-based authentication
- **Password Hashing**: bcrypt
- **HTTP Client**: httpx (for external API calls)
- **Containerization**: Docker
- **Cloud Deployment**: AWS ECS (Fargate)

## Project Structure

```
adminServer/
├── app/                    # Application logic and API routes
│   ├── user_login.py      # User authentication endpoints
│   ├── user_crud.py       # User CRUD operations
│   ├── clients.py         # Client/customer management
│   ├── tickets.py         # Ticket management
│   └── packages.py        # Package management
├── core/                   # Core application modules
│   ├── __init__.py        # Core module exports
│   ├── config.py          # Application configuration and settings
│   ├── database.py        # Database engine and base setup
│   ├── security.py        # Authentication and security utilities
│   └── logging.py         # Logging configuration
├── database/              # Database models and session management
│   ├── session.py        # Database session management
│   ├── db_users.py       # User model
│   ├── db_customer.py    # Client/customer models
│   ├── db_tickets.py     # Ticket model
│   ├── db_ticket_updates.py  # Ticket update model
│   ├── db_packages.py    # Package model
│   ├── db_updates.py     # Update tracking model
│   └── db_transactions.py # Transaction model (abstract)
├── middleware/            # Middleware components
│   └── error_handler.py  # Centralized error handling
├── schema/               # Pydantic schemas for validation
│   ├── s_users.py        # User schemas
│   ├── s_client.py       # Client schemas
│   ├── s_client_list_base.py  # Client list schemas
│   ├── s_client_update.py     # Client update schemas
│   ├── s_tickets.py      # Ticket schemas
│   ├── s_ticket_updates.py    # Ticket update schemas
│   ├── s_packages.py     # Package schemas
│   └── s_transactions.py # Transaction schemas
├── docker/               # Docker configuration files
│   ├── Dockerfile        # Docker image configuration
│   └── compose.yaml      # Docker Compose configuration
├── utils/                # Utility files and deployment configs
│   ├── send_updates.py   # External update service integration
│   ├── ecs-task-template.json  # AWS ECS task definition
│   └── README.Docker.md  # Docker deployment documentation
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Database Configuration

The application connects to two MySQL databases hosted on AWS RDS:

- **Host**: `shopos-db.cj8uqe0gmqvq.ap-south-1.rds.amazonaws.com`
- **Username**: `admin`
- **Databases**: `pos` (application data) and `posAdmin` (admin data)

**Note**: Database credentials are configured in `core/config.py` using environment variables. For production, set these via environment variables or `.env` file.

## API Documentation

### Swagger UI (Interactive Documentation)

The API includes **automatic interactive documentation** powered by Swagger/OpenAPI:

- **Swagger UI**: Available at `http://localhost:80/docs` (or your server URL + `/docs`)
- **ReDoc**: Available at `http://localhost:80/redoc` (alternative documentation format)

#### Using Swagger UI for Authentication

1. **Get Your Credentials**:
   - Use the `/admin-api/login/admin_login` endpoint to authenticate
   - You'll receive a `user_id` and `token` in the response

2. **Set Global Authentication**:
   - Click the **"Authorize"** button (🔒) at the top right of Swagger UI
   - You'll see two fields:
     - **Bearer**: Enter your token (just the token value, without "Bearer " prefix)
     - **UserId**: Enter your user_id (integer)
   - Click "Authorize" to save both values

3. **Using the APIs**:
   - Both `token` and `user_id` will be automatically included in all API requests
   - The token is sent in the `Authorization: Bearer <token>` header
   - The user_id is sent in the `X-User-Id: <user_id>` header
   - All endpoints are documented with request/response schemas
   - You can test endpoints directly from Swagger UI
   - (Optional) You can still provide `user_id` as a query parameter for backward compatibility

#### Features

- **Interactive Testing**: Test all endpoints directly from the browser
- **Request/Response Schemas**: See exact data structures for all endpoints
- **Authentication**: Global token authentication via the Authorize button
- **Try It Out**: Execute API calls and see responses in real-time

### API Endpoints Overview

The API is organized into the following modules:

#### Authentication
- `POST /admin-api/login/admin_login` - Authenticate and get user credentials

#### User Management (`/admin-api/user`)
- `POST /create_user` - Create a new admin user
- `PUT /update_user` - Update user information
- `DELETE /delete_user` - Soft delete a user
- `GET /get_users` - Get all users

#### Client Management (`/admin-api/customers`)
- `GET /get_all_clients` - Get list of all clients
- `GET /get_specific_client` - Get detailed client information
- `POST /update_client_subscription` - Update client subscription settings

#### Ticket Management (`/admin-api/tickets`)
- `POST /create_ticket` - Create a new support ticket
- `GET /get_all_opened_ticket` - Get all open tickets
- `GET /get_client_tickets` - Get tickets for a specific client
- `GET /get_ticket_updates` - Get updates for a ticket
- `POST /create_update` - Add an update to a ticket
- `PUT /update_ticket_status` - Update ticket status and priority

#### Package Management (`/admin-api/packages`)
- `POST /create_package` - Create a new subscription package
- `GET /get_packages` - Get all packages
- `DELETE /delete_package` - Soft delete a package

**For complete API documentation with request/response examples, please visit the Swagger UI at `/docs` when the server is running.**

## Authentication

The application uses **token-based authentication** with the following requirements:

1. **user_id**: User ID of the authenticated user
   - Can be provided as a header: `X-User-Id: 1` (recommended for Swagger UI)
   - Can be provided as a query parameter: `?user_id=1` (for Postman/other clients)
   
2. **token**: Authentication token
   - Must be provided in the Authorization header: `Authorization: Bearer <token>`
   - In Swagger UI, use the "Authorize" button to set this globally

### Authentication Flow

1. **Login**: Use `/admin-api/login/admin_login` with email and password
2. **Get Credentials**: Receive `user_id` and `token` in the response
3. **Using Swagger UI**: 
   - Click "Authorize" button
   - Enter your token in "Bearer" field (without "Bearer " prefix)
   - Enter your user_id in "UserId" field
   - Click "Authorize" - both will be automatically included in all requests
4. **Using Postman or Other Clients**:
   - Add `Authorization: Bearer <token>` header
   - Add `X-User-Id: <user_id>` header (recommended)
   - OR add `?user_id=<user_id>` as a query parameter (alternative)

### Token Generation

Tokens are generated using `secrets.token_hex(16)` when a user is created. Each user has a unique token stored in the database.

### User Verification

The `verify_user()` function in `core/security.py` checks:
- User exists in the database
- User's token matches the provided token
- User is active (`is_active = 1`)

### Global Authentication Dependency

The application uses authentication utilities from `core/security.py`:
- `get_user_id()`: Accepts `user_id` from header (X-User-Id) or query parameter (header takes precedence)
- `get_bearer_token()`: Extracts token from Authorization Bearer header
- `verify_user()`: Validates user credentials
- Can be reused across all endpoints using `Depends()`

## Installation

### Prerequisites

- Python 3.9.6
- MySQL database access
- Docker (optional, for containerized deployment)

### Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd adminServer
```

2. Create a virtual environment:
```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure database connection in `core/config.py` (or use environment variables via `.env` file)

5. Run the application:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Running the Application

### Using Docker Compose

```bash
docker compose -f docker/compose.yaml up --build
```

The application will be available at `http://localhost:80`

### Using Docker

```bash
docker build -f docker/Dockerfile -t admin-server .
docker run -p 80:80 admin-server
```

### Direct Python Execution

```bash
uvicorn main:app --host 0.0.0.0 --port 80
```

## Deployment

### AWS ECS Deployment

The project includes an ECS task definition template (`ecs-task-template.json`) for deployment to AWS ECS Fargate.

**Container Configuration:**
- **Image**: `314146310240.dkr.ecr.ap-south-1.amazonaws.com/admin-api-server:latest`
- **CPU**: 256 units
- **Memory**: 512 MB
- **Port**: 80
- **Logging**: AWS CloudWatch Logs

### Building for Production

For cross-platform builds (e.g., Mac M1 to AMD64):

```bash
docker build --platform=linux/amd64 -f docker/Dockerfile -t admin-server .
```

### Pushing to Registry

```bash
docker tag admin-server <registry>/admin-server:latest
docker push <registry>/admin-server:latest
```

## Environment Variables

**Note**: Currently, database credentials are hardcoded. For production, consider using environment variables:

```python
# Recommended approach
import os
username = os.getenv('DB_USERNAME', 'admin')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
```

## Data Models

### User Model (AdminUsers)
- `user_id`: Primary key
- `user_name`: User's name
- `email`: Unique email address
- `password`: Bcrypt hashed password
- `is_active`: Active status (1=active, 0=inactive)
- `created_at`: Creation timestamp
- `created_by`: ID of user who created this account
- `permissions`: JSON array of permission IDs
- `token`: Authentication token

### Client Models

#### Client (BusinessDetails)
- `account_id`: Primary key
- `business_name`: Business name
- `manager`: Manager name
- `phone`: Contact phone number
- `street1`, `street2`: Address fields
- `address`, `state`, `country_code`, `postcode`: Location fields
- `industry_type`: Industry classification
- `onboarded_by`: Onboarding user
- `onboarded_date`: Onboarding timestamp

#### ClientMain (Customers)
- `account_id`: Primary key
- `account_status`: Account status
- `business_email`: Unique business email
- `password`: Account password
- `account_token`: Account authentication token
- `web_token`: Web authentication token

#### ClientSettings (BusinessSettings)
- `account_id`: Primary key
- `inventory`: Inventory feature flag
- `web_settings`: Web settings flag
- `unit_pricing`: Unit pricing flag
- `use_barcode`: Barcode usage flag
- `admin_pin`: Admin PIN
- `admin_pin_modules`: JSON array of PIN-protected modules

#### ClientSubscription (BusinessSubscription)
- `account_id`: Primary key
- `subscribed`: Subscription status
- `active_modules`: JSON array of active module IDs
- `device_limit`: Maximum number of devices
- `package_id`: Associated package ID
- `additional_devices`: Additional device count
- `chargeAmount`: Additional charges
- `additional_modules`: JSON array of additional module IDs

### Ticket Model (client_tickets)
- `ticket_id`: Primary key
- `account_id`: Associated client account
- `user_id`: User who created the ticket
- `subject`: Ticket subject
- `description`: Ticket description
- `status`: Status (1=open, 2=under review, 3=closed)
- `priority`: Priority (1=low, 2=medium, 3=high)
- `created_at`: Creation timestamp
- `contact_mode`: Contact method (1=email, 2=phone, 3=chat)
- `clinet_name`: Client name (note: typo in column name)
- `client_phone`: Client phone number
- `clinet_email`: Client email (note: typo in column name)
- `attachment`: Attachment reference
- `notes`: Additional notes

### TicketUpdate Model (client_ticket_updates)
- `update_id`: Primary key
- `ticket_id`: Associated ticket ID
- `user_id`: User who created the update
- `description`: Update description
- `attachment`: Attachment reference
- `created_at`: Creation timestamp
- `contact_mode`: Contact method
- `notes`: Additional notes

### Package Model (packages)
- `id`: Primary key
- `name`: Package name
- `active_modules`: JSON array of module IDs
- `device_limit`: Device limit for the package
- `status`: Status (1=active, 0=inactive)
- `notes`: Package notes
- `price`: Package price
- `created_at`: Creation timestamp
- `created_by`: User who created the package

### TrackUpdate Model (TrackUpdates)
- `id`: Primary key
- `update_data`: JSON data of the update
- `updated_at`: Update timestamp
- `updated_by`: User who made the update
- `account_id`: Associated client account

## External Integrations

### Update Service

The application integrates with an external update service (`https://updates.gritticon.com/api/update/send_update`) to notify client devices of subscription changes.

**Function**: `send_device1_update()` in `utils/send_updates.py`

**Parameters:**
- `account_id`: Client account ID
- `OID`: Operation ID (default: 60)
- `message`: Update data dictionary
- `notify`: Notification flag (default: False)

## Security Considerations

1. **Password Hashing**: All passwords are hashed using bcrypt before storage
2. **Token Authentication**: OAuth2 token-based authentication for API access
3. **CORS**: Currently configured to allow all origins (`*`). For production, restrict to specific domains
4. **Database Credentials**: Should be moved to environment variables or secrets management
5. **Input Validation**: Pydantic schemas validate all request/response data

## Error Handling

The application uses HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors, duplicate entries)
- `401`: Unauthorized (invalid credentials, missing token)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

## Logging

Currently, the application uses default FastAPI logging. For production, consider:
- Structured logging (JSON format)
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Log aggregation (CloudWatch, ELK, etc.)

## Future Improvements

1. **Environment Variables**: Move database credentials to environment variables
2. **CORS Configuration**: Restrict CORS to specific domains
3. **Logging**: Implement structured logging
4. **Testing**: Add unit and integration tests
5. **API Documentation**: Enable FastAPI automatic documentation at `/docs`
6. **Rate Limiting**: Implement rate limiting for API endpoints
7. **Caching**: Add caching for frequently accessed data
8. **Pagination**: Add pagination for list endpoints
9. **Search/Filtering**: Add search and filtering capabilities
10. **Audit Logging**: Enhanced audit trail for all operations

## License

[Specify license here]

## Contact

[Add contact information or support details]

