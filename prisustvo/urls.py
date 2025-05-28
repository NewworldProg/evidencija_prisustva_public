from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('jutarnji/', views.jutarnji_unos_view, name='jutarnji_unos'),
    path('mesecni/', views.mesecni_pregled_view, name='mesecni_pregled'),
    path('godisnji/', views.godisnji_pregled_view, name='godisnji_pregled'),
    path('privatno/', views.privatna_stranica, name='privatno'),
    path('accounts/', include('django.contrib.auth.urls')),  # ⬅️ login/logout/password
]
