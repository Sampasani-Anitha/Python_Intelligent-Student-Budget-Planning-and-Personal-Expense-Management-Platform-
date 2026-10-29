from django.contrib import admin
from .models import Profile, Expense, Income, Budget, SavingsGoal, Notification
admin.site.register(Profile)
admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(Budget)
admin.site.register(SavingsGoal)
admin.site.register(Notification)
