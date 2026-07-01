from weasyprint import HTML


def _table(headers: list, rows: list) -> str:
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = ""
    for row in rows:
        td = "".join(f"<td>{v}</td>" for v in row)
        body += f"<tr>{td}</tr>"
    return f"<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>"


REPORT_CSS = """
<style>
  body {{ font-family: Helvetica, sans-serif; padding: 1.5cm; color: #1f2937; font-size: 10pt; }}
  h1 {{ font-size: 18pt; color: #6366f1; border-bottom: 2px solid #6366f1; padding-bottom: 6px; }}
  h2 {{ font-size: 13pt; color: #374151; margin-top: 20px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
  th {{ background: #f3f4f6; text-align: left; padding: 6px 8px; font-size: 9pt; }}
  td {{ padding: 5px 8px; border-bottom: 1px solid #e5e7eb; }}
  .summary {{ display: flex; gap: 20px; margin: 16px 0; }}
  .kpi {{ background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px 16px; flex: 1; }}
  .kpi-label {{ font-size: 8pt; color: #6b7280; }}
  .kpi-value {{ font-size: 15pt; font-weight: bold; color: #111827; }}
  .meta {{ color: #9ca3af; font-size: 8pt; margin-bottom: 16px; }}
</style>
"""


def render_profit_report_pdf(tenant, start_date=None, end_date=None) -> bytes:
    from apps.reports.services.report_service import (
        get_monthly_trends,
        get_profit_summary,
        get_top_clients,
    )

    profit = get_profit_summary(tenant, start_date, end_date)
    trends = get_monthly_trends(tenant, start_date, end_date)
    top_clients = get_top_clients(tenant, start_date, end_date, limit=10)

    period = f"{start_date or 'All time'} → {end_date or 'present'}"

    trends_table = _table(
        ["Month", "Revenue", "Expenses", "Profit"],
        [(r["month"], r["revenue"], r["expenses"], r["profit"]) for r in trends],
    )
    clients_table = _table(
        ["Client", "Total Invoiced", "Invoices"],
        [(r["client_name"], r["total_invoiced"], r["invoice_count"]) for r in top_clients],
    )

    html = f"""
    <html><head>{REPORT_CSS}</head><body>
    <h1>Profit & Revenue Report</h1>
    <p class="meta">Period: {period}</p>

    <div class="summary">
      <div class="kpi"><div class="kpi-label">Revenue</div><div class="kpi-value">{profit['revenue']}</div></div>
      <div class="kpi"><div class="kpi-label">Expenses</div><div class="kpi-value">{profit['expenses']}</div></div>
      <div class="kpi"><div class="kpi-label">Profit</div><div class="kpi-value">{profit['profit']}</div></div>
      <div class="kpi"><div class="kpi-label">Margin</div><div class="kpi-value">{profit['margin_percent']}%</div></div>
    </div>

    <h2>Monthly Trends</h2>
    {trends_table}

    <h2>Top Clients</h2>
    {clients_table}
    </body></html>
    """
    return HTML(string=html).write_pdf()
