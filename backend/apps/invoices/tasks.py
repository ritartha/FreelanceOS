import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def check_overdue_invoices():
    """
    Daily task. Marks sent/partial invoices past their due_date as overdue
    and queues a reminder email to the freelancer.

    Add to CELERY_BEAT_SCHEDULE:
        "overdue-invoices-daily": {
            "task": "apps.invoices.tasks.check_overdue_invoices",
            "schedule": crontab(hour=7, minute=0),
        },
    """
    from apps.invoices.models import Invoice

    today = timezone.now().date()
    overdue = Invoice.objects.filter(
        status__in=[Invoice.StatusChoices.SENT, Invoice.StatusChoices.PARTIAL],
        due_date__lt=today,
        is_deleted=False,
    )
    for invoice in overdue:
        invoice.status = Invoice.StatusChoices.OVERDUE
        invoice.save(update_fields=["status", "updated_at"])
        send_payment_reminder.delay(str(invoice.id))


@shared_task
def send_payment_reminder(invoice_id: str):
    from django.core.mail import EmailMessage

    from apps.invoices.models import Invoice

    invoice = Invoice.objects.select_related("client", "tenant", "created_by").filter(id=invoice_id).first()
    if not invoice:
        return

    owner_email = getattr(invoice.created_by, "email", None)
    client_email = invoice.client.email

    if client_email:
        EmailMessage(
            subject=f"Payment reminder: Invoice {invoice.invoice_number}",
            body=(
                f"Hi {invoice.client.name},\n\n"
                f"This is a reminder that invoice {invoice.invoice_number} "
                f"for {invoice.currency} {invoice.amount_due} was due on {invoice.due_date}.\n\n"
                f"Please arrange payment at your earliest convenience."
            ),
            to=[client_email],
        ).send(fail_silently=True)

    logger.info("Payment reminder sent for invoice %s", invoice.invoice_number)


@shared_task
def generate_recurring_invoices():
    """
    Daily task. Creates new Invoice instances from active RecurringInvoice
    templates whose next_issue_date is today or earlier, then advances
    next_issue_date to the next cycle.

    Add to CELERY_BEAT_SCHEDULE:
        "recurring-invoices-daily": {
            "task": "apps.invoices.tasks.generate_recurring_invoices",
            "schedule": crontab(hour=6, minute=0),
        },
    """
    from apps.invoices.models import Invoice, InvoiceLineItem, RecurringInvoice
    from apps.invoices.services.invoice_service import recalculate_totals

    today = timezone.now().date()
    due = RecurringInvoice.objects.filter(
        is_active=True,
        next_issue_date__lte=today,
        is_deleted=False,
    ).filter(
        models_end_date_filter(today)
    ).select_related("client", "tenant")

    for recurring in due:
        try:
            _generate_from_recurring(recurring, today)
        except Exception:
            logger.exception("Failed to generate invoice from recurring template %s", recurring.id)


def models_end_date_filter(today):
    """Returns a Q object: end_date is null OR end_date >= today."""
    from django.db.models import Q
    return Q(end_date__isnull=True) | Q(end_date__gte=today)


def _generate_from_recurring(recurring, today):
    from apps.invoices.models import Invoice, InvoiceLineItem
    from apps.invoices.services.invoice_service import recalculate_line_item_total, recalculate_totals

    due_date = today + timedelta(days=recurring.due_days)
    invoice = Invoice.objects.create(
        tenant=recurring.tenant,
        client=recurring.client,
        project=recurring.project,
        recurring_invoice=recurring,
        invoice_number=Invoice.generate_invoice_number(recurring.tenant),
        issue_date=today,
        due_date=due_date,
        tax_rate=recurring.tax_rate,
        discount_type=recurring.discount_type,
        discount_value=recurring.discount_value,
        currency=recurring.currency,
        notes=recurring.notes,
    )

    for template_item in recurring.line_items.all():
        li = InvoiceLineItem.objects.create(
            invoice=invoice,
            description=template_item.description,
            quantity=template_item.quantity,
            unit_price=template_item.unit_price,
            total=0,
        )
        recalculate_line_item_total(li)

    recalculate_totals(invoice)

    # Advance next_issue_date
    recurring.next_issue_date = _next_date(recurring.next_issue_date, recurring.frequency)
    recurring.save(update_fields=["next_issue_date"])
    logger.info("Generated invoice %s from recurring template %s", invoice.invoice_number, recurring.id)


def _next_date(current_date, frequency):
    from dateutil.relativedelta import relativedelta

    freq_map = {
        "weekly": timedelta(weeks=1),
        "biweekly": timedelta(weeks=2),
    }
    rel_map = {
        "monthly": relativedelta(months=1),
        "quarterly": relativedelta(months=3),
        "yearly": relativedelta(years=1),
    }
    if frequency in freq_map:
        return current_date + freq_map[frequency]
    return current_date + rel_map[frequency]
