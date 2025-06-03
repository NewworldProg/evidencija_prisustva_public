from django import template
from prisustvo.models import Uprava

register = template.Library()

@register.simple_tag
def naziv_uprave_po_id(uprava_id):
    try:
        return Uprava.objects.get(id=uprava_id).naziv
    except Uprava.DoesNotExist:
        return f"Uprava {uprava_id}"
