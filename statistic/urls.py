# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
  path('graph/parent', views.graph_api_parent, name='graph_api_parent'),
  path('graph/child', views.graph_api_child, name='graph_api_child'),
]
