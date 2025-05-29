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


@login_required                     #login check
def jutarnji_unos_view(request):    #metod koji koristi request varijablu, obradjivace post zahtev
    today = timezone.now().date()   #dan
    prisustva_dict = {              #dict od p koji je usao u tabelu zaposlenih na osnovu ./models.py PrisustvoNaDan prvi red zaposleni koji je ForeignKey(Zaposleni, on_delete=models.CASCADE) pa je usao u tabelu Zaposleni i iz njega u vrednost iz kolone zaposleni_id
        p.zaposleni_id: p for p in PrisustvoNaDan.objects.filter(datum=today) #i sada ispisuje sve sto je u koloni prisustvo na dan vezano za taj zaposleni_id ali samo za danasnji dan
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
    if request.method == 'POST':        #ako trazi nesto od programa
        post_data = request.POST.copy() #daje mu se kopija
        for uprava_id, zaposleni_lista in uprava_map.items():   #iz dikta se prikazuju sve elementi
            formovi = []                                        #pravi se array form
            for zaposleni in zaposleni_lista:
                prefix = str(zaposleni.id)
                post_data[f"{prefix}-zaposleni"] = zaposleni.id
                form = PrisustvoZaZaposlenogForm(post_data, prefix=prefix)
                formovi.append((form, zaposleni))               #stavlja u array post data i prefix, zaposleni id
            formovi_po_upravama[uprava_id] = formovi        

        # Validacija svih formi
        if all(form.is_valid() for forms in formovi_po_upravama.values() for form, _ in forms):
            for forms in formovi_po_upravama.values():
                for form, zaposleni in forms:
                    status = form.cleaned_data['status']
                    PrisustvoNaDan.objects.update_or_create(        #popunjava 
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

@login_required                                     #dekorator, ugradjena funkcija djanga, proverava da li je korisnik ulogovan
def dnevni_pregled_view(request):                   #ime metode
    today = timezone.now().date()                   #varijabla za vreme
    tabela = {}                                     #dict koji ce cuvati podatke o zaposlenima
    statistike = {}                                 #dict koji ce cuvati podatke statistike statusa

    if request.user.is_superuser:                   #provera ko je logovan
        uprave = Zaposleni.objects.values_list('uprava', flat=True).distinct() #u petlju stavlja sve uprave iz ./models.py @ Zaposleni || flat = true pretvara touple u list || distinct samo unikate
        for uprava_id in uprave:                   #iterira kroz uprave
            zaposleni_uprave = Zaposleni.objects.filter(uprava_id=uprava_id) #petlja u petlji filtrira zaposlene u okviru jedne distinct uprave - dakle iterirace kroz sve zaposlene u jednoj upravi i pravi od njih kolonu
            prisustva = PrisustvoNaDan.objects.filter(                       #pravi petlju i filtrira za danasnji dan za zaposlene u distinct upravi u cijoj se petlji nalazis i pravi kolonu od njih 
                datum=today, zaposleni__in=zaposleni_uprave 
            ).select_related('zaposleni')       #opcia koja smanjuje broj SQL upita, optimizacija

            tabela[uprava_id] = prisustva       #pravi recnik sa upravom_id kao key, a prisustvo kao value

            # Statistika
            ukupno = zaposleni_uprave.count()           #broji zaposlene
            status_count = {}                           #broji statuse ranije unete u jutarnji_unos
            for p in prisustva:                          
                status_count[p.status] = status_count.get(p.status, 0) + 1

            procenti = {
                status: f"{(count / ukupno) * 100:.0f}%"
                for status, count in status_count.items()
            } if ukupno > 0 else {}

            statistike[uprava_id] = {
                'ukupno': ukupno,
                'brojevi': status_count,
                'procenti': procenti,
            }

    elif hasattr(request.user, 'zaposleni'):            #ako nije superuser, gleda kolonu zaposleni da li je nakacena na user
        uprava = request.user.zaposleni.uprava          #ako jeste gleda da li je zaposleni zakaceno na uprava
        zaposleni_uprave = Zaposleni.objects.filter(uprava=uprava)
        prisustva = PrisustvoNaDan.objects.filter(
            datum=today, zaposleni__in=zaposleni_uprave
        ).select_related('zaposleni')

        tabela[uprava.id] = prisustva

        # Statistika
        ukupno = zaposleni_uprave.count()
        status_count = {}
        for p in prisustva:
            status_count[p.status] = status_count.get(p.status, 0) + 1

        procenti = {
            status: f"{(count / ukupno) * 100:.0f}%"
            for status, count in status_count.items()
        } if ukupno > 0 else {}

        statistike[uprava.id] = {
            'ukupno': ukupno,
            'brojevi': status_count,
            'procenti': procenti,
        }

    return render(request, 'prisustvo/dnevni_pregled.html', {   #renderuje (prikazuje)
        'tabela': tabela,                                       #tabela tamo gde zove tabela {[uprava_id] = zaposleni}
        'statistike': statistike,                               #statistike tamo gde zove tabela {[uprava_id] = zaposleni}
        'danas': today                                          #today gde zove danas tamo gde zove tabela {[uprava_id] = zaposleni}
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
