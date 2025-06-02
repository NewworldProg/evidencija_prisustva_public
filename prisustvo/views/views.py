from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import date
from django.contrib import messages

from ..models import PrisustvoNaDan, PrisustvoMesec, Zaposleni, Uprava
from ..forms import FilterForma, PrisustvoZaZaposlenogForm
from .services.forme_za_izmenu_statusa import FormeZaIzmenuStatusa
from .services.preuzimanje_statusa_iz_forme import PreuzimanjeStatusaIzForme
from .services.sortiranje_po_upravama import SortiranjePoUpravama
from .services.prisustvo_service import dohvati_prisustva_po_upravama
from .services.statistika_service import izracunaj_statistiku_po_entitetima



def home_view(request):
    return render(request, 'prisustvo/home.html')


@login_required
def jutarnji_unos_view(request):
    today = timezone.now().date()

    prisustva_dict = {p.zaposleni_id: p for p in PrisustvoNaDan.objects.filter(datum=today)}

    uprava_map = {}
    uprava_map = SortiranjePoUpravama.superuser(request, uprava_map)
    uprava_map = SortiranjePoUpravama.user(request, uprava_map)

    if request.method == 'POST':
        formovi_po_upravama = FormeZaIzmenuStatusa.izmena(request, uprava_map)
        validno, sve_forme = PreuzimanjeStatusaIzForme.validiranje_forme(formovi_po_upravama)

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
        else:
            messages.error(request, "❌ Greška u formi.")
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

    tabela = dohvati_prisustva_po_upravama(uprava_map, today)

    statistike = {}
    for uprava_id, zaposleni_lista in uprava_map.items():
        prisustva = tabela.get(uprava_id, [])
        statistike_po_upravi = izracunaj_statistiku_po_entitetima([uprava_id], prisustva, entitet_polje='zaposleni')
        statistike[uprava_id] = statistike_po_upravi.get(uprava_id, {'ukupno': 0, 'brojevi': {}, 'procenti': {}})

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
    godina_str = request.GET.get('godina')
    mesec_str = request.GET.get('mesec')
    uprava_id = request.GET.get('uprava')
    zaposleni_id = request.GET.get('zaposleni')

    if not request.user.is_superuser and hasattr(request.user, 'zaposleni'):
        uprava_id = request.user.zaposleni.uprava.id

    godina = int(godina_str) if godina_str else danas.year
    mesec = int(mesec_str) if mesec_str else danas.month

    forma = FilterForma(request.GET or None)

    zaposlenici = Zaposleni.objects.all().select_related('uprava')
    if uprava_id:
        zaposlenici = zaposlenici.filter(uprava__id=uprava_id)
    if zaposleni_id:
        zaposlenici = zaposlenici.filter(id=zaposleni_id)

    evidencija = PrisustvoMesec.objects.filter(godina=godina, mesec=mesec)

    tabela = {}
    for z in zaposlenici:
        tabela[z] = {}
        for dan in range(1, 32):
            zapis = evidencija.filter(zaposleni=z, dan=dan).first()
            tabela[z][dan] = zapis.status if zapis else ''

    dani = list(range(1, 32))

    statistike_po_zaposlenima = izracunaj_statistiku_po_entitetima(zaposlenici, evidencija, entitet_polje='zaposleni')

    statistika_uprave = izracunaj_statistiku_po_entitetima(zaposlenici, evidencija, entitet_polje='zaposleni')

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
    zaposlenici = Zaposleni.objects.all()
    evidencija = PrisustvoMesec.objects.all()

    agregat = {}
    for z in zaposlenici:
        agregat[z] = {}
        for e in evidencija.filter(zaposleni=z):
            kljuc = f"{e.godina}-{e.mesec:02d}-{e.dan:02d}"
            agregat[z][kljuc] = e.status

    return render(request, 'prisustvo/godisnji_pregled.html', {
        'agregat': agregat
    })
