

**New Django apps to create** (currently nonexistent)
- `proposals` — ProposalTemplate, Proposal, Variable, models for markdown content, PDF export, send-via-email, acceptance tracking, analytics (views/opens)
- `quotations` — Quotation, QuotationLineItem, tax/GST/discount fields, PDF, shareable link (public token), version history
- `contracts` — Contract, ContractVersion, signature (store signed file or e-sign integration), renewal/expiration reminder fields (for Celery beat)
- `calendar_app` — CalendarEvent linking to tasks/projects/deadlines, optional Google Calendar sync fields
- `portfolio` — PortfolioItem, media (images/videos), case studies, skills, public slug for shareable profile
- `client_portal` — separate auth/permission layer so Client (not Membership user) can log in and view scoped data; needs its own auth or token-based access tied to `crm.Client`
- `notes` — rich text/markdown Note model, attachable to Project/Client/Task generically (consider a generic FK or polymorphic link)
- Agency Mode isn't a new app — it extends `tenants` (Membership already exists): needs Role, Permission, Department models added there

**Existing apps to flesh out**
- `dashboard` — empty models.py; needs either a `DashboardSnapshot` cache model (Celery-refreshed) or stays computed-on-the-fly with a proper service layer (revenue, deadlines, recent clients, notifications feed, KPI deltas)
- `reports` — empty models.py and stub view; needs real aggregation services for revenue/expense/profit/top-clients/monthly trends, plus CSV/PDF export
- `invoices` — has models but check: recurring invoices, partial payments, payment reminders via Celery — confirm these fields/tasks exist
- `crm` — only 39 lines in models.py; verify lead scoring, tags, communication history, notes linkage are present
- `files` — only 20 lines; needs folders, versioning, tags, storage usage tracking
- `accounts` — confirm 2FA, Google OAuth, email verification are actually implemented vs. stubbed

**Cross-cutting backend work**
- Service layer audit: confirm every app has a `services/` folder with actual business logic (some only have `accounts` and `audit` with services/ currently)
- Repository pattern: `common/repositories.py` exists — confirm it's actually used, not just defined
- Celery tasks: list what's in each `tasks.py`/`tasks/` — needed for invoice reminders, contract expiration alerts, recurring invoices, notification digest
- Permissions/RBAC: needs to span new client_portal + agency roles
- API versioning/pagination/filtering: confirm `common/pagination.py` and `common/filters.py` are wired into all ViewSets, not just defined

Since this is a lot of surface area, I'd suggest sequencing it rather than building everything in parallel. Want me to propose a build order (e.g., which app to do first, second, etc.) and turn this into a literal step-by-step checklist artifact you can check off, or do you want to just pick a starting app and we go module by module right now?