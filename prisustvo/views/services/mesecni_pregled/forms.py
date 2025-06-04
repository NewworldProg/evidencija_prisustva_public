from django import forms
from prisustvo.models import PrisustvoMesec


class MesecGodinaFilterForma(forms.Form):
    godina = forms.IntegerField(required=False)
    mesec = forms.IntegerField(required=False)

    def filtriraj(self, godina, mesec):
        return PrisustvoMesec.objects.filter(godina=godina, mesec=mesec)
