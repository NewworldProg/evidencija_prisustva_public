from prisustvo.models import Zaposleni

class SortiranjePoUpravama:
    @staticmethod
    def superuser(request, uprava_map: dict):
        if request.user.is_superuser:
            uprave = Zaposleni.objects.values_list('uprava', flat=True).distinct()
            for uprava_id in uprave:
                zaposleni = Zaposleni.objects.filter(uprava_id=uprava_id).order_by('ime_prezime')
                uprava_map[uprava_id] = zaposleni
        return uprava_map

    @staticmethod
    def user(request, uprava_map: dict):
        if hasattr(request.user, 'zaposleni'):
            uprava = request.user.zaposleni.uprava
            zaposleni = Zaposleni.objects.filter(uprava=uprava).order_by('ime_prezime')
            uprava_map[uprava.id] = zaposleni
        return uprava_map

    @staticmethod
    def zaposleni_iz_uprave(request, uprava_id):
        uprava_map = {}
        uprava_map = SortiranjePoUpravama.superuser(request, uprava_map)
        uprava_map = SortiranjePoUpravama.user(request, uprava_map)
        return uprava_map.get(int(uprava_id), [])