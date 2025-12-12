# 📘 LOGIXPress API - Complete Testing Guide

**Panduan Lengkap Testing API dengan Detail Request, Response, dan Ekspektasi**

---

## 📋 Daftar Isi
1. [Setup & Persiapan](#setup--persiapan)
2. [Authentication Endpoints](#1️⃣-authentication-endpoints)
3. [Shipment Management Endpoints](#2️⃣-shipment-management-endpoints)
4. [Tracking Endpoints](#3️⃣-tracking-endpoints)
5. [Statistics & Health Endpoints](#4️⃣-statistics--health-endpoints)
6. [Testing Scenarios](#5️⃣-testing-scenarios)
7. [Error Handling](#6️⃣-error-handling)

---

## Setup & Persiapan

### 1. Start Server
```bash
# Pastikan di dalam virtual environment
python run.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Application startup complete.
```

### 2. Akses Dokumentasi
- Swagger UI: http://127.0.0.1:8000/docs
- Scalar UI: http://127.0.0.1:8000/scalar

### 3. Tools yang Bisa Digunakan
- ✅ Swagger UI (Recommended untuk pemula)
- ✅ cURL (Terminal)
- ✅ Postman
- ✅ Python requests
- ✅ HTTPie

---

## 1️⃣ AUTHENTICATION ENDPOINTS

### 🔐 A. Sign Up / Register User

**Endpoint:** `POST /auth/register`

**Tujuan:** Membuat akun user baru dalam sistem

**Authorization:** ❌ Tidak perlu (Public endpoint)

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "password": "securepass123",
  "role": "customer"
}
```

**Field Descriptions:**
| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| username | string | ✅ Yes | Username unik untuk login | Harus unik, belum terdaftar |
| email | string | ✅ Yes | Email address | Format email valid, harus unik |
| password | string | ✅ Yes | Password untuk login | Minimal 6 karakter |
| role | string | ❌ No | Role user | `customer` (default), `courier`, atau `admin` |

#### Response

**Success (201 Created):**
```json
{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "role": "customer",
  "message": "User 'john_doe' registered successfully with role 'customer'"
}
```

**Error - Username Already Exists (400):**
```json
{
  "detail": "Username already registered"
}
```

**Error - Email Already Exists (400):**
```json
{
  "detail": "Email already registered"
}
```

**Error - Password Too Short (400):**
```json
{
  "detail": "Password must be at least 6 characters long"
}
```

**Error - Invalid Email Format (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

#### Testing dengan cURL
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john.doe@example.com",
    "password": "securepass123",
    "role": "customer"
  }'
```

#### Ekspektasi
✅ User baru berhasil dibuat
✅ Data user tersimpan di database
✅ Password di-hash dengan bcrypt
✅ User bisa langsung login setelah register

---

### 🔑 B. Login

**Endpoint:** `POST /auth/login`

**Tujuan:** Autentikasi user dan mendapatkan JWT access token

**Authorization:** ❌ Tidak perlu (Public endpoint)

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "username": "john_doe",
  "password": "securepass123"
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | ✅ Yes | Username yang sudah terdaftar |
| password | string | ✅ Yes | Password user |

#### Response

**Success (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsInJvbGUiOiJjdXN0b21lciIsImV4cCI6MTcwMTQzMDgwMH0.xyz...",
  "token_type": "bearer"
}
```

**Response Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| access_token | string | JWT token untuk autentikasi (berlaku 30 menit) |
| token_type | string | Tipe token (selalu "bearer") |

**Error - Wrong Username/Password (401):**
```json
{
  "detail": "Incorrect username or password"
}
```

#### Testing dengan cURL
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepass123"
  }'
```

#### Ekspektasi
✅ Mendapat JWT token yang valid
✅ Token berlaku selama 30 menit
✅ Token berisi informasi: username dan role
✅ Token digunakan untuk semua protected endpoints

**⚠️ PENTING:** Simpan `access_token` untuk digunakan di request selanjutnya!

---

### 👤 C. Get Current User Info

**Endpoint:** `GET /auth/me`

**Tujuan:** Mendapatkan informasi user yang sedang login

**Authorization:** ✅ Required (JWT Token)

#### Request

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Body:** ❌ Tidak ada (GET request)

#### Response

**Success (200 OK):**
```json
{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "role": "customer",
  "disabled": false
}
```

**Response Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| username | string | Username user |
| email | string | Email address user |
| role | string | Role user (customer/courier/admin) |
| disabled | boolean | Status aktif user (false = aktif) |

**Error - No Token (401):**
```json
{
  "detail": "Not authenticated"
}
```

**Error - Invalid Token (401):**
```json
{
  "detail": "Could not validate credentials"
}
```

#### Testing dengan cURL
```bash
# Ganti <TOKEN> dengan token dari login
curl -X GET "http://127.0.0.1:8000/auth/me" \
  -H "Authorization: Bearer <TOKEN>"
```

#### Ekspektasi
✅ Mendapat informasi user yang sedang login
✅ Data sesuai dengan user yang melakukan login
✅ Bisa digunakan untuk verifikasi token masih valid

---

## 2️⃣ SHIPMENT MANAGEMENT ENDPOINTS

### 📦 A. Get All Shipments (List)

**Endpoint:** `GET /shipments`

**Tujuan:** Mengambil daftar shipment dengan opsi filtering

**Authorization:** ✅ Required (JWT Token)

**Role Access:** Admin (all), Courier (assigned), Customer (own)

#### Request

**Headers:**
```
Authorization: Bearer <TOKEN>
```

**Query Parameters:**
| Parameter | Type | Required | Description | Default | Valid Values |
|-----------|------|----------|-------------|---------|--------------|
| status | string | ❌ No | Filter by status | - | placed, in_transit, out_for_delivery, delivered, returned, cancelled |
| destination_code | integer | ❌ No | Filter by destination | - | Any integer |
| limit | integer | ❌ No | Max results | 10 | 1-100 |

**Body:** ❌ Tidak ada (GET request)

#### Response

**Success (200 OK):**
```json
[
  {
    "id": 12701,
    "content": "aluminum sheets",
    "weight": 8.2,
    "current_status": "placed",
    "destination_code": 11002,
    "recipient_name": "Ahmad Suryadi",
    "created_at": "2024-12-01T09:00:00"
  },
  {
    "id": 12702,
    "content": "steel rods",
    "weight": 14.7,
    "current_status": "in_transit",
    "destination_code": 11003,
    "recipient_name": "Budi Santoso",
    "created_at": "2024-12-01T10:00:00"
  }
]
```

**Response Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Tracking number / Shipment ID |
| content | string | Deskripsi isi paket |
| weight | float | Berat paket (kg) |
| current_status | string | Status pengiriman saat ini |
| destination_code | integer | Kode tujuan pengiriman |
| recipient_name | string | Nama penerima |
| created_at | datetime | Waktu pembuatan shipment |

**Empty Result (200 OK):**
```json
[]
```

#### Testing dengan cURL

**Get All (No Filter):**
```bash
curl -X GET "http://127.0.0.1:8000/shipments" \
  -H "Authorization: Bearer <TOKEN>"
```

**Filter by Status:**
```bash
curl -X GET "http://127.0.0.1:8000/shipments?status=placed" \
  -H "Authorization: Bearer <TOKEN>"
```

**Filter by Destination:**
```bash
curl -X GET "http://127.0.0.1:8000/shipments?destination_code=11002" \
  -H "Authorization: Bearer <TOKEN>"
```

**Multiple Filters:**
```bash
curl -X GET "http://127.0.0.1:8000/shipments?status=in_transit&limit=5" \
  -H "Authorization: Bearer <TOKEN>"
```

#### Ekspektasi
✅ Admin: Melihat SEMUA shipments
✅ Courier: Melihat shipments yang assigned
✅ Customer: Melihat shipments milik sendiri
✅ Filter berfungsi sesuai parameter
✅ Limit membatasi jumlah hasil maksimal

---

### 📋 B. Get Shipment by ID (Detail)

**Endpoint:** `GET /shipment/{shipment_id}`

**Tujuan:** Mengambil detail lengkap shipment berdasarkan tracking number

**Authorization:** ✅ Required (JWT Token)

**Role Access:** Admin (any), Courier (assigned), Customer (own)

#### Request

**Headers:**
```
Authorization: Bearer <TOKEN>
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| shipment_id | integer | ✅ Yes | Tracking number shipment |

**Body:** ❌ Tidak ada (GET request)

#### Response

**Success (200 OK):**
```json
{
  "id": 12701,
  "package_details": {
    "content": "aluminum sheets",
    "weight": 8.2,
    "dimensions": "50x30x10",
    "fragile": false
  },
  "recipient": {
    "name": "Ahmad Suryadi",
    "email": "ahmad@example.com",
    "phone": "081234567890",
    "address": "Jl. Sudirman No. 123, Jakarta Pusat"
  },
  "seller": {
    "name": "Metal Supplies Co.",
    "email": "sales@metalsupplies.com",
    "phone": "021-5551234"
  },
  "destination_code": 11002,
  "current_status": "placed",
  "tracking_events": [
    {
      "id": 1,
      "location": "Warehouse Jakarta",
      "description": "Package received at warehouse",
      "status": "placed",
      "timestamp": "2024-12-01T09:00:00"
    }
  ],
  "created_at": "2024-12-01T09:00:00",
  "updated_at": "2024-12-01T09:00:00"
}
```

**Error - Not Found (404):**
```json
{
  "detail": "Shipment with tracking number 99999 not found"
}
```

**Error - Forbidden (403):**
```json
{
  "detail": "Not enough permissions"
}
```

#### Testing dengan cURL
```bash
curl -X GET "http://127.0.0.1:8000/shipment/12701" \
  -H "Authorization: Bearer <TOKEN>"
```

#### Ekspektasi
✅ Mendapat detail lengkap shipment (Aggregate Root)
✅ Termasuk semua Value Objects (PackageDetails, Recipient, Seller)
✅ Termasuk tracking events history
✅ Customer hanya bisa lihat shipment miliknya
✅ Admin bisa lihat semua shipment

---

### ➕ C. Create Shipment

**Endpoint:** `POST /shipment`

**Tujuan:** Membuat shipment baru dalam sistem

**Authorization:** ✅ Required (JWT Token)

**Role Access:** ✅ Admin, ✅ Customer, ❌ Courier

#### Request

**Headers:**
```
Authorization: Bearer <TOKEN>
Content-Type: application/json
```

**Body (JSON):**
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
    "address": "Jl. Sudirman No. 123, Jakarta Pusat, DKI Jakarta 10220"
  },
  "seller": {
    "name": "Toko Electronics ABC",
    "email": "sales@tokoabc.com",
    "phone": "+6281234567891"
  },
  "destination_code": 11002
}
```

**Field Descriptions:**

**package_details:**
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| content | string | ✅ Yes | min_length=1 | Deskripsi isi paket |
| weight | float | ✅ Yes | > 0, ≤ 25 | Berat paket (kg), max 25kg |
| dimensions | string | ❌ No | - | Dimensi paket (PxLxT cm) |
| fragile | boolean | ❌ No | default=false | Apakah barang mudah pecah |

**recipient:**
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| name | string | ✅ Yes | min_length=1 | Nama penerima |
| email | string | ✅ Yes | valid email | Email penerima |
| phone | string | ✅ Yes | - | Nomor telepon |
| address | string | ✅ Yes | - | Alamat lengkap |

**seller:**
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| name | string | ✅ Yes | - | Nama seller/pengirim |
| email | string | ✅ Yes | valid email | Email seller |
| phone | string | ✅ Yes | - | Nomor telepon seller |

**destination_code:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| destination_code | integer | ✅ Yes | Kode tujuan pengiriman |

#### Response

**Success (201 Created):**
```json
{
  "tracking_number": 12706
}
```

**Error - Weight Exceeds Maximum (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "package_details", "weight"],
      "msg": "ensure this value is less than or equal to 25",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**Error - Invalid Email (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "recipient", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Error - Forbidden for Courier (403):**
```json
{
  "detail": "Access denied. Required roles: admin, customer"
}
```

#### Testing dengan cURL
```bash
curl -X POST "http://127.0.0.1:8000/shipment" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
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
      "address": "Jl. Sudirman No. 123, Jakarta"
    },
    "seller": {
      "name": "Toko ABC",
      "email": "sales@tokoabc.com",
      "phone": "+6281234567891"
    },
    "destination_code": 11002
  }'
```

#### Ekspektasi
✅ Shipment baru berhasil dibuat
✅ Mendapat tracking number unik
✅ Status awal: "placed"
✅ Tracking event pertama otomatis dibuat
✅ Customer bisa create untuk dirinya
✅ Admin bisa create untuk siapapun
✅ Courier TIDAK bisa create shipment

---

### ✏️ D. Update Shipment

**Endpoint:** `PATCH /shipment/{shipment_id}`

**Tujuan:** Mengupdate data shipment (partial update)

**Authorization:** ✅ Required (JWT Token)

**Role Access:** 
- Admin: Semua field
- Courier: Status & tracking only
- Customer: Package details (before shipped)

#### Request

**Headers:**
```
Authorization: Bearer <TOKEN>
Content-Type: application/json
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| shipment_id | integer | ✅ Yes | Tracking number shipment |

**Body (JSON) - Semua field opsional:**

**Update Status (Admin/Courier):**
```json
{
  "current_status": "in_transit"
}
```

**Update Package Details (Admin/Customer):**
```json
{
  "package_details": {
    "content": "Updated Electronic Components",
    "weight": 6.0,
    "dimensions": "35x25x20",
    "fragile": true
  }
}
```

**Update Recipient (Admin):**
```json
{
  "recipient": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "+6281234567899",
    "address": "Jl. New Address No. 456"
  }
}
```

**Update Destination (Admin):**
```json
{
  "destination_code": 11005
}
```

**Multiple Fields (Admin):**
```json
{
  "current_status": "out_for_delivery",
  "package_details": {
    "content": "Updated content",
    "weight": 5.8,
    "fragile": false
  }
}
```

#### Response

**Success (200 OK):**
```json
{
  "id": 12701,
  "package_details": {
    "content": "Updated Electronic Components",
    "weight": 6.0,
    "dimensions": "35x25x20",
    "fragile": true
  },
  "recipient": {
    "name": "Ahmad Suryadi",
    "email": "ahmad@example.com",
    "phone": "081234567890",
    "address": "Jl. Sudirman No. 123, Jakarta Pusat"
  },
  "seller": {
    "name": "Metal Supplies Co.",
    "email": "sales@metalsupplies.com",
    "phone": "021-5551234"
  },
  "destination_code": 11002,
  "current_status": "in_transit",
  "tracking_events": [...],
  "created_at": "2024-12-01T09:00:00",
  "updated_at": "2024-12-01T15:30:00"
}
```

**Error - Invalid Status Transition (400):**
```json
{
  "detail": "Invalid status transition from 'placed' to 'delivered'. Valid next status: in_transit"
}
```

**Valid Status Transitions:**
- `placed` → `in_transit`
- `in_transit` → `out_for_delivery`
- `out_for_delivery` → `delivered`
- Any status → `returned` atau `cancelled`

**Error - Not Found (404):**
```json
{
  "detail": "Shipment with id 99999 not found"
}
```

**Error - Forbidden (403):**
```json
{
  "detail": "Not enough permissions"
}
```

#### Testing dengan cURL

**Update Status:**
```bash
curl -X PATCH "http://127.0.0.1:8000/shipment/12701" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"current_status": "in_transit"}'
```

**Update Package Details:**
```bash
curl -X PATCH "http://127.0.0.1:8000/shipment/12701" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "package_details": {
      "content": "Updated content",
      "weight": 6.0,
      "fragile": false
    }
  }'
```

#### Ekspektasi
✅ Field yang diupdate berubah
✅ Field yang tidak disebutkan tetap sama
✅ Validasi status transition berlaku
✅ `updated_at` diupdate otomatis
✅ Role permissions diterapkan dengan benar

---

### 🗑️ E. Delete Shipment

**Endpoint:** `DELETE /shipment/{shipment_id}`

**Tujuan:** Menghapus shipment dari sistem

**Authorization:** ✅ Required (JWT Token)

**Role Access:** ✅ Admin only, ❌ Courier, ❌ Customer

#### Request

**Headers:**
```
Authorization: Bearer <TOKEN>
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| shipment_id | integer | ✅ Yes | Tracking number shipment |

**Body:** ❌ Tidak ada (DELETE request)

#### Response

**Success (200 OK):**
```json
{
  "message": "Shipment 12701 deleted successfully"
}
```

**Error - Not Found (404):**
```json
{
  "detail": "Shipment with id 99999 not found"
}
```

**Error - Forbidden (403):**
```json
{
  "detail": "Access denied. Required roles: admin"
}
```

#### Testing dengan cURL
```bash
curl -X DELETE "http://127.0.0.1:8000/shipment/12701" \
  -H "Authorization: Bearer <TOKEN>"
```

#### Ekspektasi
✅ Shipment dihapus dari database
✅ Hanya Admin yang bisa delete
✅ Courier dan Customer akan mendapat error 403
✅ Shipment yang tidak ada akan error 404

---

## 3️⃣ TRACKING ENDPOINTS

### 📍 A. Get Tracking History

**Endpoint:** `GET /shipment/{shipment_id}/tracking`

**Tujuan:** Mengambil riwayat tracking events dari shipment

**Authorization:** ✅ Required (JWT Token)

**Role Access:** Admin (any), Courier (assigned), Customer (own)

#### Request

**Headers:**
```
Authorization: Bearer <TOKEN>
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| shipment_id | integer | ✅ Yes | Tracking number shipment |

**Body:** ❌ Tidak ada (GET request)

#### Response

**Success (200 OK):**
```json
[
  {
    "id": 1,
    "location": "Warehouse Jakarta",
    "description": "Package received at warehouse",
    "status": "placed",
    "timestamp": "2024-12-01T09:00:00"
  },
  {
    "id": 2,
    "location": "Distribution Center Jakarta",
    "description": "Package sorted and ready for dispatch",
    "status": "in_transit",
    "timestamp": "2024-12-01T14:30:00"
  },
  {
    "id": 3,
    "location": "On delivery vehicle",
    "description": "Package out for delivery",
    "status": "out_for_delivery",
    "timestamp": "2024-12-02T08:00:00"
  }
]
```

**Empty Tracking (200 OK):**
```json
[]
```

**Error - Not Found (404):**
```json
{
  "detail": "Shipment with tracking number 99999 not found"
}
```

#### Testing dengan cURL
```bash
curl -X GET "http://127.0.0.1:8000/shipment/12701/tracking" \
  -H "Authorization: Bearer <TOKEN>"
```

#### Ekspektasi
✅ Mendapat semua tracking events berurutan
✅ Events terurut dari yang paling lama
✅ Setiap event punya lokasi, deskripsi, status, timestamp
✅ Bisa kosong jika belum ada tracking

---

### ➕ B. Add Tracking Event

**Endpoint:** `POST /shipment/{shipment_id}/tracking`

**Tujuan:** Menambahkan tracking event baru ke shipment

**Authorization:** ✅ Required (JWT Token)

**Role Access:** ✅ Admin, ✅ Courier (assigned), ❌ Customer

#### Request

**Headers:**
```
Authorization: Bearer <TOKEN>
Content-Type: application/json
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| shipment_id | integer | ✅ Yes | Tracking number shipment |

**Body (JSON):**
```json
{
  "location": "Distribution Center Surabaya",
  "description": "Package arrived at sorting facility",
  "status": "in_transit"
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| location | string | ✅ Yes | Lokasi kejadian tracking |
| description | string | ✅ Yes | Deskripsi detail kejadian |
| status | string | ✅ Yes | Status shipment pada event ini |

**Valid Status Values:**
- `placed`
- `in_transit`
- `out_for_delivery`
- `delivered`
- `returned`
- `cancelled`

#### Response

**Success (201 Created):**
```json
{
  "id": 4,
  "location": "Distribution Center Surabaya",
  "description": "Package arrived at sorting facility",
  "status": "in_transit",
  "timestamp": "2024-12-02T10:15:00"
}
```

**Error - Not Found (404):**
```json
{
  "detail": "Shipment with id 99999 not found"
}
```

**Error - Forbidden (403):**
```json
{
  "detail": "Access denied. Required roles: admin, courier"
}
```

**Error - Invalid Status (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "status"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

#### Testing dengan cURL
```bash
curl -X POST "http://127.0.0.1:8000/shipment/12701/tracking" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Distribution Center Surabaya",
    "description": "Package arrived at sorting facility",
    "status": "in_transit"
  }'
```

#### Ekspektasi
✅ Tracking event baru ditambahkan
✅ ID auto-increment
✅ Timestamp otomatis (waktu sekarang)
✅ Status shipment ikut terupdate sesuai event
✅ Customer TIDAK bisa menambah tracking

---

## 4️⃣ STATISTICS & HEALTH ENDPOINTS

### 📊 A. Get Statistics

**Endpoint:** `GET /stats`

**Tujuan:** Mendapatkan statistik ringkasan shipment

**Authorization:** ✅ Required (JWT Token)

**Role Access:** All roles (data filtered by role)

#### Request

**Headers:**
```
Authorization: Bearer <TOKEN>
```

**Body:** ❌ Tidak ada (GET request)

#### Response

**Success (200 OK):**
```json
{
  "total_shipments": 5,
  "by_status": {
    "placed": 2,
    "in_transit": 2,
    "delivered": 1,
    "out_for_delivery": 0,
    "returned": 0,
    "cancelled": 0
  },
  "total_weight": 62.4,
  "avg_weight": 12.48
}
```

**Response Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| total_shipments | integer | Total jumlah shipments |
| by_status | object | Jumlah shipments per status |
| total_weight | float | Total berat semua paket (kg) |
| avg_weight | float | Rata-rata berat paket (kg) |

**Empty State (200 OK):**
```json
{
  "total_shipments": 0,
  "by_status": {
    "placed": 0,
    "in_transit": 0,
    "out_for_delivery": 0,
    "delivered": 0,
    "returned": 0,
    "cancelled": 0
  },
  "total_weight": 0,
  "avg_weight": 0
}
```

#### Testing dengan cURL
```bash
curl -X GET "http://127.0.0.1:8000/stats" \
  -H "Authorization: Bearer <TOKEN>"
```

#### Ekspektasi
✅ Admin: Statistik SEMUA shipments
✅ Courier: Statistik shipments assigned
✅ Customer: Statistik shipments milik sendiri
✅ Perhitungan akurat (total, rata-rata)
✅ Grouping by status benar

---

### ❤️ B. Health Check

**Endpoint:** `GET /health`

**Tujuan:** Mengecek status kesehatan API

**Authorization:** ❌ Tidak perlu (Public endpoint)

#### Request

**Headers:** ❌ Tidak perlu

**Body:** ❌ Tidak ada (GET request)

#### Response

**Success (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-03T10:30:00",
  "total_shipments": 5
}
```

**Response Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| status | string | Status kesehatan API |
| timestamp | datetime | Waktu saat health check |
| total_shipments | integer | Total shipments di sistem |

#### Testing dengan cURL
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

#### Ekspektasi
✅ Server berjalan normal
✅ Response cepat (< 100ms)
✅ Tidak butuh autentikasi
✅ Bisa digunakan untuk monitoring

---

## 5️⃣ TESTING SCENARIOS

### 🎯 Scenario 1: Complete Customer Journey

**Tujuan:** Customer mendaftar, login, membuat shipment, dan tracking

```bash
# Step 1: Sign Up
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "customer_new",
    "email": "customer@example.com",
    "password": "customer123"
  }'

# Expected: 201 Created
# Response: {"username": "customer_new", "email": "customer@example.com", "role": "customer", ...}

# Step 2: Login
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "customer_new",
    "password": "customer123"
  }'

# Expected: 200 OK
# Response: {"access_token": "eyJ...", "token_type": "bearer"}
# ACTION: Copy token untuk step selanjutnya

# Step 3: Create Shipment
curl -X POST "http://127.0.0.1:8000/shipment" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "package_details": {
      "content": "Books",
      "weight": 3.0,
      "fragile": false
    },
    "recipient": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+6281234567890",
      "address": "Jl. Test No. 123"
    },
    "seller": {
      "name": "Bookstore",
      "email": "book@store.com",
      "phone": "+6281234567891"
    },
    "destination_code": 11002
  }7

# Expected: 201 Created
# Response: {"tracking_number": 12706}

# Step 4: View Own Shipments
curl -X GET "http://127.0.0.1:8000/shipments" \
  -H "Authorization: Bearer <TOKEN>"

# Expected: 200 OK
# Response: Array of shipments (hanya milik customer_new)

# Step 5: Get Shipment Detail
curl -X GET "http://127.0.0.1:8000/shipment/12706" \
  -H "Authorization: Bearer <TOKEN>"

# Expected: 200 OK
# Response: Full shipment detail

# Step 6: Get Tracking History
curl -X GET "http://127.0.0.1:8000/shipment/12706/tracking" \
  -H "Authorization: Bearer <TOKEN>"

# Expected: 200 OK
# Response: Array of tracking events

# Step 7: Try to Update Status (Should Fail)
curl -X PATCH "http://127.0.0.1:8000/shipment/12706" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"current_status": "delivered"}'

# Expected: 403 Forbidden
# Customer tidak bisa update status
```

**Hasil Ekspektasi:**
✅ Customer berhasil register dan login
✅ Customer bisa create shipment
✅ Customer bisa view shipment miliknya
✅ Customer TIDAK bisa update status
✅ Customer TIDAK bisa add tracking event

---

### 🚚 Scenario 2: Courier Workflow

**Tujuan:** Courier login, lihat shipment assigned, update status, add tracking

```bash
# Step 1: Login as Courier
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "courier",
    "password": "courier123"
  }'

# Expected: 200 OK
# ACTION: Copy token

# Step 2: View Assigned Shipments
curl -X GET "http://127.0.0.1:8000/shipments" \
  -H "Authorization: Bearer <TOKEN>"

# Expected: 200 OK
# Response: Shipments assigned to courier

# Step 3: Get Shipment Detail
curl -X GET "http://127.0.0.1:8000/shipment/12701" \
  -H "Authorization: Bearer <TOKEN>"

# Expected: 200 OK

# Step 4: Update Status to in_transit
curl -X PATCH "http://127.0.0.1:8000/shipment/12701" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"current_status": "in_transit"}'

# Expected: 200 OK
# Shipment status updated

# Step 5: Add Tracking Event
curl -X POST "http://127.0.0.1:8000/shipment/12701/tracking" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "On delivery vehicle",
    "description": "Package picked up by courier",
    "status": "in_transit"
  }'

# Expected: 201 Created

# Step 6: Update to out_for_delivery
curl -X PATCH "http://127.0.0.1:8000/shipment/12701" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"current_status": "out_for_delivery"}'

# Expected: 200 OK

# Step 7: Add Tracking - Out for Delivery
curl -X POST "http://127.0.0.1:8000/shipment/12701/tracking" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Near destination",
    "description": "Package out for delivery to recipient",
    "status": "out_for_delivery"
  }'

# Expected: 201 Created

# Step 8: Mark as Delivered
curl -X PATCH "http://127.0.0.1:8000/shipment/12701" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"current_status": "delivered"}'

# Expected: 200 OK

# Step 9: Add Final Tracking Event
curl -X POST "http://127.0.0.1:8000/shipment/12701/tracking" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Recipient address",
    "description": "Package delivered successfully",
    "status": "delivered"
  }'

# Expected: 201 Created

# Step 10: Try to Create Shipment (Should Fail)
curl -X POST "http://127.0.0.1:8000/shipment" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{...shipment data...}'

# Expected: 403 Forbidden
# Courier tidak bisa create shipment
```

**Hasil Ekspektasi:**
✅ Courier bisa login
✅ Courier bisa view assigned shipments
✅ Courier bisa update status shipment
✅ Courier bisa add tracking events
✅ Status transition tervalidasi dengan benar
✅ Courier TIDAK bisa create shipment
✅ Courier TIDAK bisa delete shipment

---

### 👨‍💼 Scenario 3: Admin Full Access

**Tujuan:** Admin melakukan semua operasi CRUD dan view statistics

```bash
# Step 1: Login as Admin
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Expected: 200 OK
# ACTION: Copy token

# Step 2: View ALL Shipments
curl -X GET "http://127.0.0.1:8000/shipments" \
  -H "Authorization: Bearer <TOKEN>"

# Expected: 200 OK
# Response: ALL shipments in system

# Step 3: Create Shipment
curl -X POST "http://127.0.0.1:8000/shipment" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "package_details": {
      "content": "Office Supplies",
      "weight": 10.0
    },
    "recipient": {
      "name": "Company XYZ",
      "email": "company@xyz.com",
      "phone": "+6281111111111",
      "address": "Jl. Office No. 99"
    },
    "seller": {
      "name": "Supplier ABC",
      "email": "supplier@abc.com",
      "phone": "+6282222222222"
    },
    "destination_code": 11004
  }'

# Expected: 201 Created

# Step 4: Update Any Field
curl -X PATCH "http://127.0.0.1:8000/shipment/12701" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_status": "delivered",
    "package_details": {
      "content": "Updated by admin",
      "weight": 9.0
    },
    "destination_code": 11006
  }'

# Expected: 200 OK
# Admin bisa update semua field sekaligus

# Step 5: Add Tracking Event
curl -X POST "http://127.0.0.1:8000/shipment/12701/tracking" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Admin override",
    "description": "Status updated by admin",
    "status": "delivered"
  }'

# Expected: 201 Created

# Step 6: View Statistics
curl -X GET "http://127.0.0.1:8000/stats" \
  -H "Authorization: Bearer <TOKEN>"

# Expected: 200 OK
# Response: Statistics of ALL shipments

# Step 7: Delete Shipment
curl -X DELETE "http://127.0.0.1:8000/shipment/12705" \
  -H "Authorization: Bearer <TOKEN>"

# Expected: 200 OK
# Response: {"message": "Shipment 12705 deleted successfully"}

# Step 8: Verify Deletion
curl -X GET "http://127.0.0.1:8000/shipment/12705" \
  -H "Authorization: Bearer <TOKEN>"

# Expected: 404 Not Found
```

**Hasil Ekspektasi:**
✅ Admin bisa view ALL shipments
✅ Admin bisa create shipment
✅ Admin bisa update ANY field
✅ Admin bisa add tracking
✅ Admin bisa view complete statistics
✅ Admin bisa delete shipment
✅ Admin memiliki full access ke semua operasi

---

### 🔒 Scenario 4: Authorization Testing

**Tujuan:** Memastikan role-based access control berfungsi dengan benar

```bash
# Test 1: Access Protected Endpoint Without Token
curl -X GET "http://127.0.0.1:8000/shipments"

# Expected: 401 Unauthorized
# Response: {"detail": "Not authenticated"}

# Test 2: Customer Try to Delete (Should Fail)
# Login as customer first, get token
curl -X DELETE "http://127.0.0.1:8000/shipment/12701" \
  -H "Authorization: Bearer <CUSTOMER_TOKEN>"

# Expected: 403 Forbidden
# Response: {"detail": "Access denied. Required roles: admin"}

# Test 3: Customer Try to Add Tracking (Should Fail)
curl -X POST "http://127.0.0.1:8000/shipment/12701/tracking" \
  -H "Authorization: Bearer <CUSTOMER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Test",
    "description": "Test",
    "status": "in_transit"
  }'

# Expected: 403 Forbidden
# Response: {"detail": "Access denied. Required roles: admin, courier"}

# Test 4: Courier Try to Create Shipment (Should Fail)
curl -X POST "http://127.0.0.1:8000/shipment" \
  -H "Authorization: Bearer <COURIER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{...shipment data...}'

# Expected: 403 Forbidden
# Response: {"detail": "Access denied. Required roles: admin, customer"}

# Test 5: Customer Try to View Other's Shipment (Should Fail)
# Assuming 12701 bukan milik customer yang login
curl -X GET "http://127.0.0.1:8000/shipment/12701" \
  -H "Authorization: Bearer <CUSTOMER_TOKEN>"

# Expected: 403 Forbidden (jika bukan miliknya)

# Test 6: Invalid Token
curl -X GET "http://127.0.0.1:8000/shipments" \
  -H "Authorization: Bearer invalid_token_12345"

# Expected: 401 Unauthorized
# Response: {"detail": "Could not validate credentials"}

# Test 7: Expired Token (wait > 30 minutes after login)
curl -X GET "http://127.0.0.1:8000/shipments" \
  -H "Authorization: Bearer <EXPIRED_TOKEN>"

# Expected: 401 Unauthorized
```

**Hasil Ekspektasi:**
✅ Semua protected endpoints butuh token
✅ Token invalid/expired ditolak (401)
✅ Role permissions diterapkan dengan benar (403)
✅ Customer hanya bisa akses miliknya sendiri
✅ Courier tidak bisa create/delete
✅ Only admin bisa delete

---

## 6️⃣ ERROR HANDLING

### Common HTTP Status Codes

| Code | Status | Meaning | Example |
|------|--------|---------|---------|
| 200 | OK | Request berhasil | GET /shipments |
| 201 | Created | Resource berhasil dibuat | POST /shipment |
| 400 | Bad Request | Request tidak valid | Invalid input |
| 401 | Unauthorized | Tidak ada/invalid token | Missing Authorization header |
| 403 | Forbidden | Tidak punya permission | Customer try to delete |
| 404 | Not Found | Resource tidak ditemukan | Shipment ID 99999 |
| 422 | Unprocessable Entity | Validation error | Weight > 25kg |
| 500 | Internal Server Error | Server error | Unexpected error |

### Error Response Formats

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "package_details", "weight"],
      "msg": "ensure this value is less than or equal to 25",
      "type": "value_error.number.not_le",
      "ctx": {"limit_value": 25}
    }
  ]
}
```

**Authorization Error (401):**
```json
{
  "detail": "Not authenticated"
}
```

**Permission Error (403):**
```json
{
  "detail": "Access denied. Required roles: admin, courier"
}
```

**Not Found Error (404):**
```json
{
  "detail": "Shipment with tracking number 99999 not found"
}
```

**Business Logic Error (400):**
```json
{
  "detail": "Invalid status transition from 'placed' to 'delivered'. Valid next status: in_transit"
}
```

---

## 📝 Testing Checklist

### Authentication
- [ ] Sign up dengan data valid
- [ ] Sign up dengan username duplicate (error)
- [ ] Sign up dengan email duplicate (error)
- [ ] Sign up dengan password < 6 char (error)
- [ ] Login dengan credentials benar
- [ ] Login dengan password salah (error)
- [ ] Get user info dengan token valid
- [ ] Get user info tanpa token (error)

### Shipment CRUD
- [ ] Create shipment sebagai customer
- [ ] Create shipment sebagai admin
- [ ] Create shipment sebagai courier (error)
- [ ] Get all shipments (sesuai role)
- [ ] Get shipment by ID (existing)
- [ ] Get shipment by ID (not found)
- [ ] Update status (valid transition)
- [ ] Update status (invalid transition)
- [ ] Update package details
- [ ] Delete shipment sebagai admin
- [ ] Delete shipment sebagai customer (error)

### Tracking
- [ ] Get tracking history (existing shipment)
- [ ] Get tracking (shipment tanpa tracking)
- [ ] Add tracking sebagai courier
- [ ] Add tracking sebagai admin
- [ ] Add tracking sebagai customer (error)

### Filtering & Queries
- [ ] Filter shipments by status
- [ ] Filter shipments by destination
- [ ] Limit results
- [ ] Multiple filters combined

### Authorization
- [ ] Access protected endpoint tanpa token (401)
- [ ] Access dengan token invalid (401)
- [ ] Access dengan token expired (401)
- [ ] Customer akses shipment orang lain (403)
- [ ] Courier create shipment (403)
- [ ] Customer delete shipment (403)

### Statistics & Health
- [ ] Get statistics (all roles)
- [ ] Health check (no auth)

---

## 🚀 Quick Start Testing

```bash
# 1. Start server
python run.py

