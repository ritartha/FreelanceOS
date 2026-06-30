from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from apps.quotations.models import Quotation, QuotationLineItem, QuotationVersion

TWO_PLACES = Decimal("0.01")


def _round(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


@transaction.atomic
def recalculate_totals(quotation: Quotation) -> Quotation:
    """
    Recompute subtotal -> discount -> GST/tax -> total from the quotation's
    line items. Order matters: discount is applied to the subtotal first,
    then tax is calculated on the discounted amount (standard GST practice).
    """
    subtotal = sum((li.total for li in quotation.line_items.all()), Decimal("0"))

    if quotation.discount_type == "percent":
        discount_amount = subtotal * (quotation.discount_value / Decimal("100"))
    else:
        discount_amount = quotation.discount_value

    discount_amount = min(discount_amount, subtotal)  # never discount below zero
    taxable_amount = subtotal - discount_amount
    tax_amount = taxable_amount * (quotation.tax_rate / Decimal("100"))
    total = taxable_amount + tax_amount

    quotation.subtotal = _round(subtotal)
    quotation.discount_amount = _round(discount_amount)
    quotation.tax_amount = _round(tax_amount)
    quotation.total = _round(total)
    quotation.save(update_fields=["subtotal", "discount_amount", "tax_amount", "total", "updated_at"])

    return quotation


def recalculate_line_item_total(line_item: QuotationLineItem) -> QuotationLineItem:
    line_item.total = _round(line_item.quantity * line_item.unit_price)
    line_item.save(update_fields=["total"])
    return line_item


def _serialize_snapshot(quotation: Quotation) -> dict:
    return {
        "quotation_number": quotation.quotation_number,
        "status": quotation.status,
        "subtotal": str(quotation.subtotal),
        "discount_type": quotation.discount_type,
        "discount_value": str(quotation.discount_value),
        "discount_amount": str(quotation.discount_amount),
        "tax_rate": str(quotation.tax_rate),
        "tax_amount": str(quotation.tax_amount),
        "total": str(quotation.total),
        "notes": quotation.notes,
        "line_items": [
            {
                "description": li.description,
                "quantity": str(li.quantity),
                "unit_price": str(li.unit_price),
                "total": str(li.total),
            }
            for li in quotation.line_items.all()
        ],
        "snapshotted_at": timezone.now().isoformat(),
    }


@transaction.atomic
def snapshot_version(quotation: Quotation, user=None) -> QuotationVersion:
    """Write an immutable version snapshot of the quotation's current state."""
    next_version = quotation.versions.count() + 1
    return QuotationVersion.objects.create(
        tenant=quotation.tenant,
        quotation=quotation,
        version_number=next_version,
        snapshot=_serialize_snapshot(quotation),
        created_by=user,
    )
