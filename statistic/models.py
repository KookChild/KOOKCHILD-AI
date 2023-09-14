from typing import Any
from django.db import models

# Create your models here.

class Account_history(models.Model):
  user_id = models.IntegerField()
  # pub_date = models.DateTimeField('date published')
  amount = models.IntegerField()
  crdt_date = models.DateTimeField()
  category = models.CharField(max_length=200)
  is_deposit = models.IntegerField()
  modified_date = models.DateTimeField()
  account_number = models.CharField(max_length=100)
  target_name = models.CharField(max_length=100)
  

  def __str__(self) :
    return self


  class Meta:
    permissions = [
    ("can_view_account_history", "Can view Account History"),

    ]
    db_table_name = 'account_history'