import re

from apps.proposals.models import ProposalVariable

VARIABLE_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


def render_variables(body_markdown: str, tenant, overrides: dict | None = None) -> str:
    """
    Replace {{variable}} placeholders in body_markdown.

    Resolution order per variable: overrides dict > ProposalVariable.default_value
    for the tenant > left untouched if no value is found anywhere.
    """
    overrides = overrides or {}
    defaults = {
        v.key: v.default_value for v in ProposalVariable.objects.filter(tenant=tenant)
    }

    def _replace(match):
        key = match.group(1)
        if key in overrides and overrides[key]:
            return str(overrides[key])
        if key in defaults:
            return defaults[key]
        return match.group(0)  # leave placeholder as-is if unresolved

    return VARIABLE_PATTERN.sub(_replace, body_markdown or "")


def extract_variable_keys(body_markdown: str) -> list[str]:
    """List the distinct {{variable}} keys referenced in a template body."""
    return sorted(set(VARIABLE_PATTERN.findall(body_markdown or "")))
