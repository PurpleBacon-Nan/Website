from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Space(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class FishStock(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    space = models.ForeignKey(Space, related_name='fish_stocks', on_delete=models.CASCADE,default=1)

    def __str__(self):
        return f"{self.name} - {self.quantity} units"

class MoneyStock (models.Model):
    balance = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Balance: {self.balance} CFA"

class FishStockLog(models.Model):
    fish = models.ForeignKey(FishStock, on_delete=models.CASCADE)
    action = models.CharField(max_length=10)
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} {self.quantity} units of {self.fish.name} at {self.timestamp}"

class MoneyStockLog(models.Model):
    balance = models.ForeignKey(MoneyStock, on_delete=models.CASCADE)
    action = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} {self.amount} CFA at {self.timestamp}"

