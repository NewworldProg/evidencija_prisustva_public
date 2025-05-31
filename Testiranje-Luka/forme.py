import os
import sys

# Dodaj root folder projekta u sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Podesi Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evidencija.settings')

import django
django.setup()

from prisustvo.forms import PrisustvoZaZaposlenogForm
from django.contrib.auth.models import AnonymousUser

fake_data = {
    'zaposleni': 1,
    'status': '+'
}
form = PrisustvoZaZaposlenogForm(data=fake_data)

if form.is_valid():
    print("Forma validna!")
else:
    print("Greške:", form.errors)


from prisustvo.forms import PrisustvoNaDanForm

fake_data = {
    'zaposleni': 1,  
    'status': '+'
}

form = PrisustvoNaDanForm(data=fake_data)

if form.is_valid():
    print("✅ Forma PrisustvoNaDanForm je validna.")
    print("Zaposleni ID:", form.cleaned_data['zaposleni'])
    print("Status:", form.cleaned_data['status'])
else:
    print("❌ Greške:", form.errors)


from prisustvo.forms import FilterForma

fake_data = {
    'godina': 2025,
    'mesec': 5,
    'uprava': '', 
    'zaposleni': ''
}

form = FilterForma(data=fake_data)

if form.is_valid():
    print("✅ FilterForma je validna.")
    print("Godina:", form.cleaned_data['godina'])
    print("Mesec:", form.cleaned_data['mesec'])
else:
    print("❌ Greške:", form.errors)
