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
    prisustva_dict = {
        p.zaposleni_id: p for p in PrisustvoNaDan.objects.filter(datum=today)
    }

    uprava_map = {}

    # Grupisanje po upravama
    if request.user.is_superuser:
        uprave = Zaposleni.objects.values_list('uprava', flat=True).distinct()
        for uprava_id in uprave:
            zaposleni = Zaposleni.objects.filter(uprava_id=uprava_id).order_by('ime_prezime')
            uprava_map[uprava_id] = zaposleni
    elif hasattr(request.user, 'zaposleni'):
        uprava = request.user.zaposleni.uprava
        zaposleni = Zaposleni.objects.filter(uprava=uprava).order_by('ime_prezime')
        uprava_map[uprava.id] = zaposleni

    # Forme po zaposlenima
    formovi_po_upravama = {}
    if request.method == 'POST':
        post_data = request.POST.copy()
        for uprava_id, zaposleni_lista in uprava_map.items():
            formovi = []
            for zaposleni in zaposleni_lista:
                prefix = str(zaposleni.id)
                post_data[f"{prefix}-zaposleni"] = zaposleni.id
                form = PrisustvoZaZaposlenogForm(post_data, prefix=prefix)
                formovi.append((form, zaposleni))
            formovi_po_upravama[uprava_id] = formovi

        # Validacija svih formi
        if all(form.is_valid() for forms in formovi_po_upravama.values() for form, _ in forms):
            for forms in formovi_po_upravama.values():
                for form, zaposleni in forms:
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
    else:
        for uprava_id, zaposleni_lista in uprava_map.items():
            formovi = []
            for zaposleni in zaposleni_lista:
                prisustvo = prisustva_dict.get(zaposleni.id)
                initial = {
                    'zaposleni': zaposleni,
                    'status': prisustvo.status if prisustvo else ''
                }
                form = PrisustvoZaZaposlenogForm(initial=initial, prefix=str(zaposleni.id))
                formovi.append((form, zaposleni))
            formovi_po_upravama[uprava_id] = formovi

    return render(request, 'prisustvo/jutarnji_unos.html', {
        'formovi_po_upravama': formovi_po_upravama,
        'danas': today
    })

@login_required
def dnevni_pregled_view(request):
    today = timezone.now().date()
    tabela = {}

    if request.user.is_superuser:
        uprave = Zaposleni.objects.values_list('uprava', flat=True).distinct()
        for uprava_id in uprave:
            zaposleni_uprave = Zaposleni.objects.filter(uprava_id=uprava_id)
            prisustva = PrisustvoNaDan.objects.filter(
                datum=today, zaposleni__in=zaposleni_uprave
            ).select_related('zaposleni')
            tabela[uprava_id] = prisustva
    elif hasattr(request.user, 'zaposleni'):
        uprava = request.user.zaposleni.uprava
        zaposleni_uprave = Zaposleni.objects.filter(uprava=uprava)
        prisustva = PrisustvoNaDan.objects.filter(
            datum=today, zaposleni__in=zaposleni_uprave
        ).select_related('zaposleni')
        tabela[uprava.id] = prisustva

    return render(request, 'prisustvo/dnevni_pregled.html', {
        'tabela': tabela,
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
