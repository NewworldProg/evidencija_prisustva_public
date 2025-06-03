def izracunaj_statistiku_po_entitetima(entiteti, evidencija, entitet_polje='zaposleni'):
    """
    Izračunava statistiku prisustva po entitetima (zaposleni, uprava ili slično).

    :param entiteti: lista entiteta (model instanci) za koje želimo statistiku
    :param evidencija: queryset prisustva (dnevno ili mesečno)
    :param entitet_polje: naziv polja u evidenciji koje referencira entitet (npr. 'zaposleni', 'uprava')
    :return: dict entitet -> {'ukupno': int, 'brojevi': dict status->broj, 'procenti': dict status->%' }
    """

    statistike = {}

    for entitet in entiteti:
        # filtriramo evidenciju za taj entitet
        filter_kwargs = {entitet_polje: entitet}
        evidencije_entiteta = evidencija.filter(**filter_kwargs)

        brojevi = {}
        for e in evidencije_entiteta:
            brojevi[e.status] = brojevi.get(e.status, 0) + 1

        ukupno = sum(brojevi.values())

        procenti = {
            status: f"{(count / ukupno) * 100:.0f}%" for status, count in brojevi.items()
        } if ukupno > 0 else {}

        statistike[entitet] = {
            'ukupno': ukupno,
            'brojevi': brojevi,
            'procenti': procenti,
        }

    return statistike
