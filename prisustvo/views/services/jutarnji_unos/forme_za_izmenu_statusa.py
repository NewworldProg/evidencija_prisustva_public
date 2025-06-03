# services/jutarnji_unos/forme.py

from ....forms import PrisustvoZaZaposlenogForm

class FormeZaIzmenuStatusa:
    @staticmethod
    def izmena(request, uprava_map: dict) -> dict:
        formovi_po_upravama = {}
        post_data = request.POST.copy()

        for uprava_id, zaposleni_lista in uprava_map.items():
            formovi = []
            for zaposleni in zaposleni_lista:
                prefix = str(zaposleni.id)
                post_data[f"{prefix}-zaposleni"] = zaposleni.id
                form = PrisustvoZaZaposlenogForm(post_data, prefix=prefix)
                formovi.append((form, zaposleni))
            formovi_po_upravama[uprava_id] = formovi

        return formovi_po_upravama

    @staticmethod
    def initial_forme(uprava_map: dict, prisustva_dict: dict) -> dict:
        formovi_po_upravama = {}

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

        return formovi_po_upravama
