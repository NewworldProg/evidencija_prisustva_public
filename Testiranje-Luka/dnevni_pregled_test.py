import os
import sys
import django
from datetime import date
from collections import defaultdict  #✅ OVO DODATO

#Dodaj korenski folder u sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#ostavi Django settings (promeni ako se zove drugačije!)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evidencija.settings')

#Pokreni Django
django.setup()

#Import modela
from prisustvo.models import Zaposleni, PrisustvoNaDan

#Današnji datum
danas = date.today()

#Rečnici za organizaciju podataka
tabela = defaultdict(list)

#Uzimanje svih različitih uprava
uprave = Zaposleni.objects.values_list('uprava', flat=True).distinct()

#Iteracija po upravama
for uprava_id in uprave:
    zaposleni_uprave = Zaposleni.objects.filter(uprava_id=uprava_id)
    prisustva = PrisustvoNaDan.objects.filter(
        datum=danas,
        zaposleni__in=zaposleni_uprave
    ).select_related('zaposleni')

    tabela[uprava_id] = prisustva

#Štampanje rezultata
for uprava_id, prisustva in tabela.items():
    print(f"\n📋 Uprava ID {uprava_id}")
    for p in prisustva:
        print(f"- {p.zaposleni.ime_prezime} ({p.zaposleni.cin}): {p.status}")
