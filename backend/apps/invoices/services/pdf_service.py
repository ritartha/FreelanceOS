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
  .totals td {{ border: none; }}
  .grand-total td {{ font-weight: bold; font-size: 13pt; border-top: 2px solid #6366f1; }}
  .meta {{ color: #6b7280; font-size: 9pt; margin-bottom: 4px; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; background: #e0e7ff; color: #3730a3; font-size: 9pt; }}
</style>
</head>
<body>
<h1>Invoice {invoice_number} <span class="badge">{status}</span></h1>
<p class="meta">Issued: {issue_date} | Due: {due_date} | Currency: {currency}</p>
<table>
  <thead><tr><th>Description</th><th>Qty</th><th>Unit Price</th><th>Total</th></tr></thead>
  <tbody>{line_rows}</tbody>
  <tfoot>
    <tr class="totals"><td colspan="3">Subtotal</td><td style="text-align:right">{currency} {subtotal}</td></tr>
    <tr class="totals"><td colspan="3">Discount</td><td style="text-align:right">- {currency} {discount_amount}</td></tr>
    <tr class="totals"><td colspan="3">Tax ({tax_rate}%)</td><td style="text-align:right">{currency} {tax_amount}</td></tr>
    <tr class="grand-total"><td colspan="3">Total</td><td style="text-align:right">{currency} {total}</td></tr>
    <tr class="totals"><td colspan="3">Amount Paid</td><td style="text-align:right">{currency} {amount_paid}</td></tr>
    <tr class="totals"><td colspan="3"><strong>Amount Due</strong></td><td style="text-align:right"><strong>{currency} {amount_due}</strong></td></tr>
  </tfoot>
</table>
{notes_block}
</body>
</html>
"""


def render_invoice_pdf(invoice) -> bytes:
    line_rows = "".join(
        LINE_ITEM_ROW.format(
            description=li.description,
            quantity=li.quantity,
            unit_price=li.unit_price,
            total=li.total,
        )
        for li in invoice.line_items.all()
    )
    notes_block = f"<p><em>{invoice.notes}</em></p>" if invoice.notes else ""
    html = PDF_TEMPLATE.format(
        invoice_number=invoice.invoice_number,
        status=invoice.get_status_display(),
        issue_date=invoice.issue_date,
        due_date=invoice.due_date,
        currency=invoice.currency,
        line_rows=line_rows,
        subtotal=invoice.subtotal,
        discount_amount=invoice.discount_amount,
        tax_rate=invoice.tax_rate,
        tax_amount=invoice.tax_amount,
        total=invoice.total,
        amount_paid=invoice.amount_paid,
        amount_due=invoice.amount_due,
        notes_block=notes_block,
    )
    return HTML(string=html).write_pdf()
