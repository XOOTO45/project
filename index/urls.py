from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('load_capacity/', views.loadCapacity),
    path('creating_a_loader/', views.creatingALoader),
    path('load/', views.chunkLoad),
    path('download/', views.download)
]
