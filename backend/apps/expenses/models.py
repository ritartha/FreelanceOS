from django.db import models

from apps.common.models import TenantAwareModel


class Expense(TenantAwareModel):
    class CategoryChoices(models.TextChoices):
        TRAVEL = "travel", "Travel"
        SOFTWARE = "software", "Software"
        OFFICE = "office", "Office"
        OTHER = "other", "Other"

    project = models.ForeignKey("projects.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="expenses")
    category = models.CharField(max_length=50, choices=CategoryChoices.choices, default=CategoryChoices.OTHER)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    expense_date = models.DateField()
    receipt = models.ImageField(upload_to="expenses/receipts/", null=True, blank=True)
    is_billable = models.BooleanField(default=False)
    is_reimbursable = models.BooleanField(default=False)

    class Meta:
        db_table = "expenses_expense"

    def __str__(self):
        return f"{self.category}: {self.amount}"
