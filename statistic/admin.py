from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import *

admin.site.register(Account)
admin.site.register(Users)
admin.site.register(AccountHistory)
admin.site.register(ParentChild)

