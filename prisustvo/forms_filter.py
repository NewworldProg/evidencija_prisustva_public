from django import forms
from .models import Uprava

class FilterForma(forms.Form):
    godina = forms.IntegerField(label="Godina", required=False)
    mesec = forms.IntegerField(label="Mesec", required=False)
    uprava = forms.ModelChoiceField(queryset=Uprava.objects.all(), required=False)
