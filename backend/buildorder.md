# FreelanceOS — Backend Build Order

Sequenced so each stage unblocks the next: foundational data models first, then the modules that depend on them, then the cross-cutting glue (dashboard/reports) last, since those read from everything else.

---

##✅ Stage 0 — Foundation hardening (do first, touches everything downstream)
- 🔲 Audit `accounts` app: confirm email verification, Google OAuth, 2FA are fully implemented (not stubbed) — every later module assumes a working auth/session layer
- 🔲 Extend `tenants` app for Agency Mode: add `Role`, `Permission`, `Department` models; wire into existing `Membership` model
- 🔲 Confirm `common/repositories.py` and `common/pagination.py`/`filters.py` are actually used in existing ViewSets, not just defined — fix any that bypass them
- 🔲 Add `services/` folder to every app missing one (currently only `accounts` and `audit` have it)
- 🔲 Decide and document the Note-attachment pattern (generic FK vs. per-model FK) before building `notes`, since CRM, Projects, and Tasks will all need it

##✅  Stage 1 — CRM depth (everything else links back to Client)
- 🔲 Expand `crm/models.py` (currently 39 lines): Lead, Contact, Company, Tag, LeadScore, CommunicationHistory
- 🔲 Add CRM services: lead scoring logic, lead→client conversion
- 🔲 Add search/filter endpoints (leads, clients, tags)

##✅  Stage 2 — Notes app (new, small, needed by CRM/Projects/Tasks)
- 🔲 Build `notes` app: rich text/markdown Note model, generic attachment to Client/Project/Task
- 🔲 Wire into CRM and Projects serializers

##✅  Stage 3 — Files depth
- 🔲 Expand `files/models.py` (currently 20 lines): folders, version history, tags, storage usage tracking per tenant
- 🔲 Attach files to Projects/Contracts/Proposals (those come later — keep FK generic or nullable for now)

##✅  Stage 4 — Proposal Builder (new app)
- 🔲 `proposals` app: ProposalTemplate, Proposal, Variable model, markdown content field
- 🔲 PDF export service
- 🔲 Email-send service (reuse notifications app)
- 🔲 Acceptance tracking + analytics (views/opens) fields and endpoints

##✅ Stage 5 — Quotation Module (new app, depends on Proposals for "convert to quotation" later)
- 🔲 `quotations` app: Quotation, QuotationLineItem
- 🔲 Tax/GST/discount calculation service
- 🔲 PDF export, shareable public link (token-based, no login)
- 🔲 Version history model

## Stage 6 — Contract Module (new app, depends on Quotation/Proposal acceptance)
- 🔲 `contracts` app: Contract, ContractVersion
- 🔲 Signature storage (uploaded signed file first; e-sign integration is a later phase)
- 🔲 Renewal/expiration fields + Celery task for expiration alerts

## Stage 7 — Invoice depth (existing app, now has Quotation/Contract to pull from)
- 🔲 Confirm/add: recurring invoices, automatic numbering, partial payments
- 🔲 Convert-quotation-to-invoice service
- 🔲 Pull billable hours from `time_tracking` into invoice line items
- 🔲 Celery task: payment reminders

## Stage 8 — Calendar app (new, depends on Projects/Tasks/Invoices existing)
- 🔲 `calendar_app`: CalendarEvent linked to Task/Project deadlines and Invoice due dates
- 🔲 Optional Google Calendar sync fields (build sync logic later — model first)

## Stage 9 — Portfolio Manager (new, independent — can be built anytime, placed here to keep momentum on bigger pieces first)
- 🔲 `portfolio` app: PortfolioItem, media, case studies, skills, public slug

## Stage 10 — Client Portal (new, depends on almost everything above existing first)
- 🔲 Separate auth/access layer for `crm.Client` to log in (token or scoped session — decide approach)
- 🔲 Read-scoped endpoints: view project progress, approve quotations, download invoices, approve milestones, upload files, message freelancer

## Stage 11 — Reports (flesh out, now real data exists across all modules)
- 🔲 Replace stub `reports` app: revenue, expense, tax, profit, top-clients, monthly trend aggregation services
- 🔲 CSV/PDF export

## Stage 12 — Dashboard (last, since it aggregates from every module above)
- 🔲 Build out `DashboardSummaryAPIView` beyond the current 4 counts: revenue, upcoming deadlines, recent clients, pending invoices, recent notifications, KPI deltas
- 🔲 Decide live-query vs. Celery-cached snapshot model (`dashboard/models.py` is currently empty — needed if caching)
- 🔲 Wire `frontend_ui3/dashboard.html` to call the real endpoint (currently has zero fetch calls)

## Stage 13 — Cross-cutting Celery tasks pass
- 🔲 Invoice payment reminders, contract expiration alerts, recurring invoice generation, notification digest — confirm all exist and are scheduled via Celery beat

---

### Notes
- Stages 4→7 (Proposal → Quotation → Contract → Invoice) form the core revenue workflow chain — build them in that order since each "convert to X" action depends on the previous model existing.
- Dashboard and Reports are placed last on purpose: building them early just means rebuilding their queries every time a new module lands.
- Agency Mode (Stage 0) is placed first because RBAC affects every endpoint you write afterward — bolting it on later means touching every ViewSet twice.