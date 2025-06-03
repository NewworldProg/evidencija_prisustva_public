# services/dnevni_pregled/statistika.py

from ..prisustvo_service import dohvati_prisustva_po_upravama

def pripremi_statistiku_po_upravama(uprava_map, datum):
    tabela = dohvati_prisustva_po_upravama(uprava_map, datum)

    statistike = {}

    for uprava_id, zaposleni_lista in uprava_map.items():
        prisustva = tabela.get(uprava_id, [])
        
        # Inicijalizuj brojanje po statusima
        brojevi = {}
        for zapis in prisustva:
            status = zapis.status
            brojevi[status] = brojevi.get(status, 0) + 1

        ukupno = len(prisustva)
        procenti = {}
        if ukupno > 0:
            for status, broj in brojevi.items():
                procenti[status] = f"{(broj / ukupno) * 100:.0f}%"

        statistike[uprava_id] = {
            'ukupno': ukupno,
            'brojevi': brojevi,
            'procenti': procenti
        }

    return tabela, statistike
