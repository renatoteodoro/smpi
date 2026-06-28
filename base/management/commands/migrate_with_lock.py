import time

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Run migrate with PostgreSQL advisory lock — safe for multiple replicas.'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('SELECT pg_try_advisory_lock(20260101)')
            acquired = cursor.fetchone()[0]

        if acquired:
            self.stdout.write('[migrate_with_lock] Lock acquired — running migrations...')
            try:
                call_command('migrate', '--noinput', verbosity=1)
            finally:
                with connection.cursor() as cursor:
                    cursor.execute('SELECT pg_advisory_unlock(20260101)')
            self.stdout.write(self.style.SUCCESS('[migrate_with_lock] Done, lock released.'))
        else:
            self.stdout.write('[migrate_with_lock] Another replica is migrating — waiting 15s...')
            time.sleep(15)
            self.stdout.write('[migrate_with_lock] Assuming migrations complete.')
