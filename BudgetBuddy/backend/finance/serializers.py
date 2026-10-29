from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Profile, Expense, Income, Budget, SavingsGoal, Notification

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Profile.objects.get_or_create(user=user)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    class Meta:
        model = Profile
        fields = ["id", "username", "email", "monthly_income", "currency"]

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "title", "amount", "category", "date", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]
    def validate_amount(self, value):
        if value <= 0: raise serializers.ValidationError("Amount must be greater than zero.")
        return value

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ["id", "title", "amount", "source", "date", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]
    def validate_amount(self, value):
        if value <= 0: raise serializers.ValidationError("Amount must be greater than zero.")
        return value

class BudgetSerializer(serializers.ModelSerializer):
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    utilization_percent = serializers.SerializerMethodField()
    class Meta:
        model = Budget
        fields = ["id", "name", "category", "limit_amount", "month", "spent", "remaining", "utilization_percent"]
        read_only_fields = ["id", "spent", "remaining", "utilization_percent"]
    def get_spent(self, obj): return obj.spent_amount()
    def get_remaining(self, obj): return obj.limit_amount - obj.spent_amount()
    def get_utilization_percent(self, obj):
        if not obj.limit_amount: return 0
        return min(999, round(float(obj.spent_amount() / obj.limit_amount * 100), 1))
    def validate_limit_amount(self, value):
        if value <= 0: raise serializers.ValidationError("Budget must be greater than zero.")
        return value

class SavingsGoalSerializer(serializers.ModelSerializer):
    progress_percent = serializers.SerializerMethodField()
    class Meta:
        model = SavingsGoal
        fields = ["id", "name", "target_amount", "saved_amount", "target_date", "completed", "progress_percent"]
        read_only_fields = ["id", "progress_percent"]
    def validate(self, attrs):
        target = attrs.get("target_amount", getattr(self.instance, "target_amount", 0))
        saved = attrs.get("saved_amount", getattr(self.instance, "saved_amount", 0))
        if target <= 0: raise serializers.ValidationError({"target_amount": "Target must be greater than zero."})
        if saved < 0: raise serializers.ValidationError({"saved_amount": "Saved amount cannot be negative."})
        return attrs
    def get_progress_percent(self, obj): return obj.progress_percent()

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "message", "read", "created_at"]
        read_only_fields = ["id", "message", "created_at"]
