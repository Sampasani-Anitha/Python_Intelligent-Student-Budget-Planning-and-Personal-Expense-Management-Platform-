import csv
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Profile, Expense, Income, Budget, SavingsGoal, Notification
from .serializers import (
    RegisterSerializer, ProfileSerializer, ExpenseSerializer, IncomeSerializer,
    BudgetSerializer, SavingsGoalSerializer, NotificationSerializer
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class OwnedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExpenseViewSet(OwnedViewSet):
    serializer_class = ExpenseSerializer
    def get_queryset(self): return Expense.objects.filter(user=self.request.user)

class IncomeViewSet(OwnedViewSet):
    serializer_class = IncomeSerializer
    def get_queryset(self): return Income.objects.filter(user=self.request.user)

class BudgetViewSet(OwnedViewSet):
    serializer_class = BudgetSerializer
    def get_queryset(self): return Budget.objects.filter(user=self.request.user)

class SavingsGoalViewSet(OwnedViewSet):
    serializer_class = SavingsGoalSerializer
    def get_queryset(self): return SavingsGoal.objects.filter(user=self.request.user)
    def perform_update(self, serializer):
        goal = serializer.save()
        if goal.saved_amount >= goal.target_amount and not goal.completed:
            goal.completed = True
            goal.save(update_fields=["completed"])

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self): return Notification.objects.filter(user=self.request.user)

@api_view(["GET", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "GET":
        return Response(ProfileSerializer(profile).data)
    serializer = ProfileSerializer(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_view(request):
    today = timezone.localdate()
    month_expenses = Expense.objects.filter(user=request.user, date__year=today.year, date__month=today.month)
    month_incomes = Income.objects.filter(user=request.user, date__year=today.year, date__month=today.month)
    total_expenses = month_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    total_income = month_incomes.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    categories = list(month_expenses.values("category").annotate(total=Sum("amount")).order_by("-total"))
    recent_expenses = ExpenseSerializer(Expense.objects.filter(user=request.user)[:5], many=True).data
    budgets = Budget.objects.filter(user=request.user, month__year=today.year, month__month=today.month)
    budget_rows = BudgetSerializer(budgets, many=True).data
    # Keep one current notification per over-limit budget; avoid creating duplicates on every dashboard refresh.
    for b in budgets:
        spent = b.spent_amount()
        if spent > b.limit_amount and not Notification.objects.filter(
            user=request.user, message=f"Budget alert: {b.category} spending exceeded your monthly limit."
        ).exists():
            Notification.objects.create(user=request.user, message=f"Budget alert: {b.category} spending exceeded your monthly limit.")
    return Response({
        "month": today.strftime("%Y-%m"),
        "total_income": str(total_income),
        "total_expenses": str(total_expenses),
        "balance": str(total_income - total_expenses),
        "category_spending": categories,
        "recent_expenses": recent_expenses,
        "budgets": budget_rows,
        "savings_goals": SavingsGoalSerializer(SavingsGoal.objects.filter(user=request.user), many=True).data,
    })

def csv_response(queryset, fields, filename):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(fields)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in fields])
    return response

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def export_expenses_csv(request):
    return csv_response(Expense.objects.filter(user=request.user), ["date", "title", "category", "amount", "notes"], "budgetbuddy-expenses.csv")

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def export_incomes_csv(request):
    return csv_response(Income.objects.filter(user=request.user), ["date", "title", "source", "amount", "notes"], "budgetbuddy-incomes.csv")
