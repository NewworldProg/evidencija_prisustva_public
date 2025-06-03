from django.core.management.base import BaseCommand
from prisustvo.models import PrisustvoNaDan, Zaposleni
from django.db import connection

class Command(BaseCommand):
    help = 'Briše zapise sa sve NULL i zaposlene sa id=NULL'

    def handle(self, *args, **kwargs):
        # 1. Obriši zaposlene koji imaju NULL kao ID (nevalidno, ali SQL dopušta)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM prisustvo_zaposleni WHERE id IS NULL")
            deleted_null_id_count = cursor.rowcount
        self.stdout.write(self.style.WARNING(f"🧹 Obrisano {deleted_null_id_count} zaposlenih sa id=NULL"))

        # 2. Obriši zapise iz PrisustvoNaDan gde su sve kolone NULL (status, datum, zaposleni)
        null_rows_count, _ = PrisustvoNaDan.objects.filter(
            datum__isnull=True,
            status__isnull=True,
            zaposleni__isnull=True
        ).delete()
        self.stdout.write(self.style.SUCCESS(f"🧼 Obrisano {null_rows_count} zapisa iz PrisustvoNaDan gde su sve vrednosti NULL"))
