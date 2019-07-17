from django.contrib import admin
from django.urls import path, include
from . import views
import re
urlpatterns = [
    path('statuscodehits/', views.statuscodehits, name="statuscodehits"),
    path('bots/', views.webrobots, name="bots"),
    path('error/<str:ip>/<path:req>/<str:time>/<str:date>/', views.errorlog, name="errorlog"),
    path('statuscodeips/<int:statuscode>/', views.statuscodeips, name="statuscodeips"),
    path('statuscodepercent/', views.statuscodepercent, name="statuscodepercent"),
    path('apihits/<int:offset>/', views.apihits, name="apihits"),
    path('unauthorizedips/<int:offset>/', views.unauthorizedips, name="unauthorizedips"),
    path('authorizedips/<int:offset>/', views.authorizedips, name="authorizedips"),
    path('hitcounts/', views.hitcounts, name="hitcounts"),
    path('linegraphhits/<str:period>/', views.linegraphhits, name="linegraphhits"),
    path('threatips/', views.threatips, name="threatips"),
    path('heatmaplocations/', views.heatmaplocations, name="heatmaplocations"),
    path('statuscodecsv/<int:category>/', views.statuscodecsv, name="statuscodecsv"),
    path('graphAreaData/', views.graphAreaData, name="graphAreaData"),
    path('findlocation/<str:location>/', views.findlocation, name="findlocation"),
    path('tableAreaData/', views.tableAreaData, name="tableAreaData"),
    path('errorgraph',views.error_graph, name="errorgraph"),    
]