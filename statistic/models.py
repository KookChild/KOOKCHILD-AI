# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

# 가장 기본 Users
class Users(models.Model):
    id = models.BigIntegerField(primary_key=True)
    created_date = models.DateTimeField(blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    birthdate = models.DateTimeField(blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    is_parent = models.BooleanField()
    name = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    phone_num = models.CharField(max_length=255, blank=True, null=True)
    ssn = models.CharField(max_length=255, blank=True, null=True)
    
    
    
    # is_authenticated = models.BooleanField()
    # is_anonymous = models.BooleanField()
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []

    class Meta:
        managed = False
        db_table = 'users'

class Account(models.Model):
    id = models.BigIntegerField(primary_key=True)
    created_date = models.DateTimeField(blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    balance = models.BigIntegerField(blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    account_history = models.ForeignKey('AccountHistory', models.DO_NOTHING, blank=True, null=True, related_name='accountHistory')
    user = models.ForeignKey(Users, models.DO_NOTHING, blank=True, null=True, related_name='user_account')
    account_num = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'account'


class AccountHistory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    created_date = models.DateTimeField(blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    amount = models.BigIntegerField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    is_deposit = models.BooleanField()
    target_name = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.BigIntegerField(blank=True, null=True)
    account = models.ForeignKey(Account, models.DO_NOTHING, blank=True, null=True, related_name='account')

    class Meta:
        managed = False
        db_table = 'account_history'

class ParentChild(models.Model):

    id = models.BigIntegerField(primary_key=True)
    created_date = models.DateTimeField(blank=True, null=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    level1reward = models.IntegerField()
    level2reward = models.IntegerField()
    level3reward = models.IntegerField()
    child = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    parent = models.ForeignKey('Users', models.DO_NOTHING, related_name='parentchild_parent_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parent_child'
