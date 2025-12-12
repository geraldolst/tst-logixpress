# Supabase + Vercel Deployment Guide

## 🗄️ Setup Supabase (PostgreSQL Database)

### Step 1: Create Supabase Project
1. Go to https://supabase.com
2. Click "Start your project"
3. Sign in with GitHub
4. Click "New Project"
5. Fill in:
   - Name: `tst-logixpress`
   - Database Password: (generate strong password)
   - Region: Choose closest to you
6. Click "Create new project" (wait ~2 minutes)

### Step 2: Get Database Connection String
1. Go to Project Settings → Database
2. Copy "Connection string" → "URI"
3. It looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
4. Save this for Vercel setup

### Step 3: Create Tables (Optional - untuk production)
Run SQL di Supabase SQL Editor:

```sql
-- Users table
CREATE TABLE users (
    username VARCHAR(100) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'customer',
    disabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Shipments table
CREATE TABLE shipments (
    shipment_id VARCHAR(20) PRIMARY KEY,
    package_details JSONB NOT NULL,
    recipient JSONB NOT NULL,
    seller JSONB NOT NULL,
    current_status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tracking events table
CREATE TABLE tracking_events (
    event_id SERIAL PRIMARY KEY,
    shipment_id VARCHAR(20) REFERENCES shipments(shipment_id),
    status VARCHAR(20) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Insert default users
INSERT INTO users (username, email, hashed_password, full_name, role)
VALUES 
    ('admin', 'admin@logixpress.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ND.Lhf8l0wCG', 'Admin User', 'admin'),
    ('courier1', 'courier@logixpress.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ND.Lhf8l0wCG', 'Courier One', 'courier'),
    ('customer1', 'customer@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ND.Lhf8l0wCG', 'Customer One', 'customer');
```

**Note:** Password hash di atas adalah untuk password `admin123`

---

## ▲ Deploy to Vercel with Supabase

### Step 1: Deploy to Vercel
1. Go to https://vercel.com
2. Click "Add New..." → "Project"
3. Import `geraldolst/tst-logixpress`
4. Click "Deploy"

### Step 2: Add Supabase Environment Variable
1. In Vercel Dashboard → Your Project
2. Go to "Settings" → "Environment Variables"
3. Add:
   ```
   Key: DATABASE_URL
   Value: postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
4. Click "Save"
5. Redeploy: "Deployments" → "..." → "Redeploy"

### Step 3: Test Deployment
```bash
# Health check
curl https://tst-logixpress.vercel.app/health

# API docs
https://tst-logixpress.vercel.app/docs
```

---

## 🎯 Current Setup (In-Memory)

**Note:** Aplikasi saat ini menggunakan in-memory database untuk kemudahan development.

**Untuk production dengan Supabase:**
- Database connection string akan digunakan kalau `DATABASE_URL` environment variable ada
- Kalau tidak ada, fallback ke in-memory database
- Data akan persistent di Supabase PostgreSQL

---

## 📊 Features with Supabase

✅ **Persistent Data** - Data tidak hilang
✅ **Free Tier** - 500MB database, 2GB bandwidth
✅ **Auto Backups** - Daily backups
✅ **SQL Editor** - Built-in SQL editor
✅ **Real-time** - Supabase realtime features
✅ **Auth** - Built-in authentication (optional)

---

## 🔧 Local Development with Supabase

```bash
# Set environment variable
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres"

# Or add to .env file
echo "DATABASE_URL=postgresql://..." >> .env

# Run app
python run.py
```

---

## 💡 Alternative: Keep In-Memory for Demo

Kalau mau tetap pakai in-memory database (untuk demo sederhana):
- ✅ Tidak perlu setup Supabase
- ✅ Deployment lebih cepat
- ❌ Data reset setiap deployment/restart
- ✅ Cukup untuk testing & demo

**Current deployment sudah bisa jalan tanpa database!**
