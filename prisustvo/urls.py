from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('jutarnji-unos/', views.jutarnji_unos_view, name='jutarnji_unos'),
    path('dnevni-pregled/', views.dnevni_pregled_view, name='dnevni_pregled'),
    path('mesecni/', views.mesecni_pregled_view, name='mesecni_pregled'),
    path('godisnji/', views.godisnji_pregled_view, name='godisnji_pregled'),
    path('privatno/', views.privatna_stranica, name='privatno'),
    ]

