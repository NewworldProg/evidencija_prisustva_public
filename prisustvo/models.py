from django.db import models
from django.contrib.auth.models import User

class Uprava(models.Model):
    naziv = models.CharField(max_length=100)

    def __str__(self):
        return self.naziv

class Zaposleni(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    ime_prezime = models.CharField(max_length=100)
    cin = models.CharField(max_length=50)
    lokal = models.CharField(max_length=20)
    uprava = models.ForeignKey(Uprava, on_delete=models.CASCADE)

    def __str__(self):
        return self.ime_prezime

class PrisustvoNaDan(models.Model):
    STATUSI = [
        ('+', 'Prisutan'),
        ('Го', 'Godišnji odmor'),
        ('Д', 'Dežurstvo'),
        ('Б', 'Bolovanje'),
        ('С', 'Slobodan'),
        ('Н', 'Neopravdano'),
        ('Р', 'Rad od kuće'),
        ('О', 'Odsutan'),
    ]
    zaposleni = models.ForeignKey(Zaposleni, on_delete=models.CASCADE)
    datum = models.DateField()
    status = models.CharField(max_length=5, choices=STATUSI)

    class Meta:
        unique_together = ('zaposleni', 'datum')

    def __str__(self):
        return f"{self.zaposleni} - {self.datum} - {self.status}"

class PrisustvoMesec(models.Model):
    zaposleni = models.ForeignKey(Zaposleni, on_delete=models.CASCADE)
    godina = models.IntegerField()
    mesec = models.IntegerField()
    dan = models.IntegerField()
    status = models.CharField(max_length=5)

    class Meta:
        unique_together = ('zaposleni', 'godina', 'mesec', 'dan')

    def __str__(self):
        return f"{self.zaposleni} - {self.dan}.{self.mesec}.{self.godina} - {self.status}"
