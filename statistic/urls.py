# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('/graph', views.graph_api, name='graph_api'),
]
