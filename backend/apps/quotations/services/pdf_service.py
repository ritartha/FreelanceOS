"""
PDF export for quotations via WeasyPrint (same library/pattern as
apps.proposals.services.pdf_service).
"""

from weasyprint import HTML

LINE_ITEM_ROW = """
<tr>
  <td>{description}</td>
  <td style="text-align:right">{quantity}</td>
  <td style="text-align:right">{unit_price}</td>
  <td style="text-align:right">{total}</td>
</tr>
"""

PDF_TEMPLATE = """
<html>
<head>
<style>
  body {{ font-family: 'Helvetica', sans-serif; padding: 2.5cm; color: #1f2937; font-size: 11pt; }}
  h1 {{ font-size: 20pt; border-bottom: 2px solid #6366f1; padding-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
  th, td {{ padding: 8px; border-bottom: 1px solid #e5e7eb; }}
  th {{ text-align: left; background: #f3f4f6; }}
  .totals td {{ border: none; font-weight: bold; }}
  .meta {{ color: #6b7280; font-size: 9pt; margin-bottom: 4px; }}
</style>
</head>
<body>
<h1>Quotation {quotation_number}</h1>
<p class="meta">Issued: {issue_date} | Valid until: {valid_until}</p>
<p class="meta">GSTIN: {gst_number}</p>
<table>
  <thead><tr><th>Description</th><th>Qty</th><th>Unit Price</th><th>Total</th></tr></thead>
  <tbody>{line_rows}</tbody>
  <tfoot>
    <tr class="totals"><td colspan="3">Subtotal</td><td style="text-align:right">{currency} {subtotal}</td></tr>
    <tr class="totals"><td colspan="3">Discount</td><td style="text-align:right">- {currency} {discount_amount}</td></tr>
    <tr class="totals"><td colspan="3">Tax ({tax_rate}%)</td><td style="text-align:right">{currency} {tax_amount}</td></tr>
    <tr class="totals"><td colspan="3">Total</td><td style="text-align:right">{currency} {total}</td></tr>
  </tfoot>
</table>
{notes_block}
</body>
</html>
"""


def render_quotation_pdf(quotation) -> bytes:
    """Returns PDF bytes for the given Quotation instance."""
    line_rows = "".join(
        LINE_ITEM_ROW.format(
            description=li.description,
            quantity=li.quantity,
            unit_price=li.unit_price,
            total=li.total,
        )
        for li in quotation.line_items.all()
    )
    notes_block = f"<p>{quotation.notes}</p>" if quotation.notes else ""

    html = PDF_TEMPLATE.format(
        quotation_number=quotation.quotation_number,
        issue_date=quotation.issue_date,
        valid_until=quotation.valid_until or "N/A",
        gst_number=quotation.gst_number or "N/A",
        line_rows=line_rows,
        currency=quotation.currency,
        subtotal=quotation.subtotal,
        discount_amount=quotation.discount_amount,
        tax_rate=quotation.tax_rate,
        tax_amount=quotation.tax_amount,
        total=quotation.total,
        notes_block=notes_block,
    )
    return HTML(string=html).write_pdf()
