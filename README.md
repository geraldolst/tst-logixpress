# LOGIXPress API
Production-ready FastAPI microservice for last-mile delivery shipment lifecycle management.

## Quick Start

### Docker usage
```bash
docker compose up --build
```
- App: http://localhost:8000
- Docs: http://localhost:8000/docs
- Scalar: http://localhost:8000/scalar
- Health: http://localhost:8000/health

### Local development
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
python run.py
```
Alternative:
```bash
uvicorn app.main:app --reload --port 8000
```

## Project Structure
```
tst-logixpress/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── router.py
│   │   ├── dependencies.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── shipment.py
│   │   │   ├── tracking.py
│   │   │   └── stats.py
│   │   └── schemas/
│   │       ├── auth.py
│   │       └── shipment.py
│   ├── core/
│   │   ├── exceptions.py
│   │   └── security.py
│   ├── models/
│   │   └── shipment.py
│   └── services/
│       ├── auth.py
│       └── shipment.py
├── tests/
├── data/
├── Dockerfile
├── docker-compose.yaml
├── pyproject.toml
├── requirements.txt
└── README.md
```

## API Overview
All endpoints use JSON with JWT Bearer token authentication.

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Create new user account | No |
| POST | `/auth/login` | Login and get JWT token | No |
| GET | `/auth/me` | Get current user info | Yes |

### Shipments
| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/shipments` | List shipments (filterable) | Any authenticated |
| GET | `/shipment/{id}` | Get shipment details | Any authenticated |
| POST | `/shipment` | Create new shipment | admin, customer |
| PATCH | `/shipment/{id}` | Update shipment | admin, courier |
| DELETE | `/shipment/{id}` | Delete shipment | admin |

### Tracking
| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/shipment/{id}/tracking` | Get tracking history | Any authenticated |
| POST | `/shipment/{id}/tracking` | Add tracking event | admin, courier |

### Statistics
| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/stats` | Get shipment statistics | admin |
| GET | `/health` | Health check | None |

## Shipment Status Workflow
Shipment lifecycle:

**PLACED** → **IN_TRANSIT** → **OUT_FOR_DELIVERY** → **DELIVERED**

Alternative paths:
- Any status → **CANCELLED**
- IN_TRANSIT/OUT_FOR_DELIVERY → **RETURNED**

### Status Transitions
- `placed`: Initial status when shipment is created
- `in_transit`: Package in transit to destination
- `out_for_delivery`: Package out for delivery to recipient
- `delivered`: Successfully delivered (terminal state)
- `returned`: Package returned to sender (terminal state)
- `cancelled`: Shipment cancelled (terminal state)

**Rules:**
- Only forward transitions allowed (except cancel/return)
- Delivered shipments are immutable
- Status changes automatically create tracking events

## Default Users
| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Admin | `admin` | `admin123` | Full access (all operations) |
| Courier | `courier` | `courier123` | Update status, add tracking |
| Customer | `customer` | `customer123` | Create shipments, view own data |

## Example Payloads

