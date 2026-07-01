import markdown as md
from weasyprint import HTML

PDF_TEMPLATE = """
<html>
<head>
<style>
  body {{ font-family: 'Helvetica', sans-serif; padding: 2.5cm; color: #1f2937; font-size: 11pt; }}
  h1 {{ font-size: 20pt; border-bottom: 2px solid #6366f1; padding-bottom: 8px; }}
  h2 {{ font-size: 14pt; color: #4338ca; margin-top: 24px; }}
  p {{ line-height: 1.6; }}
  .meta {{ color: #6b7280; font-size: 9pt; margin-bottom: 4px; }}
  .signature-block {{ margin-top: 60px; border-top: 1px solid #e5e7eb; padding-top: 16px; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="meta">Status: {status} | Start: {start_date} | End: {end_date}</p>
{content}
<div class="signature-block">
  <p><strong>Client signature:</strong> {client_signature_name}</p>
  <p><strong>Signed at:</strong> {signed_at}</p>
</div>
</body>
</html>
"""


def render_contract_pdf(contract) -> bytes:
    html_body = md.markdown(contract.body_markdown or "", extensions=["fenced_code", "tables"])
    full_html = PDF_TEMPLATE.format(
        title=contract.title,
        status=contract.get_status_display(),
        start_date=contract.start_date or "N/A",
        end_date=contract.end_date or "Open-ended",
        content=html_body,
        client_signature_name=contract.client_signature_name or "—",
        signed_at=contract.signed_at.strftime("%Y-%m-%d %H:%M UTC") if contract.signed_at else "—",
    )
    return HTML(string=full_html).write_pdf()
