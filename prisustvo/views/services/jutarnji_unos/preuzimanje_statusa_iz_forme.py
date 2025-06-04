# services/jutarnji_unos/validacija.py

class PreuzimanjeStatusaIzForme:

    @staticmethod
    def validiranje_forme(formovi_po_upravama):     #forma je validna ako se na osnovu nje moze popuniti model cije kolone koristi
        sve_forme = []
        nevalidni_zaposleni = []

        for formovi in formovi_po_upravama.values():
            for form, zaposleni in formovi:
                sve_forme.append((form, zaposleni))
                if not form.is_valid():
                    nevalidni_zaposleni.append(zaposleni)

        validno = len(nevalidni_zaposleni) == 0
        return validno, sve_forme, nevalidni_zaposleni

    @staticmethod
    def statusi(sve_forme):
        statusi_i_zaposleni = []
        for form, zaposleni in sve_forme:
            status = form.cleaned_data['status']
            statusi_i_zaposleni.append((zaposleni, status))
        return statusi_i_zaposleni
