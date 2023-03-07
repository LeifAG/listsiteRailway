from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('registrera/', views.registrera, name='registrera'),
    path('loggain/',auth_views.LoginView.as_view(template_name='listapp/loggain.html'),name='loggain'),
    path('loggaut/',auth_views.LogoutView.as_view(),name='loggaut'),

    path('', views.AllaListor.as_view(), name='listor-hem'),
    path('lista/<int:pk>/', views.EnLista.as_view(), name='lista-sida'),
    path('lista/<int:pk>/uppdatera/', views.UppdateraLista.as_view(), name='lista-uppdatera'),
    path('lista/<int:pk>/radera/', views.RaderaLista.as_view(), name='lista-radera'),
    path('lista/ny/', views.SkapaLista.as_view(), name='lista-ny'),
    path('lista/<int:pk>/dela/', views.SharedListCreateView.as_view(), name='lista-dela'),

    path('rensa/<int:l_pk>/', views.RaderaPurchasedObject.as_view(), name='object-rensa'),


    path('object/<int:pk>/uppdatera/', views.UppdateraObject.as_view(), name='object-uppdatera'),
    path('object/<int:pk>/radera/', views.RaderaObject.as_view(), name='object-radera'),
    path('object/<int:l_pk>/ny/', views.SkapaObject.as_view(), name='object-ny'),



]