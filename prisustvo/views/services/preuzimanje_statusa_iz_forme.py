class PreuzimanjeStatusaIzForme:

    @staticmethod
    def validiranje_forme(formovi_po_upravama):
        if all(form.is_valid() for forms in formovi_po_upravama.values() for form, _ in forms):
            sve_forme = []
            for forms in formovi_po_upravama.values():
                for form, zaposleni in forms:
                    sve_forme.append((form, zaposleni))
            return True, sve_forme
        return False, []

    @staticmethod
    def statusi(sve_forme):
        statusi_i_zaposleni = []
        for form, zaposleni in sve_forme:
            status = form.cleaned_data['status']
            statusi_i_zaposleni.append((zaposleni, status))
        return statusi_i_zaposleni