### Register User
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123",
  "role": "customer"
}
```

### Login
```json
{
  "username": "admin",
  "password": "admin123"
}
```

### Create Shipment
```json
{
  "package_details": {
    "content": "Electronic Components",
    "weight": 5.5,
    "dimensions": "30x20x15",
    "fragile": true
  },
  "recipient": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+6281234567890",
    "address": "Jl. Sudirman No. 123, Jakarta Pusat"
  },
  "seller": {
    "name": "Tech Store",
    "email": "sales@techstore.com",
    "phone": "+6281234567891"
  },
  "destination_code": 11002
}
```

### Update Shipment Status
```json
{
  "current_status": "in_transit"
}
```

### Add Tracking Event
```json
{
  "location": "Distribution Center Jakarta",
  "description": "Package sorted and ready for dispatch",
  "status": "in_transit"
}
```

### Get Shipments (with filters)
Query Parameters:
- `status`: Filter by status (placed, in_transit, etc.)
- `destination_code`: Filter by destination
- `limit`: Max results (default: 10, max: 100)

Example: `GET /shipments?status=in_transit&limit=20`

## Example Responses

### Single Shipment Response
```json
{
  "id": 12701,
  "package_details": {
    "content": "Electronic Components",
    "weight": 5.5,
    "dimensions": "30x20x15",
    "fragile": true
  },
  "recipient": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+6281234567890",
    "address": "Jl. Sudirman No. 123, Jakarta Pusat"
  },
  "seller": {
    "name": "Tech Store",
    "email": "sales@techstore.com",
    "phone": "+6281234567891"
  },
  "destination_code": 11002,
  "current_status": "placed",
  "tracking_events": [
    {
      "id": 1,
      "location": "Warehouse",
      "description": "Shipment order created and received at warehouse",
      "status": "placed",
      "timestamp": "2024-12-01T09:00:00"
    }
  ],
  "created_at": "2024-12-01T09:00:00",
  "updated_at": "2024-12-01T09:00:00"
}
```

### Shipment List Response
```json
[
  {
    "id": 12701,
    "content": "Electronic Components",
    "weight": 5.5,
    "current_status": "placed",
    "destination_code": 11002,
    "recipient_name": "John Doe",
    "created_at": "2024-12-01T09:00:00"
  },
  {
    "id": 12702,
    "content": "Steel Rods",
    "weight": 14.7,
    "current_status": "in_transit",
    "destination_code": 11003,
    "recipient_name": "Jane Smith",
    "created_at": "2024-12-01T08:00:00"
  }
]
```

### Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Model Fields

### ShipmentCreate
- `package_details`: PackageDetails object
- `recipient`: Recipient object
- `seller`: Seller object
- `destination_code`: int

### PackageDetails
- `content`: str (required)
- `weight`: float (required, max 25kg)
- `dimensions`: str | None
- `fragile`: bool (default: false)

### Recipient
- `name`: str (required)
- `email`: EmailStr (required)
- `phone`: str (required)
- `address`: str (required)

### Seller
- `name`: str (required)
- `email`: EmailStr (required)
- `phone`: str (required)

### ShipmentRead
- `id`: int (tracking number)
- `package_details`: PackageDetails
- `recipient`: Recipient
- `seller`: Seller
- `destination_code`: int
- `current_status`: ShipmentStatus
- `tracking_events`: list[TrackingEvent]
- `created_at`: datetime
- `updated_at`: datetime

### TrackingEvent
- `id`: int
- `location`: str
- `description`: str
- `status`: ShipmentStatus
- `timestamp`: datetime

## Role Permissions
All write operations require authentication and proper role:

- **Admin**: Full access to all operations
- **Courier**: Can update shipment status and add tracking events
- **Customer**: Can create shipments and view own data
- **All authenticated**: Can view shipments and tracking

## Error Handling
- `400`: Bad request or validation error
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not found
- `422`: Validation error (Pydantic)
- `500`: Internal server error

## Testing
```bash
# Run with curl
curl http://localhost:8000/health

# Login and get token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer <your-token>" \
  http://localhost:8000/shipments
```

## Docker Usage
```bash
# Build and run
docker compose up --build

# Run in background
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down

# Rebuild
docker compose build --no-cache
```

**Endpoints:**
- App: http://localhost:8000
- Docs: http://localhost:8000/docs
- Scalar: http://localhost:8000/scalar
- Health: http://localhost:8000/health

## Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server with auto-reload
python run.py
# or
uvicorn app.main:app --reload --port 8000

# Check code (if dev tools installed)
black app/ tests/           # Format
ruff check app/ tests/      # Lint
mypy app/                   # Type check
```

## Architecture
**Domain-Driven Design (DDD)** with modular structure:

- **API Layer** (`app/api/`): FastAPI routers, dependencies, schemas
- **Core Layer** (`app/core/`): Security, exceptions, utilities
- **Domain Layer** (`app/models/`): Domain models and business rules
- **Service Layer** (`app/services/`): Business logic and operations
- **Configuration** (`app/config.py`): Centralized settings

**Benefits:**
- Clean separation of concerns
- Easy to test and maintain
- Scalable architecture
- Following FastAPI best practices

---

**Author**: Geraldo Linggom Samuel Tampubolon (18223136)  
**Course**: TST (Teknologi Sistem Terintegrasi) - ITB  
**Repository**: https://github.com/geraldolst/tst-logixpress