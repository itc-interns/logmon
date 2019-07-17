from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="dashboard"),
    path('viewall/', views.viewall, name="dashboardviewall"),
    path('viewerror/', views.viewerror, name="dashboardviewerror"),
    path('threats/', views.threats, name="dashboardthreats"),

]