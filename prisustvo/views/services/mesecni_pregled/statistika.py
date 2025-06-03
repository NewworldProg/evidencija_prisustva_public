# services/mesecni_pregled/statistika.py

from prisustvo.models import Zaposleni


def pripremi_mesecni_pregled(godina, mesec, uprava_id, evidencija):
    """
    Glavna funkcija za pripremu podataka za mesečni pregled.
    Vraća tabelu prisustva, dane, statistike i naziv uprave.
    """
    if uprava_id:
        zaposlenici = Zaposleni.objects.filter(uprava_id=uprava_id).order_by('ime_prezime')
    else:
        zaposlenici = Zaposleni.objects.all().order_by('ime_prezime')

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

    return {
        'tabela': tabela,
        'dani': dani,
        'statistike_po_zaposlenima': statistike_po_zaposlenima,
        'statistika_uprave': statistika_uprave,
        'naziv_uprave': naziv_uprave,
    }


def izracunaj_statistiku_po_zaposlenima(zaposleni_qs, evidencija):
    """
    Statistika po svakom zaposlenom ponaosob.
    """
    statistike = {}

    for z in zaposleni_qs:
        prisustva = evidencija.filter(zaposleni=z)

        brojevi = {}
        for e in prisustva:
            brojevi[e.status] = brojevi.get(e.status, 0) + 1

        ukupno = sum(brojevi.values())

        procenti = {}
        if ukupno > 0:
            for status, broj in brojevi.items():
                procenti[status] = f"{(broj / ukupno) * 100:.0f}%"

        statistike[z.id] = {
            'ukupno': ukupno,
            'brojevi': brojevi,
            'procenti': procenti
        }

    return statistike


def izracunaj_statistiku_za_upravu(zaposleni_qs, evidencija):
    """
    Agregirana statistika za celu upravu.
    """
    brojevi = {}

    for z in zaposleni_qs:
        prisustva = evidencija.filter(zaposleni=z)
        for e in prisustva:
            brojevi[e.status] = brojevi.get(e.status, 0) + 1

    ukupno = sum(brojevi.values())

    procenti = {}
    if ukupno > 0:
        for status, broj in brojevi.items():
            procenti[status] = f"{(broj / ukupno) * 100:.0f}%"

    return {
        'ukupno': ukupno,
        'brojevi': brojevi,
        'procenti': procenti
    }
