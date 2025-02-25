from django.contrib import admin
from .models import FishStock, MoneyStock
# Register your models here.

admin.site.register(FishStock)
admin.site.register(MoneyStock)