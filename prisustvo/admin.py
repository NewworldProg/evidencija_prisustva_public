from django.contrib import admin
from .models import Uprava, Zaposleni, PrisustvoNaDan, PrisustvoMesec

@admin.register(Uprava)
class UpravaAdmin(admin.ModelAdmin):
    list_display = ('id', 'naziv')
    search_fields = ('naziv',)

@admin.register(Zaposleni)
class ZaposleniAdmin(admin.ModelAdmin):
    list_display = ('ime_prezime', 'cin', 'lokal', 'uprava')
    list_filter = ('uprava',)
    search_fields = ('ime_prezime', 'cin', 'lokal')

@admin.register(PrisustvoNaDan)
class PrisustvoNaDanAdmin(admin.ModelAdmin):
    list_display = ('zaposleni', 'datum', 'status')
    list_filter = ('datum', 'status')
    search_fields = ('zaposleni__ime_prezime',)

@admin.register(PrisustvoMesec)
class PrisustvoMesecAdmin(admin.ModelAdmin):
    list_display = ('zaposleni', 'godina', 'mesec', 'dan', 'status')
    list_filter = ('godina', 'mesec', 'status')
    search_fields = ('zaposleni__ime_prezime',)
