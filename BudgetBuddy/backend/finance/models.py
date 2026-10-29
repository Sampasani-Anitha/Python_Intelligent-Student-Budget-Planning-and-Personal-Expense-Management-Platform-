from django.conf import settings
from django.db import models
from django.db.models import Sum
from decimal import Decimal

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="INR")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Category(models.TextChoices):
    FOOD = "Food", "Food"
    TRAVEL = "Travel", "Travel"
    SHOPPING = "Shopping", "Shopping"
    EDUCATION = "Education", "Education"
    ENTERTAINMENT = "Entertainment", "Entertainment"
    MISCELLANEOUS = "Miscellaneous", "Miscellaneous"

class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expenses")
    title = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.MISCELLANEOUS)
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} - {self.amount}"

class Income(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="incomes")
    title = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=80, default="Pocket money")
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} - {self.amount}"

class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=Category.choices)
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.DateField(help_text="Use the first day of the budget month")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-month", "category"]
        constraints = [
            models.UniqueConstraint(fields=["user", "category", "month"], name="unique_user_category_budget_month")
        ]

    def spent_amount(self):
        return Expense.objects.filter(
            user=self.user, category=self.category,
            date__year=self.month.year, date__month=self.month.month
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    def __str__(self):
        return f"{self.name} ({self.month:%Y-%m})"

class SavingsGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals")
    name = models.CharField(max_length=120)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def progress_percent(self):
        if not self.target_amount:
            return 0
        return min(100, round(float(self.saved_amount / self.target_amount * 100), 1))

    def __str__(self):
        return self.name

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
