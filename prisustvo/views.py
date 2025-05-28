from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import date
from django.contrib import messages

from .models import PrisustvoNaDan, PrisustvoMesec, Zaposleni
from .forms import PrisustvoFormset, FilterForma, PrisustvoZaZaposlenogForm


def home_view(request):
    return render(request, 'prisustvo/home.html')


@login_required
def jutarnji_unos_view(request):
    today = timezone.now().date()

    if request.user.is_superuser:
        uprava_id = request.GET.get("uprava")
        svi_zaposleni = Zaposleni.objects.all().order_by('ime_prezime')
        if uprava_id:
            svi_zaposleni = svi_zaposleni.filter(uprava__id=uprava_id)
    else:
        if hasattr(request.user, 'zaposleni'):
            svi_zaposleni = Zaposleni.objects.filter(
                uprava=request.user.zaposleni.uprava
            ).order_by('ime_prezime')
        else:
            svi_zaposleni = Zaposleni.objects.none()

    prisustva_dict = {
        p.zaposleni_id: p for p in PrisustvoNaDan.objects.filter(datum=today)
    }

    formovi = []

    if request.method == 'POST':
        post_data = request.POST.copy()
        for zaposleni in svi_zaposleni:
            prefix = str(zaposleni.id)
            post_data[f"{prefix}-zaposleni"] = zaposleni.id
            form = PrisustvoZaZaposlenogForm(post_data, prefix=prefix)
            formovi.append((form, zaposleni))

        if all(form.is_valid() for form, _ in formovi):
            for form, zaposleni in formovi:
                status = form.cleaned_data['status']
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
            for form, z in formovi:
                if not form.is_valid():
                    print(f"❌ Greška za {z}: {form.errors}")

    else:
        for zaposleni in svi_zaposleni:
            prisustvo = prisustva_dict.get(zaposleni.id)
            initial = {
                'zaposleni': zaposleni,
                'status': prisustvo.status if prisustvo else ''
            }
            form = PrisustvoZaZaposlenogForm(initial=initial, prefix=str(zaposleni.id))
            formovi.append((form, zaposleni))

    return render(request, 'prisustvo/jutarnji_unos.html', {
        'formovi': formovi,
        'danas': today
    })


@login_required
def dnevni_pregled_view(request):
    today = timezone.now().date()
    prisustva = PrisustvoNaDan.objects.filter(
        datum=today
    ).select_related('zaposleni').order_by('zaposleni__ime_prezime')

    return render(request, 'prisustvo/dnevni_pregled.html', {
        'prisustva': prisustva,
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

    godina = int(godina_str) if godina_str else danas.year
    mesec = int(mesec_str) if mesec_str else danas.month

    uprava_id = request.GET.get('uprava')
    forma = FilterForma(request.GET or None)

    zaposlenici = Zaposleni.objects.all().select_related('uprava')
    if uprava_id:
        zaposlenici = zaposlenici.filter(uprava__id=uprava_id)

    evidencija = PrisustvoMesec.objects.filter(godina=godina, mesec=mesec)

    tabela = {}
    for z in zaposlenici:
        tabela[z] = {}
        for dan in range(1, 32):
            zapis = evidencija.filter(zaposleni=z, dan=dan).first()
            tabela[z][dan] = zapis.status if zapis else ''

    dani = list(range(1, 32))

    return render(request, 'prisustvo/mesecni_pregled.html', {
        'tabela': tabela,
        'godina': godina,
        'mesec': mesec,
        'forma': forma,
        'dani': dani
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
