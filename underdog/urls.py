from django.urls import path
from underdog import views

urlpatterns = [
    #path('', views.home, name='underdog-home'),
    #path('about/', views.about, name='underdog-about'),
    path('', views.home, name='home'),
]