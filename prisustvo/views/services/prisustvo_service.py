from ...models import PrisustvoNaDan

def dohvati_prisustva_po_upravama(uprava_map: dict, datum):
    tabela = {}
    for uprava_id, zaposleni_lista in uprava_map.items():
        prisustva = PrisustvoNaDan.objects.filter(
            datum=datum,
            zaposleni__in=zaposleni_lista
        ).select_related('zaposleni')
        tabela[uprava_id] = prisustva
    return tabela
