from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('jutarnji-unos/', views.jutarnji_unos_view, name='jutarnji_unos'),
    path('jutarnji-dash/', views.jutarnji_dash_view, name='jutarnji_dash'),
    path('mesecni/', views.mesecni_pregled_view, name='mesecni_pregled'),
    path('godisnji/', views.godisnji_pregled_view, name='godisnji_pregled'),
    path('privatno/', views.privatna_stranica, name='privatno'),
    ]

