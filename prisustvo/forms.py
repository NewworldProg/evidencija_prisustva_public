from django import forms
from django.forms import modelformset_factory
from .models import PrisustvoNaDan, Zaposleni, Uprava

class PrisustvoZaZaposlenogForm(forms.ModelForm):
    class Meta:
        model = PrisustvoNaDan
        fields = ['zaposleni', 'status']
        widgets = {'zaposleni': forms.HiddenInput()}

PrisustvoFormset = modelformset_factory(
    PrisustvoNaDan,
    form=PrisustvoZaZaposlenogForm,
    extra=0
)
#ne koristi se za sada, moze da bude korisno
#==================================================================================================
class PrisustvoNaDanForm(forms.ModelForm):
    class Meta:
        model = PrisustvoNaDan
        fields = ['zaposleni', 'status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and not user.is_superuser and hasattr(user, 'zaposleni'):
            uprava_korisnika = user.zaposleni.uprava
            self.fields['zaposleni'].queryset = Zaposleni.objects.filter(uprava=uprava_korisnika)
        else:
            self.fields['zaposleni'].queryset = Zaposleni.objects.all()

        self.fields['zaposleni'].label = "Zaposleni"
        self.fields['status'].label = "Status za danas"
#==================================================================================================

class FilterForma(forms.Form):
    godina = forms.IntegerField(label='Godina', required=False)
    MESECI = [
    (1, 'Januar'), (2, 'Februar'), (3, 'Mart'), (4, 'April'),
    (5, 'Maj'), (6, 'Jun'), (7, 'Jul'), (8, 'Avgust'),
    (9, 'Septembar'), (10, 'Oktobar'), (11, 'Novembar'), (12, 'Decembar'),
]
    mesec = forms.ChoiceField(
        label='Mesec',
        choices=MESECI,
        required=False
    )
    uprava = forms.ModelChoiceField(queryset=Uprava.objects.all(), required=False)
    zaposleni = forms.ModelChoiceField(queryset=Zaposleni.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and not user.is_superuser and hasattr(user, 'zaposleni'):
            uprava_korisnika = user.zaposleni.uprava
            self.fields['uprava'].queryset = Uprava.objects.filter(id=uprava_korisnika.id)
            self.fields['zaposleni'].queryset = Zaposleni.objects.filter(uprava=uprava_korisnika)
        else:
            self.fields['uprava'].queryset = Uprava.objects.all()
            self.fields['zaposleni'].queryset = Zaposleni.objects.all()

