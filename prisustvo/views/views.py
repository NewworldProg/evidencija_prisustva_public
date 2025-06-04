from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import date
from django.contrib import messages
from collections import Counter

from ..models import PrisustvoNaDan, PrisustvoMesec, Zaposleni, Uprava
from ..forms import FilterForma

# Servisi po view-ovima
from .services.jutarnji_unos.forme_za_izmenu_statusa import FormeZaIzmenuStatusa
from .services.jutarnji_unos.preuzimanje_statusa_iz_forme import PreuzimanjeStatusaIzForme
from .services.dnevni_pregled.statistika import pripremi_statistiku_po_upravama
from .services.mesecni_pregled.statistika import (
    izracunaj_statistiku_po_zaposlenima,
    izracunaj_statistiku_za_upravu
)
from prisustvo.views.services.mesecni_pregled.forms import MesecGodinaFilterForma

# Zajedničke logike
from .services.zajednicko.sortiranje_po_upravama import SortiranjePoUpravama



def home_view(request):
    return render(request, 'prisustvo/home.html')


@login_required
def jutarnji_unos_view(request):
    today = timezone.now().date()
    prisustva_dict = {
        p.zaposleni_id: p
        for p in PrisustvoNaDan.objects.filter(datum=today)
    }

    uprava_map = {}
    uprava_map = SortiranjePoUpravama.superuser(request, uprava_map)
    uprava_map = SortiranjePoUpravama.user(request, uprava_map)

    if request.method == 'POST':
        formovi_po_upravama = FormeZaIzmenuStatusa.izmena(request, uprava_map)
        validno, sve_forme, nevalidni_zaposleni = PreuzimanjeStatusaIzForme.validiranje_forme(formovi_po_upravama)

        if validno:
            statusi_i_zaposleni = PreuzimanjeStatusaIzForme.statusi(sve_forme)

            for zaposleni, status in statusi_i_zaposleni:
                PrisustvoNaDan.objects.update_or_create(
                    zaposleni=zaposleni,
                    datum=today,
                    defaults={'status': status}
                )
                PrisustvoMesec.objects.update_or_create(
                    zaposleni=zaposleni,
                    godina=today.year,
                    mesec=today.month,
                    dan=today.day,
                    defaults={'status': status}
                )

            messages.success(request, "✅ Prisustvo uspešno sačuvano.")
            return redirect('dnevni_pregled')
        #else:
            if nevalidni_zaposleni:
                imena = ', '.join(z.ime_prezime for z in nevalidni_zaposleni)
                poruka = f"❌ Sledeći zaposleni nemaju unet status: {imena}."
            else:
                poruka = "❌ Greška u formi."

            messages.error(request, poruka)
    else:
        formovi_po_upravama = FormeZaIzmenuStatusa.initial_forme(uprava_map, prisustva_dict)

    return render(request, 'prisustvo/jutarnji_unos.html', {
        'formovi_po_upravama': formovi_po_upravama,
        'danas': today
    })


@login_required
def dnevni_pregled_view(request):
    today = timezone.now().date()

    uprava_map = {}
    uprava_map = SortiranjePoUpravama.superuser(request, uprava_map)
    uprava_map = SortiranjePoUpravama.user(request, uprava_map)

    tabela, statistike = pripremi_statistiku_po_upravama(uprava_map, today)

    return render(request, 'prisustvo/dnevni_pregled.html', {
        'tabela': tabela,
        'statistike': statistike,
        'danas': today
    })


@login_required
def privatna_stranica(request):
    return render(request, 'prisustvo/privatno.html')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def mesecni_pregled_view(request):
    danas = date.today()
    forma = FilterForma(request.GET or None, initial={
    'mesec': danas.month,
    'godina': danas.year
    }, user=request.user)
    godina_str = request.GET.get('godina')
    mesec_str = request.GET.get('mesec')
    uprava_id = request.GET.get('uprava')
    zaposleni_id = request.GET.get('zaposleni')

    if not request.user.is_superuser and hasattr(request.user, 'zaposleni'):
        uprava_id = request.user.zaposleni.uprava.id

    godina = int(godina_str) if godina_str else danas.year
    mesec = int(mesec_str) if mesec_str else danas.month

    evidencija_forma = MesecGodinaFilterForma(request.GET)
    if evidencija_forma.is_valid():
        evidencija = evidencija_forma.filtriraj(godina, mesec)
    else:
        evidencija = PrisustvoMesec.objects.none()

    # Sortirani zaposleni po upravi
    if uprava_id:
        zaposlenici = SortiranjePoUpravama.zaposleni_iz_uprave(request, uprava_id)
    else:
        # Ako nije izabrana uprava i superuser je, prikaži sve
        svi_zaposleni = {}
        svi_zaposleni = SortiranjePoUpravama.superuser(request, svi_zaposleni)
        zaposlenici = [z for zaposleni_qs in svi_zaposleni.values() for z in zaposleni_qs]

    if zaposleni_id:
        zaposlenici = [z for z in zaposlenici if z.id == int(zaposleni_id)]

    tabela = {}
    for z in zaposlenici:
        tabela[z] = {}
        for dan in range(1, 32):
            zapis = evidencija.filter(zaposleni=z, dan=dan).first()
            tabela[z][dan] = zapis.status if zapis else ''

    dani = list(range(1, 32))
    statistike_po_zaposlenima = izracunaj_statistiku_po_zaposlenima(zaposlenici, evidencija)
    statistika_uprave = izracunaj_statistiku_za_upravu(zaposlenici, evidencija)

    if uprava_id:
        zaposleni_iz_uprave = Zaposleni.objects.filter(uprava__id=uprava_id).first()
        naziv_uprave = zaposleni_iz_uprave.uprava.naziv if zaposleni_iz_uprave else "Nepoznata uprava"
    else:
        naziv_uprave = "Sve uprave"

    return render(request, 'prisustvo/mesecni_pregled.html', {
        'tabela': tabela,
        'godina': godina,
        'mesec': mesec,
        'forma': forma,
        'dani': dani,
        'statistike_po_zaposlenima': statistike_po_zaposlenima,
        'statistika_uprave': statistika_uprave,
        'naziv_uprave': naziv_uprave,
    })

@login_required
def godisnji_pregled_view(request):
    evidencija = PrisustvoMesec.objects.all()

    # Sortiranje zaposlenih po upravama
    uprava_map = {}
    uprava_map = SortiranjePoUpravama.superuser(request, uprava_map)
    uprava_map = SortiranjePoUpravama.user(request, uprava_map)

    # Kombinuj sve zaposlene iz mapa u jednu listu
    zaposlenici = [z for zaposleni_qs in uprava_map.values() for z in zaposleni_qs]

    tabela = {}

    for z in zaposlenici:
        statusi = evidencija.filter(zaposleni=z).values_list('status', flat=True)
        brojac = Counter(statusi)
        ukupno = sum(brojac.values())

        tabela[z] = {
            'statusi': brojac,
            'ukupno': ukupno
        }

    svi_statusi = [
        'Го', 'Д', 'Дс', 'Со', 'Бо', 'Сп', 'Лп',
        'Опп', 'Н', 'Сд', 'Дк', 'Оо', 'Но', 'Оп'
    ]

    return render(request, 'prisustvo/godisnji_pregled.html', {
        'tabela': tabela,
        'svi_statusi': svi_statusi,
    })
