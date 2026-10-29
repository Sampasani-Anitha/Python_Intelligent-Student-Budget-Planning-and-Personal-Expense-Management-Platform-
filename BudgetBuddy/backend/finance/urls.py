from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExpenseViewSet, IncomeViewSet, BudgetViewSet, SavingsGoalViewSet,
    NotificationViewSet, profile_view, dashboard_view,
    export_expenses_csv, export_incomes_csv
)
router = DefaultRouter()
router.register("expenses", ExpenseViewSet, basename="expense")
router.register("incomes", IncomeViewSet, basename="income")
router.register("budgets", BudgetViewSet, basename="budget")
router.register("goals", SavingsGoalViewSet, basename="goal")
router.register("notifications", NotificationViewSet, basename="notification")
urlpatterns = [
    path("", include(router.urls)),
    path("profile/", profile_view),
    path("dashboard/", dashboard_view),
    path("reports/expenses.csv", export_expenses_csv),
    path("reports/incomes.csv", export_incomes_csv),
]
