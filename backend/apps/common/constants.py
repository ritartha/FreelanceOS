"""
Shared constants for FreelanceOS.

Centralised enums and lookup tables used across apps.
"""

# =============================================================================
# Currency Codes (ISO 4217 — most commonly used)
# =============================================================================

CURRENCIES = [
    ("USD", "US Dollar"),
    ("EUR", "Euro"),
    ("GBP", "British Pound"),
    ("INR", "Indian Rupee"),
    ("CAD", "Canadian Dollar"),
    ("AUD", "Australian Dollar"),
    ("JPY", "Japanese Yen"),
    ("CHF", "Swiss Franc"),
    ("CNY", "Chinese Yuan"),
    ("SEK", "Swedish Krona"),
    ("NZD", "New Zealand Dollar"),
    ("SGD", "Singapore Dollar"),
    ("HKD", "Hong Kong Dollar"),
    ("NOK", "Norwegian Krone"),
    ("KRW", "South Korean Won"),
    ("MXN", "Mexican Peso"),
    ("BRL", "Brazilian Real"),
    ("ZAR", "South African Rand"),
    ("AED", "UAE Dirham"),
    ("SAR", "Saudi Riyal"),
]

DEFAULT_CURRENCY = "USD"

# =============================================================================
# Countries (ISO 3166-1 alpha-2 — most commonly used)
# =============================================================================

COUNTRIES = [
    ("US", "United States"),
    ("GB", "United Kingdom"),
    ("IN", "India"),
    ("CA", "Canada"),
    ("AU", "Australia"),
    ("DE", "Germany"),
    ("FR", "France"),
    ("JP", "Japan"),
    ("BR", "Brazil"),
    ("MX", "Mexico"),
    ("NL", "Netherlands"),
    ("SE", "Sweden"),
    ("NO", "Norway"),
    ("DK", "Denmark"),
    ("FI", "Finland"),
    ("SG", "Singapore"),
    ("HK", "Hong Kong"),
    ("AE", "United Arab Emirates"),
    ("SA", "Saudi Arabia"),
    ("ZA", "South Africa"),
    ("NZ", "New Zealand"),
    ("CH", "Switzerland"),
    ("IT", "Italy"),
    ("ES", "Spain"),
    ("PT", "Portugal"),
    ("IE", "Ireland"),
    ("PL", "Poland"),
    ("CZ", "Czech Republic"),
    ("AT", "Austria"),
    ("BE", "Belgium"),
]

# =============================================================================
# Tenant Types
# =============================================================================

TENANT_TYPES = [
    ("freelancer", "Freelancer"),
    ("agency", "Agency"),
]

# =============================================================================
# Membership Statuses
# =============================================================================

MEMBERSHIP_STATUSES = [
    ("active", "Active"),
    ("invited", "Invited"),
    ("suspended", "Suspended"),
    ("deactivated", "Deactivated"),
]

# =============================================================================
# Default Roles
# =============================================================================

DEFAULT_ROLES = [
    {
        "name": "Owner",
        "is_system_role": True,
        "permissions": {
            "manage_tenant": True,
            "manage_members": True,
            "manage_roles": True,
            "manage_billing": True,
            "view_audit_log": True,
            "manage_crm": True,
            "manage_projects": True,
            "manage_tasks": True,
            "manage_time_tracking": True,
            "manage_invoices": True,
            "manage_expenses": True,
            "manage_files": True,
            "view_reports": True,
            "manage_settings": True,
        },
    },
    {
        "name": "Admin",
        "is_system_role": True,
        "permissions": {
            "manage_tenant": False,
            "manage_members": True,
            "manage_roles": True,
            "manage_billing": False,
            "view_audit_log": True,
            "manage_crm": True,
            "manage_projects": True,
            "manage_tasks": True,
            "manage_time_tracking": True,
            "manage_invoices": True,
            "manage_expenses": True,
            "manage_files": True,
            "view_reports": True,
            "manage_settings": True,
        },
    },
    {
        "name": "Manager",
        "is_system_role": True,
        "permissions": {
            "manage_tenant": False,
            "manage_members": False,
            "manage_roles": False,
            "manage_billing": False,
            "view_audit_log": False,
            "manage_crm": True,
            "manage_projects": True,
            "manage_tasks": True,
            "manage_time_tracking": True,
            "manage_invoices": True,
            "manage_expenses": True,
            "manage_files": True,
            "view_reports": True,
            "manage_settings": False,
        },
    },
    {
        "name": "Employee",
        "is_system_role": True,
        "permissions": {
            "manage_tenant": False,
            "manage_members": False,
            "manage_roles": False,
            "manage_billing": False,
            "view_audit_log": False,
            "manage_crm": False,
            "manage_projects": False,
            "manage_tasks": True,
            "manage_time_tracking": True,
            "manage_invoices": False,
            "manage_expenses": True,
            "manage_files": True,
            "view_reports": False,
            "manage_settings": False,
        },
    },
    {
        "name": "Finance",
        "is_system_role": True,
        "permissions": {
            "manage_tenant": False,
            "manage_members": False,
            "manage_roles": False,
            "manage_billing": True,
            "view_audit_log": True,
            "manage_crm": False,
            "manage_projects": False,
            "manage_tasks": False,
            "manage_time_tracking": False,
            "manage_invoices": True,
            "manage_expenses": True,
            "manage_files": True,
            "view_reports": True,
            "manage_settings": False,
        },
    },
    {
        "name": "ReadOnly",
        "is_system_role": True,
        "permissions": {
            "manage_tenant": False,
            "manage_members": False,
            "manage_roles": False,
            "manage_billing": False,
            "view_audit_log": False,
            "manage_crm": False,
            "manage_projects": False,
            "manage_tasks": False,
            "manage_time_tracking": False,
            "manage_invoices": False,
            "manage_expenses": False,
            "manage_files": False,
            "view_reports": True,
            "manage_settings": False,
        },
    },
]

# =============================================================================
# Common Status Choices
# =============================================================================

GENERAL_STATUSES = [
    ("active", "Active"),
    ("inactive", "Inactive"),
    ("archived", "Archived"),
]

# =============================================================================
# Priority Levels
# =============================================================================

PRIORITY_LEVELS = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("urgent", "Urgent"),
]
