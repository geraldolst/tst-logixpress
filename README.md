# LOGIXPress API
Tugas Besar II3160 Teknologi Sistem Terintegrasi
Last-Mile Delivery System - **Shipment Lifecycle Management** (Core Domain)

## Deskripsi Proyek

LOGIXPress adalah platform terintegrasi untuk mengelola siklus hidup pengiriman barang dari gudang ke pelanggan akhir (last-mile delivery). Implementasi ini menggunakan prinsip **Domain-Driven Design (DDD)** dengan fokus pada Bounded Context: **Shipment Lifecycle Management**.

### Bounded Context: Shipment Lifecycle Management

Mengelola seluruh siklus hidup pengiriman, mulai dari:
- **C0101**: Shipment Order Creation
- **C0102**: Shipment Tracking & Status Update  
- **C0103**: Shipment Manifesting & Dispatch

## Arsitektur DDD

### Aggregate Root
- **Shipment**: Objek utama yang menjamin konsistensi domain. Semua operasi harus melalui Aggregate Root ini.

### Value Objects
- **ShipmentStatus**: Enum status pengiriman (placed, in_transit, out_for_delivery, delivered, returned, cancelled)
- **Recipient**: Informasi penerima (name, email, phone, address)
- **Seller**: Informasi pengirim (name, email, phone)
- **PackageDetails**: Detail paket (content, weight, dimensions, fragile)

### Internal Entity
- **TrackingEvent**: Riwayat kejadian pengiriman yang hanya dapat diakses melalui Aggregate Root

## API Endpoints

### Shipment Management
- `GET /` - Root endpoint dengan informasi API
- `GET /shipments` - List semua shipment (dengan filtering)
- `GET /shipment/{id}` - Detail shipment berdasarkan tracking number
- `POST /shipment` - Membuat shipment baru
- `PATCH /shipment/{id}` - Update shipment
- `DELETE /shipment/{id}` - Hapus shipment

### Tracking Events
- `GET /shipment/{id}/tracking` - Riwayat tracking events
- `POST /shipment/{id}/tracking` - Tambah tracking event baru

### Statistics
- `GET /stats` - Statistik shipment
- `GET /health` - Health check

### Documentation
- `GET /docs` - OpenAPI/Swagger documentation
- `GET /scalar` - Scalar API documentation

## Setup & Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd tst-logixpress
```

### 2. Buat Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Jalankan Server

Menggunakan run.py:
```bash
python run.py
```

Atau langsung dengan uvicorn:
```bash
uvicorn app.main:app --reload
```

Server akan berjalan di: `http://127.0.0.1:8000`

## Dokumentasi API

Setelah server berjalan, akses dokumentasi di:
- Swagger UI: `http://127.0.0.1:8000/docs`
- Scalar UI: `http://127.0.0.1:8000/scalar`

## Contoh Request

### Create Shipment
```json
POST /shipment
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
    "phone": "081234567890",
    "address": "Jl. Contoh No. 123, Jakarta"
  },
  "seller": {
    "name": "Tech Store",
    "email": "sales@techstore.com",
    "phone": "021-1234567"
  },
  "destination_code": 11002
}
```

### Get Shipments (with filter)
```
GET /shipments?status=in_transit&limit=5
```

### Update Shipment Status
```json
PATCH /shipment/12701
{
  "current_status": "in_transit"
}
```

### Add Tracking Event
```json
POST /shipment/12701/tracking
{
  "location": "Distribution Center Jakarta",
  "description": "Package sorted and ready for dispatch",
  "status": "in_transit"
}
```

## Teknologi yang Digunakan

- **FastAPI**: Modern web framework untuk Python
- **Pydantic**: Data validation menggunakan Python type hints
- **Scalar FastAPI**: API documentation
- **Uvicorn**: ASGI server

## Struktur Proyek

```
tst-logixpress/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & endpoints
│   └── schemas.py       # Pydantic models (DDD)
├── requirements.txt
├── run.py
└── README.md
```

## Author

**Geraldo Linggom Samuel Tampubolon**  
NIM: 18223136  
Program Studi Sistem dan Teknologi Informasi  
Institut Teknologi Bandung


