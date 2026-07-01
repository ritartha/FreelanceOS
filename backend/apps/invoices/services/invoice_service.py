from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from apps.invoices.models import Invoice, InvoiceLineItem, Payment

TWO_PLACES = Decimal("0.01")


def _round(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


# ── Totals ─────────────────────────────────────────────────────────────────────

@transaction.atomic
def recalculate_totals(invoice: Invoice) -> Invoice:
    """
    Subtotal from line items → discount → tax → total → amount_due.
    Mirrors quotation_service.recalculate_totals exactly.
    """
    subtotal = sum(
        (li.total for li in invoice.line_items.all()), Decimal("0")
    )
    if invoice.discount_type == "percent":
        discount_amount = subtotal * (invoice.discount_value / Decimal("100"))
    else:
        discount_amount = invoice.discount_value
    discount_amount = min(discount_amount, subtotal)

    taxable = subtotal - discount_amount
    tax_amount = taxable * (invoice.tax_rate / Decimal("100"))
    total = taxable + tax_amount

    invoice.subtotal = _round(subtotal)
    invoice.discount_amount = _round(discount_amount)
    invoice.tax_amount = _round(tax_amount)
    invoice.total = _round(total)
    invoice.amount_due = _round(max(total - invoice.amount_paid, Decimal("0")))
    invoice.save(update_fields=[
        "subtotal", "discount_amount", "tax_amount", "total", "amount_due", "updated_at"
    ])
    return invoice


def recalculate_line_item_total(line_item: InvoiceLineItem) -> InvoiceLineItem:
    line_item.total = _round(line_item.quantity * line_item.unit_price)
    line_item.save(update_fields=["total"])
    return line_item


# ── Payments ───────────────────────────────────────────────────────────────────

@transaction.atomic
def record_payment(invoice: Invoice, amount: Decimal, method: str, paid_on, reference: str = "", notes: str = "", user=None) -> Payment:
    """
    Record a (partial) payment and update invoice.amount_paid / amount_due / status.
    """
    payment = Payment.objects.create(
        tenant=invoice.tenant,
        invoice=invoice,
        amount=_round(amount),
        method=method,
        paid_on=paid_on,
        reference=reference,
        notes=notes,
        created_by=user,
    )
    _sync_payment_status(invoice)
    return payment


def _sync_payment_status(invoice: Invoice) -> None:
    """Recompute amount_paid, amount_due and status from all payments."""
    total_paid = sum(
        (p.amount for p in invoice.payments.all()), Decimal("0")
    )
    invoice.amount_paid = _round(total_paid)
    invoice.amount_due = _round(max(invoice.total - total_paid, Decimal("0")))

    if invoice.amount_due <= 0:
        invoice.status = Invoice.StatusChoices.PAID
        invoice.paid_at = timezone.now()
    elif invoice.amount_paid > 0:
        invoice.status = Invoice.StatusChoices.PARTIAL
    # else leave current status unchanged (draft/sent/overdue)

    invoice.save(update_fields=["amount_paid", "amount_due", "status", "paid_at", "updated_at"])


# ── Convert from Quotation ──────────────────────────────────────────────────────

@transaction.atomic
def convert_quotation_to_invoice(quotation, user=None) -> Invoice:
    """
    Create an Invoice from an accepted Quotation, copying all line items,
    tax, discount, and currency. Marks the quotation as converted.
    """
    from apps.quotations.models import Quotation

    if quotation.status not in (
        Quotation.StatusChoices.ACCEPTED, Quotation.StatusChoices.SENT, Quotation.StatusChoices.VIEWED
    ):
        raise ValueError(f"Cannot convert a quotation with status '{quotation.status}' to an invoice.")

    tenant = quotation.tenant
    today = timezone.now().date()

    invoice = Invoice.objects.create(
        tenant=tenant,
        client=quotation.client,
        quotation=quotation,
        invoice_number=Invoice.generate_invoice_number(tenant),
        issue_date=today,
        due_date=today,  # caller should update due_date as needed
        tax_rate=quotation.tax_rate,
        discount_type=quotation.discount_type,
        discount_value=quotation.discount_value,
        currency=quotation.currency,
        notes=quotation.notes,
        created_by=user,
    )

    for q_item in quotation.line_items.all():
        li = InvoiceLineItem.objects.create(
            invoice=invoice,
            description=q_item.description,
            quantity=q_item.quantity,
            unit_price=q_item.unit_price,
            total=q_item.total,
        )

    recalculate_totals(invoice)

    quotation.status = Quotation.StatusChoices.CONVERTED
    quotation.save(update_fields=["status", "updated_at"])

    return invoice


# ── Import billable time logs ──────────────────────────────────────────────────

@transaction.atomic
def import_time_logs_to_invoice(invoice: Invoice, time_log_ids: list, user=None) -> int:
    """
    Pull billable TimeLog entries into invoice line items.
    Groups entries by description (project + task), consolidating hours.
    Returns the count of line items created.
    """
    from apps.time_tracking.models import TimeLog

    logs = TimeLog.objects.filter(
        id__in=time_log_ids,
        tenant=invoice.tenant,
        is_billable=True,
    ).select_related("task", "project")

    if not logs.exists():
        return 0

    # Group by hourly_rate so entries with different rates stay separate
    groups: dict[Decimal, dict] = {}
    for log in logs:
        rate = log.hourly_rate or Decimal("0")
        hours = Decimal(str(log.duration_seconds)) / Decimal("3600")
        if rate not in groups:
            groups[rate] = {"hours": Decimal("0"), "rate": rate, "descriptions": []}
        groups[rate]["hours"] += hours
        label = log.description or (log.task.name if log.task else log.project.name)
        if label not in groups[rate]["descriptions"]:
            groups[rate]["descriptions"].append(label)

    created = 0
    for rate, data in groups.items():
        hours = _round(data["hours"])
        description = ", ".join(data["descriptions"][:3])  # cap label length
        li = InvoiceLineItem.objects.create(
            invoice=invoice,
            description=f"Time: {description}",
            quantity=hours,
            unit_price=_round(data["rate"]),
            total=_round(hours * data["rate"]),
        )
        created += 1

    recalculate_totals(invoice)
    return created
