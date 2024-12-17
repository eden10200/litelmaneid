from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ユーザーごとにカテゴリを分離

    def __str__(self):
        return self.name

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ユーザーごとに分離
    date = models.DateField()
    store_name = models.CharField(max_length=100, default='')
    amount = models.IntegerField()
  #  transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE)
  #  description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.store_name} - {self.amount}"
