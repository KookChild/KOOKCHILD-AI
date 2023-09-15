from rest_framework import serializers
from .models import *

class DataFrameSerializer(serializers.Serializer):
  CATEGORY = serializers.ListField(source='CATEGORY.tolist()')
  SUM_AMOUNT = serializers.ListField(source='SUM_AMOUNT.tolist()')
  COUNT = serializers.ListField(source='COUNT.tolist()')
