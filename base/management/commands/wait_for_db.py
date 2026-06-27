import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Management command that polls the database until it becomes available.

    Used in Docker entrypoint scripts to block startup until PostgreSQL
    accepts connections. Retries up to 30 times with a 1-second delay.
    """

    help = 'Wait for the database to become available.'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        retries = 0
        while not db_conn:
            try:
                db_conn = connections['default']
                db_conn.ensure_connection()
            except OperationalError:
                retries += 1
                if retries > 30:
                    raise
                self.stdout.write(f'Database unavailable, retry {retries}/30...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
