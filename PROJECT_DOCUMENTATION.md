# FreelanceOS — Complete Project Documentation

---

## Table of Contents

1. [Project Description](#1-project-description)
2. [Setup & Installation Instructions](#2-setup--installation-instructions)
3. [Technical Documentation](#3-technical-documentation)
4. [User Manual](#4-user-manual)

---

# 1. Project Description

## 1.1 Overview

**FreelanceOS** is a full-stack, multi-tenant freelance business management platform built to help independent professionals and small agencies manage every aspect of their freelance operations — from client relationships and project tracking to invoicing, expenses, time logs, and reporting — all from a single unified dashboard.

The platform is architected as a **decoupled application**:
- **Backend**: A Django 5.1 REST API with JWT authentication, multi-tenant data isolation, soft-delete, audit logging, and Celery-based async task processing.
- **Frontend**: A lightweight, framework-free HTML/CSS/JavaScript single-page application (SPA) with a premium dark-themed UI featuring glassmorphism, smooth animations, and responsive layouts.

## 1.2 Key Features

| Feature Area | Description |
|---|---|
| **Authentication** | Email-based registration & login with JWT (access + refresh tokens), email verification, password reset, and session logging |
| **Multi-Tenancy** | Each user gets an isolated workspace (tenant). All business data is automatically scoped to the active tenant |
| **CRM / Clients** | Full CRUD for managing clients with name, email, phone, company, website, notes, and status (Active / Inactive / Lead) |
| **Contacts** | Per-client contact management with primary contact designation |
| **Projects** | Project lifecycle management with status tracking (Planning → Active → On Hold → Completed → Cancelled), budgets, due dates, and client linking |
| **Tasks** | Kanban-ready task management with priority levels (Low / Medium / High / Urgent), status tracking, assignees, due dates, and time estimates |
| **Time Tracking** | Per-project and per-task time logging with start/end times, automatic duration calculation, billable/non-billable flags, and hourly rates |
| **Invoices** | Professional invoicing with line items, tax calculations, status workflow (Draft → Sent → Viewed → Paid → Overdue → Cancelled), and per-tenant unique invoice numbers |
| **Expenses** | Expense tracking with categories (Travel / Software / Office / Other), receipt uploads, billable and reimbursable flags |
| **File Attachments** | Generic file attachment system linkable to any entity via polymorphic references |
| **Notifications** | In-app notification system with types (Info / Warning / Success / Error) and read/unread tracking |
| **Audit Trail** | Automatic logging of all create/update/delete actions with old/new data snapshots, IP addresses, and user agents |
| **Reports** | Dedicated reports module (API-ready, currently stateless) |
| **Dashboard** | Real-time summary statistics showing active projects, pending tasks, unpaid invoices, and total expenses |

## 1.3 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (frontend_ui2/)                  │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  index.html   │  │ dashboard.html│  │   css/styles.css │  │
│  │  (Login/Reg)  │  │ (Dashboard)  │  │  (Dark Theme UI) │  │
│  └───────┬───────┘  └──────┬───────┘  └──────────────────┘  │
│          │                 │                                 │
│          └────────┬────────┘                                 │
│                   │                                          │
│          ┌────────▼────────┐                                 │
│          │   js/api.js     │  ← API service layer            │
│          │  (JWT + fetch)  │                                  │
│          └────────┬────────┘                                 │
└───────────────────┼─────────────────────────────────────────┘
                    │  HTTP (JSON)
                    │  Authorization: Bearer <JWT>
┌───────────────────▼─────────────────────────────────────────┐
│                   Backend (backend/)                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Django 5.1  │  │   DRF 3.15   │  │  SimpleJWT       │   │
│  │  (Core)      │  │  (REST API)  │  │  (Auth Tokens)   │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────┘   │
│         │                 │                                  │
│  ┌──────▼─────────────────▼──────────────────────────────┐  │
│  │              14 Django Apps                            │  │
│  │  accounts · tenants · audit · crm · projects · tasks  │  │
│  │  time_tracking · invoices · expenses · dashboard      │  │
│  │  reports · files · notifications · common             │  │
│  └──────┬────────────────────────────────────────────────┘  │
│         │                                                    │
│  ┌──────▼──────┐  ┌──────────┐  ┌────────────────────────┐  │
│  │  SQLite /   │  │  Celery  │  │  Redis (Cache/Broker)  │  │
│  │  PostgreSQL │  │ (Async)  │  │  (Optional in dev)     │  │
│  └─────────────┘  └──────────┘  └────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## 1.4 Technology Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Runtime |
| Django | 5.1.x | Web framework |
| Django REST Framework | 3.15.x | REST API layer |
| SimpleJWT | 5.3+ | JWT authentication |
| django-filter | 24.0+ | API filtering |
| django-cors-headers | 4.0+ | Cross-origin support |
| Celery + Redis | 5.4+ | Async task processing |
| django-celery-beat | 2.6+ | Periodic task scheduling |
| PostgreSQL / SQLite | — | Database (SQLite for dev, PostgreSQL for prod) |
| WhiteNoise | 6.7+ | Static file serving |
| WeasyPrint | 62.0+ | PDF generation |
| Sentry SDK | 2.0+ | Error monitoring |
| Pillow | 10.0+ | Image processing |
| boto3 + django-storages | — | S3 file storage (optional) |

### Frontend
| Technology | Purpose |
|---|---|
| HTML5 | Page structure |
| Vanilla CSS3 | Styling with custom properties, glassmorphism, gradients |
| Vanilla JavaScript (ES6+) | API communication, DOM manipulation, SPA routing |
| Google Fonts (Inter, Orbitron) | Typography |
| icons8 | Sidebar navigation icons |

### Development Tools
| Tool | Purpose |
|---|---|
| django-debug-toolbar | Request/query debugging |
| django-extensions | Management command utilities |
| pytest + pytest-django | Testing framework |
| factory-boy + faker | Test data generation |
| black + isort + flake8 | Code formatting & linting |

---

# 2. Setup & Installation Instructions

## 2.1 Prerequisites

Before setting up FreelanceOS, ensure you have the following installed:

- **Python 3.12+** — [Download from python.org](https://www.python.org/downloads/)
- **pip** — Comes with Python (verify with `pip --version`)
- **Git** — [Download from git-scm.com](https://git-scm.com/)
- **A modern web browser** — Chrome, Firefox, or Edge

> **Note:** For local development, SQLite is used by default — no database installation is required. Redis is also bypassed in dev mode (in-memory cache + eager Celery).

## 2.2 Backend Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd FreelanceOS
```

### Step 2: Create a Virtual Environment

**Windows (PowerShell):**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements/local.txt
```

### Step 4: Create Environment File (Optional)

The application works with default settings out of the box. Optionally, create a `.env` file in the project root for custom configuration:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.local
DATABASE_URL=sqlite:///db.sqlite3
```

### Step 5: Run Database Migrations

```bash
python manage.py migrate
```

### Step 6: Create a Superuser (Optional — for Admin Panel)

```bash
python manage.py createsuperuser
```

### Step 7: Start the Development Server

```bash
python manage.py runserver
```

The backend API is now running at: **`http://127.0.0.1:8000/`**

- API endpoints: `http://127.0.0.1:8000/api/v1/`
- Admin panel: `http://127.0.0.1:8000/admin/`
- Health check: `http://127.0.0.1:8000/health/`

## 2.3 Frontend Setup

The frontend is a static HTML/CSS/JS application — no build step required.

### Option A: Open Directly in Browser

Simply double-click `frontend_ui2/index.html` in your file explorer.

> **Warning:** Some browsers restrict `file://` origin requests. If you encounter CORS issues, use Option B instead.

### Option B: Use VS Code Live Server (Recommended)

1. Install the **Live Server** extension in VS Code
2. Right-click `frontend_ui2/index.html`
3. Select **"Open with Live Server"**
4. The page will open at `http://127.0.0.1:5500/frontend_ui2/index.html`

### Option C: Use Python's Built-in HTTP Server

```bash
cd frontend_ui2
python -m http.server 5500
```

Then open `http://127.0.0.1:5500/index.html` in your browser.

## 2.4 Quick Start Checklist

| Step | Command | Expected Result |
|---|---|---|
| 1. Start backend | `cd backend && python manage.py runserver` | Server running on `:8000` |
| 2. Open frontend | Open `frontend_ui2/index.html` via Live Server | Login page appears |
| 3. Register | Fill the registration form | Redirected to dashboard |
| 4. Explore | Click sidebar sections | Data loads from API |

## 2.5 Running Tests

```bash
cd backend
pytest
```

With coverage report:
```bash
pytest --cov=apps --cov-report=html
```

## 2.6 Code Quality Checks

```bash
# Format code
black .
isort .

# Lint
flake8
```

---

# 3. Technical Documentation

## 3.1 Project Structure

```
FreelanceOS/
├── backend/                          # Django backend
│   ├── apps/                         # All Django applications
│   │   ├── common/                   # Shared base models, mixins, utilities
│   │   ├── accounts/                 # User auth, JWT, sessions
│   │   ├── tenants/                  # Multi-tenant workspaces
│   │   ├── audit/                    # Audit trail logging
│   │   ├── crm/                      # Clients & contacts
│   │   ├── projects/                 # Project management
│   │   ├── tasks/                    # Task tracking
│   │   ├── time_tracking/            # Time logging
│   │   ├── invoices/                 # Invoicing & line items
│   │   ├── expenses/                 # Expense tracking
│   │   ├── dashboard/                # Dashboard summary API
│   │   ├── reports/                  # Reports (API-ready)
│   │   ├── files/                    # File attachments
│   │   └── notifications/           # In-app notifications
│   ├── config/                       # Django project configuration
│   │   ├── settings/
│   │   │   ├── base.py               # Shared settings
│   │   │   ├── local.py              # Development overrides
│   │   │   ├── production.py         # Production settings
│   │   │   └── test.py               # Test settings
│   │   ├── urls.py                   # Root URL configuration
│   │   ├── api_urls.py               # API v1 URL namespace
│   │   ├── celery.py                 # Celery configuration
│   │   └── wsgi.py / asgi.py         # Server entry points
│   ├── requirements/
│   │   ├── base.txt                  # Core dependencies
│   │   ├── local.txt                 # Dev dependencies
│   │   └── production.txt            # Prod dependencies
│   ├── manage.py                     # Django CLI
│   └── db.sqlite3                    # Local SQLite database
│
└── frontend_ui2/                     # Frontend SPA
    ├── index.html                    # Login & Registration page
    ├── dashboard.html                # Main dashboard (all views)
    ├── css/
    │   └── styles.css                # Complete dark theme stylesheet
    └── js/
        └── api.js                    # API service class (JWT + fetch)
```

## 3.2 Backend App Documentation

### 3.2.1 `common` — Shared Foundation

The `common` app provides base classes inherited by all other apps:

**Base Models:**
| Model | Purpose |
|---|---|
| `TimeStampedModel` | Abstract model with `created_at` and `updated_at` auto-timestamps |
| `TenantAwareModel` | Abstract model adding UUID PK, tenant FK, `created_by`/`updated_by` user FKs, soft-delete (`is_deleted`, `deleted_at`, `deleted_by`), and a JSON `metadata` field for extensibility |

**Managers:**
| Manager | Behavior |
|---|---|
| `SoftDeleteManager` | Default — filters out `is_deleted=True` records |
| `AllObjectsManager` | Includes soft-deleted records |
| `TenantAwareManager` | Filters by tenant + excludes deleted, with `.for_tenant(t)` helper |

**Key Mixins:**
| Mixin | Purpose |
|---|---|
| `TenantQuerysetMixin` | DRF ViewSet mixin — auto-filters by tenant, auto-sets `tenant` and `created_by`/`updated_by` on save |
| `AuditMixin` | Logs create/update/delete actions to the audit trail |
| `TenantViewMixin` | Django CBV mixin for server-rendered views |

**Exception Handling:**
All errors are wrapped in a standardized JSON envelope:
```json
{
  "success": false,
  "error": {
    "code": "error_code",
    "message": "Human-readable message",
    "details": { }
  }
}
```

**Pagination:**
- Default: `StandardPageNumberPagination` — 25 items/page, max 100
- Response format: `{"count": N, "next": "...", "previous": "...", "results": [...]}`

---

### 3.2.2 `accounts` — Authentication & Users

**Models:**
| Model | Fields | Purpose |
|---|---|---|
| `User` | `email` (unique), `first_name`, `last_name`, `avatar`, `phone`, `timezone`, `is_email_verified`, `is_2fa_enabled` | Custom user with email as login identifier (UUID PK) |
| `EmailVerificationToken` | `user`, `token`, `expires_at`, `used_at` | Email verification flow |
| `PasswordResetToken` | `user`, `token`, `expires_at`, `used_at` | Password reset flow |
| `SessionLog` | `user`, `ip_address`, `user_agent`, `login_at`, `logout_at` | Login session auditing |

**API Endpoints (`/api/v1/auth/`):**

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register/` | Public | Register new user. Returns `{user, access_token, refresh_token}` |
| `POST` | `/auth/login/` | Public | Login. Returns `{user, access_token, refresh_token}` |
| `POST` | `/auth/logout/` | JWT | Blacklists the refresh token |
| `POST` | `/auth/token/refresh/` | Public | Refresh an access token |
| `POST` | `/auth/verify-email/` | Public | Verify email with token |
| `POST` | `/auth/password/reset-request/` | Public | Request a password reset email |
| `POST` | `/auth/password/reset/` | Public | Reset password with token |
| `POST` | `/auth/password/change/` | JWT | Change password (requires old password) |
| `GET` | `/auth/me/` | JWT | Get current user profile |
| `PATCH` | `/auth/me/` | JWT | Update profile (first_name, last_name, phone, timezone, avatar) |

**Registration Flow:**
1. User submits email, password, first_name, last_name
2. System creates User + auto-bootstraps a personal Tenant (workspace) + Owner Role + Membership
3. Returns JWT tokens — user is immediately authenticated

---

### 3.2.3 `tenants` — Multi-Tenant Workspaces

**Models:**
| Model | Fields | Purpose |
|---|---|---|
| `Tenant` | `name`, `slug` (unique), `owner`, `plan` (Free/Pro/Enterprise), `is_active` | Workspace container |
| `Role` | `tenant`, `name`, `permissions` (JSON) | Per-tenant roles |
| `Membership` | `tenant`, `user`, `role`, `status` (Active/Inactive/Invited), `joined_at` | User-tenant relationship |

**How Tenant Isolation Works:**
1. `TenantContextMiddleware` runs on every request — finds the user's active membership and sets `request.tenant`
2. `TenantQuerysetMixin` on ViewSets filters all queries by `tenant=request.tenant`
3. `perform_create()` auto-sets `tenant` and `created_by` on new records
4. Data from other tenants is never accessible

---

### 3.2.4 `crm` — Client & Contact Management

**Models:**
| Model | Fields | Purpose |
|---|---|---|
| `Client` | `name`, `email`, `phone`, `company`, `website`, `notes`, `status` (Active/Inactive/Lead) | Client organizations |
| `Contact` | `client` (FK), `first_name`, `last_name`, `email`, `phone`, `is_primary` | Individual contacts within a client |

**API Endpoints (`/api/v1/`):**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/clients/` | List all clients (paginated) |
| `POST` | `/clients/` | Create a client |
| `GET` | `/clients/{id}/` | Get client details |
| `PATCH` | `/clients/{id}/` | Update a client |
| `DELETE` | `/clients/{id}/` | Soft-delete a client |
| `GET` | `/contacts/` | List all contacts |
| `POST` | `/contacts/` | Create a contact |
| `GET` | `/contacts/{id}/` | Get contact details |
| `PATCH` | `/contacts/{id}/` | Update a contact |
| `DELETE` | `/contacts/{id}/` | Soft-delete a contact |

---

### 3.2.5 `projects` — Project Management

**Model Fields:**
`name`, `client` (FK, optional), `description`, `status` (Planning / Active / On Hold / Completed / Cancelled), `start_date`, `due_date`, `budget`, `currency`, `hourly_rate`

**API Endpoints (`/api/v1/projects/`):**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/projects/` | List projects |
| `POST` | `/projects/` | Create a project |
| `GET` | `/projects/{id}/` | Get project details |
| `PATCH` | `/projects/{id}/` | Update a project |
| `DELETE` | `/projects/{id}/` | Soft-delete a project |

---

### 3.2.6 `tasks` — Task Management

**Model Fields:**
`project` (FK, required), `title`, `description`, `status` (To Do / In Progress / Review / Done / Cancelled), `priority` (Low / Medium / High / Urgent), `assignee` (FK, optional), `due_date`, `estimated_hours`, `actual_hours`

**API Endpoints (`/api/v1/tasks/`):**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/tasks/` | List tasks |
| `POST` | `/tasks/` | Create a task (requires `project` ID) |
| `GET` | `/tasks/{id}/` | Get task details |
| `PATCH` | `/tasks/{id}/` | Update a task |
| `DELETE` | `/tasks/{id}/` | Soft-delete a task |

---

### 3.2.7 `time_tracking` — Time Logging

**Model Fields:**
`task` (FK, optional), `project` (FK, required), `user` (FK, required), `description`, `start_time`, `end_time`, `duration_seconds` (auto-calculated), `is_billable`, `hourly_rate`

**API Endpoints (`/api/v1/time-logs/`):** Standard CRUD via ModelViewSet.

---

### 3.2.8 `invoices` — Invoicing

**Models:**
| Model | Fields |
|---|---|
| `Invoice` | `client` (FK, required), `project` (FK, optional), `invoice_number` (unique per tenant), `status` (Draft / Sent / Viewed / Paid / Overdue / Cancelled), `issue_date`, `due_date`, `subtotal`, `tax_rate`, `tax_amount`, `total`, `currency`, `notes`, `paid_at` |
| `InvoiceLineItem` | `invoice` (FK), `description`, `quantity`, `unit_price`, `total` |

**API Endpoints (`/api/v1/invoices/`):**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/invoices/` | List invoices |
| `POST` | `/invoices/` | Create an invoice (requires `client`, `issue_date`, `due_date`) |
| `GET` | `/invoices/{id}/` | Get invoice details |
| `PATCH` | `/invoices/{id}/` | Update an invoice |
| `DELETE` | `/invoices/{id}/` | Soft-delete an invoice |
| `GET/POST/PATCH/DELETE` | `/invoices/line-items/` | Line item CRUD |

---

### 3.2.9 `expenses` — Expense Tracking

**Model Fields:**
`project` (FK, optional), `category` (Travel / Software / Office / Other), `description`, `amount`, `currency`, `expense_date`, `receipt` (image upload), `is_billable`, `is_reimbursable`

**API Endpoints (`/api/v1/expenses/`):** Standard CRUD via ModelViewSet.

---

### 3.2.10 `dashboard` — Summary Statistics

**API Endpoints (`/api/v1/dashboard/`):**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dashboard/summary/` | Returns `{projects, tasks, invoices, expenses}` counts |

---

### 3.2.11 `audit` — Audit Trail

**Model Fields:**
`tenant`, `user`, `action` (Create / Update / Delete / View), `entity_type`, `entity_id`, `old_data` (JSON), `new_data` (JSON), `ip_address`, `user_agent`, `created_at`

Automatically populated by the `AuditMixin` and `AuditContextMiddleware`.

---

### 3.2.12 `files` — File Attachments

**Model Fields:**
`name`, `file` (upload), `content_type`, `size`, `entity_type`, `entity_id`

Generic attachment system — any entity can have files linked via `entity_type` + `entity_id`.

---

### 3.2.13 `notifications` — In-App Notifications

**Model Fields:**
`recipient` (FK User), `title`, `body`, `type` (Info / Warning / Success / Error), `is_read`, `read_at`, `link`

---

### 3.2.14 `reports` — Reporting

Currently a stateless module with API endpoints for generating reports. No persistent models.

---

## 3.3 Frontend Architecture

### `api.js` — API Service Layer

The `ApiService` class manages all backend communication:

- **JWT Session Management**: Stores `access_token`, `refresh_token`, and `user` in `localStorage`
- **Automatic Auth Headers**: Every request includes `Authorization: Bearer <token>`
- **401 Handling**: Automatically clears session and redirects to login on token expiration
- **Error Normalization**: Extracts user-friendly messages from the backend's error envelope
- **Network Error Detection**: Catches `TypeError` (fetch failed) and shows a friendly message

### `index.html` — Auth Page

Single page with two views (toggled via CSS `.hidden` class):
- **Login form**: Email + Password → calls `api.login()` → stores JWT → redirects to dashboard
- **Registration form**: First Name + Last Name + Email + Password → calls `api.register()` → auto-bootstraps workspace → redirects

### `dashboard.html` — Main Application

Single-page dashboard with sidebar navigation. Views are toggled dynamically:

- **Dashboard view**: Shows 4 stat cards (Active Projects, Pending Tasks, Unpaid Invoices, Total Expenses)
- **List views** (Clients, Projects, Tasks, Invoices): Data table with Create/Edit/Delete modals

The `VIEW_CONFIG` object defines the configuration for each entity type:
- Column definitions for the data table
- API methods for CRUD operations
- Form field definitions (including async-loaded dropdowns for foreign keys)
- Row data formatters

---

## 3.4 API Authentication Flow

```
1. User submits credentials
       │
       ▼
2. POST /api/v1/auth/login/
   Body: { "email": "...", "password": "..." }
       │
       ▼
3. Backend validates → returns:
   {
     "user": { "id": "...", "email": "...", ... },
     "access_token": "eyJ...",     ← short-lived (30 min)
     "refresh_token": "eyJ..."     ← long-lived (7 days)
   }
       │
       ▼
4. Frontend stores tokens in localStorage
       │
       ▼
5. All subsequent requests include:
   Authorization: Bearer <access_token>
       │
       ▼
6. On 401 → clear session → redirect to login
```

---

# 4. User Manual

## 4.1 Getting Started

### 4.1.1 Creating Your Account

1. Open the FreelanceOS login page (`index.html`)
2. Click **"Create one"** below the login form
3. Fill in your details:
   - **First Name** — Your given name
   - **Last Name** — Your surname
   - **Email Address** — This will be your login identifier
   - **Password** — Minimum 8 characters
4. Click **"Create Account"**
5. You'll be automatically logged in and redirected to your dashboard

> **Tip:** When you register, a personal workspace is automatically created for you. All your data (clients, projects, invoices, etc.) is isolated to this workspace.

### 4.1.2 Logging In

1. Enter your **Email Address** and **Password**
2. Click **"Sign In"**
3. You'll be redirected to the dashboard

### 4.1.3 Logging Out

Click the **"Logout"** button in the top-right corner of the dashboard. Your session tokens will be invalidated and you'll be redirected to the login page.

---

## 4.2 Dashboard Overview

The dashboard is the home screen you see after logging in. It displays four summary stat cards:

| Card | Meaning |
|---|---|
| **Active Projects** | Number of currently active projects |
| **Pending Tasks** | Number of tasks not yet completed |
| **Unpaid Invoices** | Number of invoices awaiting payment |
| **Total Expenses** | Running total of tracked expenses |

The stat cards use a glassmorphism design with hover animations for a premium look.

---

## 4.3 Sidebar Navigation

The left sidebar provides access to all sections:

| Icon | Section | Description |
|---|---|---|
| 🏠 | **Dashboard** | Summary statistics overview |
| 👥 | **CRM / Clients** | Manage your clients |
| 📁 | **Projects** | Track your projects |
| ✅ | **Tasks** | Manage tasks within projects |
| 📄 | **Invoices** | Create and track invoices |

Click any section to switch views. The active section is highlighted in orange.

Your **name**, **email**, and **avatar initial** are displayed at the bottom of the sidebar.

---

## 4.4 Managing Clients (CRM)

### Viewing Clients
Click **"CRM / Clients"** in the sidebar. You'll see a table with columns:
- **Name** — Client/company name
- **Email** — Primary email address
- **Company** — Company name
- **Status** — Active (green), Lead (yellow), or Inactive (red)
- **Actions** — Edit and Delete buttons

### Creating a New Client
1. Click the **"+ Create New"** button
2. Fill in the form:
   - **Name** * — Client or company name (required)
   - **Email** * — Email address (required)
   - **Company** — Company name
   - **Phone** — Phone number
   - **Status** — Active, Inactive, or Lead
3. Click **"Save"**
4. A success notification appears and the table refreshes

### Editing a Client
1. Click the **"Edit"** button in the client's row
2. Modify the fields as needed
3. Click **"Save"**

### Deleting a Client
1. Click the **"Delete"** button in the client's row
2. A confirmation dialog appears: _"Are you sure you want to delete this record?"_
3. Click **"Delete"** to confirm or **"Cancel"** to abort

> **Note:** Deletions are "soft deletes" — the record is marked as deleted but not permanently removed from the database. This allows for potential recovery.

---

## 4.5 Managing Projects

### Viewing Projects
Click **"Projects"** in the sidebar. The table shows:
- **Name** — Project name
- **Status** — Active (green), On Hold/Planning (yellow), Completed (green), Cancelled (red)
- **Start Date** — When the project begins
- **Budget** — Project budget in dollars

### Creating a New Project
1. Click **"+ Create New"**
2. Fill in:
   - **Project Name** * — Name of the project (required)
   - **Status** — Active, On Hold, Completed, or Cancelled
   - **Start Date** — Project start date
   - **Budget ($)** — Budget amount
   - **Description** — Detailed description
3. Click **"Save"**

### Editing / Deleting
Same workflow as Clients — use the **Edit** and **Delete** buttons in each row.

---

## 4.6 Managing Tasks

### Viewing Tasks
Click **"Tasks"** in the sidebar. The table shows:
- **Title** — Task title
- **Priority** — Low (yellow), Medium (yellow), High (yellow), Urgent (red)
- **Status** — To Do, In Progress, Done, Cancelled
- **Due Date** — Deadline

### Creating a New Task
1. Click **"+ Create New"**
2. Fill in:
   - **Project** * — Select the project this task belongs to (required dropdown, auto-loaded from your projects)
   - **Title** * — Task title (required)
   - **Priority** — Low, Medium, High, or Urgent
   - **Status** — To Do, In Progress, Done, or Cancelled
   - **Due Date** — Task deadline
3. Click **"Save"**

> **Important:** Every task must be assigned to a project. If you don't have any projects yet, create one first under the Projects section.

### Editing / Deleting
Same workflow as other sections.

---

## 4.7 Managing Invoices

### Viewing Invoices
Click **"Invoices"** in the sidebar. The table shows:
- **Invoice #** — Unique invoice number
- **Status** — Draft (yellow), Sent (yellow), Paid (green), Overdue (red), Cancelled (red)
- **Issue Date** — When the invoice was issued
- **Total** — Invoice amount in dollars

### Creating a New Invoice
1. Click **"+ Create New"**
2. Fill in:
   - **Client** * — Select the client (required dropdown, auto-loaded from your clients)
   - **Invoice #** — Unique invoice identifier (e.g., "INV-001")
   - **Status** — Draft, Sent, Paid, Overdue, or Cancelled
   - **Issue Date** * — Date the invoice is issued (required)
   - **Due Date** * — Payment due date (required)
   - **Total ($)** — Invoice total amount
3. Click **"Save"**

> **Important:** Every invoice must be linked to a client. If you don't have any clients yet, create one first under the CRM / Clients section.

### Editing / Deleting
Same workflow as other sections.

---

## 4.8 Notifications & Alerts

The application displays contextual alerts in the top-right corner:

| Alert Type | Color | When It Appears |
|---|---|---|
| **Success** (green) | ✅ | After creating, updating, or deleting a record |
| **Error** (red) | ❌ | When an API call fails (validation error, network issue, etc.) |

Alerts auto-dismiss after 5 seconds.

---

## 4.9 Recommended Workflow

The recommended order for setting up your workspace is:

```
1. Register / Login
       │
       ▼
2. Create Clients  (CRM / Clients → + Create New)
       │
       ▼
3. Create Projects  (Projects → + Create New)
       │
       ▼
4. Create Tasks     (Tasks → + Create New, select a Project)
       │
       ▼
5. Create Invoices  (Invoices → + Create New, select a Client)
       │
       ▼
6. Monitor Dashboard  (Dashboard → view summary stats)
```

### Tips & Best Practices

1. **Create clients first** → Then projects → Then tasks and invoices. This ensures the required dropdowns are populated.
2. **Use meaningful invoice numbers** → Follow a pattern like `INV-001`, `INV-002` for easy tracking.
3. **Set realistic due dates** → Helps you track overdue tasks and invoices.
4. **Organize by project** → Group related tasks under the same project for clarity.
5. **Regular backups** → The SQLite database file (`backend/db.sqlite3`) contains all your data. Back it up periodically.

---

## 4.10 Troubleshooting

| Problem | Solution |
|---|---|
| **"Unable to connect to the server"** | Make sure the Django backend is running: `python manage.py runserver` |
| **Login fails with no error** | Check the browser console (F12) for CORS or network errors |
| **"A tenant context is required"** | Your user doesn't have a workspace. Re-register or use the admin panel to create a Membership |
| **Data doesn't load (404)** | Ensure the backend server is running and accessible at `http://127.0.0.1:8000` |
| **Can't create tasks** | You need at least one project first. Create a project, then create tasks |
| **Can't create invoices** | You need at least one client first. Create a client, then create invoices |
| **Styles look broken** | Ensure you're opening files from the `frontend_ui2/` folder, not `frontend/` |

---

> **FreelanceOS** — Built for freelancers who take their business seriously. 🚀
