"""
Renders a Proposal's markdown body to PDF via markdown -> HTML -> WeasyPrint.

Both libraries are already in requirements/base.txt (markdown, weasyprint),
so no new dependency is introduced here.
"""

import markdown as md
from weasyprint import HTML

PDF_TEMPLATE = """
<html>
<head>
<style>
  body {{ font-family: 'Helvetica', sans-serif; padding: 2.5cm; color: #1f2937; }}
  h1 {{ font-size: 22pt; border-bottom: 2px solid #6366f1; padding-bottom: 8px; }}
  h2 {{ font-size: 15pt; color: #4338ca; margin-top: 24px; }}
  code {{ background: #f3f4f6; padding: 2px 5px; border-radius: 4px; }}
  pre {{ background: #f3f4f6; padding: 12px; border-radius: 6px; overflow-x: auto; }}
</style>
</head>
<body>
<h1>{title}</h1>
{content}
</body>
</html>
"""


def render_proposal_pdf(proposal) -> bytes:
    """Returns PDF bytes for the given Proposal instance."""
    html_body = md.markdown(proposal.body_markdown or "", extensions=["fenced_code", "tables"])
    full_html = PDF_TEMPLATE.format(title=proposal.title, content=html_body)
    return HTML(string=full_html).write_pdf()
