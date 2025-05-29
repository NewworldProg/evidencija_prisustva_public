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

prisustva_dict = {
    p.zaposleni_id: p for p in PrisustvoNaDan.objects.filter(datum=danas)
}

print(prisustva_dict)