# 2. Test health (no auth)
curl http://127.0.0.1:8000/health

# 3. Login as admin
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 4. Copy token dari response

# 5. Test protected endpoint
curl -H "Authorization: Bearer <TOKEN>" \
  http://127.0.0.1:8000/shipments

# 6. Create shipment
curl -X POST http://127.0.0.1:8000/shipment \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "package_details": {"content": "Test", "weight": 5.0},
    "recipient": {
      "name": "Test",
      "email": "test@test.com",
      "phone": "081234567890",
      "address": "Test Address"
    },
    "seller": {
      "name": "Test Seller",
      "email": "seller@test.com",
      "phone": "081234567891"
    },
    "destination_code": 11002
  }'
```

---

## 💡 Testing Tips

1. **Gunakan Swagger UI** untuk testing interaktif: http://127.0.0.1:8000/docs
2. **Simpan token** di environment variable atau file untuk reuse
3. **Test dengan 3 role berbeda** untuk validasi RBAC
4. **Check HTTP status code** untuk memahami hasil request
5. **Baca error messages** untuk debugging
6. **Test edge cases** (empty data, max values, invalid input)
7. **Verify data consistency** setelah operasi create/update/delete
8. **Test status transitions** mengikuti business rules
9. **Monitor performance** untuk request yang kompleks
10. **Document issues** yang ditemukan untuk debugging

---

## 📞 Support & Resources

- **API Documentation:** http://127.0.0.1:8000/docs
- **Scalar Docs:** http://127.0.0.1:8000/scalar
- **Health Check:** http://127.0.0.1:8000/health
- **Authentication Guide:** AUTHENTICATION_GUIDE.md
- **Repository:** https://github.com/geraldolst/tst-logixpress

---

**Happy Testing! 🎉**
