from django.urls import path
from underdog import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    #path('', views.home, name='underdog-home'),
    #path('about/', views.about, name='underdog-about'),
    path('', views.home, name='home'),
]

urlpatterns += staticfiles_urlpatterns()