"""
Import historical sensor readings from banner.csv into the database.

Usage:
    python manage.py import_banner
    python manage.py import_banner --file path/to/banner.csv
    python manage.py import_banner --skip-scaler

Idempotent by external_id (uses update_or_create). Running twice does not
duplicate records — existing rows are updated in-place.

After import, fits and saves a StandardScaler on all problem readings to
ml_artifacts/scaler.pkl, then re-normalises every problem reading's
feature_vector in batches of 500.
"""

import csv
from pathlib import Path

import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from monitoring.models import FEATURE_COLUMNS
from faults.models import STATE_CODES

BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Import banner.csv historical sensor readings (idempotent).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=str(Path(settings.BASE_DIR) / 'data' / 'banner.csv'),
            help='Path to banner.csv (default: data/banner.csv)',
        )
        parser.add_argument(
            '--skip-scaler',
            action='store_true',
            help='Skip fitting/saving the StandardScaler after import.',
        )

    def handle(self, *args, **options):
        from assets.models import Equipment, MeasurementPoint
        from faults.models import Fault
        from monitoring.models import SensorReading
        from monitoring.preprocessing import extract_features, fit_and_save_scaler

        csv_path = Path(options['file'])
        if not csv_path.exists():
            raise CommandError(f'File not found: {csv_path}')

        self.stdout.write(f'Importing from {csv_path}...')

        # Ensure a default equipment + measurement point exist
        equipment, eq_created = Equipment.objects.get_or_create(
            name='Equipamento Banner',
            defaults={
                'equipment_type': 'motor',
                'sector': 'Chão de fábrica',
                'status': 'active',
            },
        )
        if eq_created:
            self.stdout.write(f'  Created equipment: {equipment}')

        measurement_point, mp_created = MeasurementPoint.objects.get_or_create(
            equipment=equipment,
            name='Sensor Principal',
            defaults={'axis': 'XZ', 'sensor_type': 'vibração'},
        )
        if mp_created:
            self.stdout.write(f'  Created measurement point: {measurement_point}')

        created = 0
        updated = 0
        skipped = 0
        all_problem_features: list[list[float]] = []

        with open(csv_path, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)

        total = len(rows)
        self.stdout.write(f'Total rows in CSV: {total}')

        for i, row in enumerate(rows, 1):
            if i % 1000 == 0:
                self.stdout.write(f'  Processed {i}/{total}...')

            # Parse external_id
            try:
                ext_id = int(row['id'])
            except (KeyError, ValueError):
                skipped += 1
                continue

            # Resolve fault
            fault_code = (row.get('fault') or '').strip()
            if not fault_code:
                skipped += 1
                continue

            is_problem = fault_code.lower() not in STATE_CODES
            fault, _ = Fault.objects.get_or_create(
                code=fault_code,
                defaults={
                    'name': fault_code.replace('_', ' ').title(),
                    'is_problem': is_problem,
                },
            )

            # Build raw metrics dict (exclude id/created_at/fault)
            metrics: dict = {}
            for k, v in row.items():
                if k in ('id', 'created_at', 'fault'):
                    continue
                try:
                    metrics[k] = float(v) if v not in ('', None) else None
                except ValueError:
                    metrics[k] = v

            raw_features = extract_features(metrics)

            # Parse event timestamp
            event_ts = None
            raw_ts = row.get('created_at', '')
            if raw_ts:
                try:
                    event_ts = parse_datetime(raw_ts.strip())
                except Exception:
                    pass

            # Parse RPM
            rpm_val = None
            try:
                rpm_raw = float(row.get('rpm') or 0)
                rpm_val = rpm_raw if rpm_raw else None
            except ValueError:
                pass

            status = 'problem' if is_problem else 'state'

            obj, was_created = SensorReading.objects.update_or_create(
                external_id=ext_id,
                defaults={
                    'measurement_point': measurement_point,
                    'metrics': metrics,
                    'feature_vector': raw_features,
                    'fault': fault,
                    'status_class': status,
                    'rpm': rpm_val,
                    'event_created_at': event_ts,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

            if is_problem:
                all_problem_features.append(raw_features)

        self.stdout.write(
            self.style.SUCCESS(
                f'Import done: {created} created, {updated} updated, {skipped} skipped.'
            )
        )

        if options['skip_scaler']:
            self.stdout.write('Scaler fitting skipped (--skip-scaler).')
            return

        if not all_problem_features:
            self.stdout.write(self.style.WARNING('No problem readings found — scaler not fitted.'))
            return

        # Fit and save the scaler
        self.stdout.write(
            f'Fitting StandardScaler on {len(all_problem_features)} problem readings...'
        )
        matrix = np.array(all_problem_features)
        fit_and_save_scaler(matrix)

        # Re-normalise all problem readings in the DB with the fitted scaler
        self.stdout.write('Applying scaler to all stored problem readings...')
        import joblib
        from sklearn.preprocessing import StandardScaler  # noqa: F401 — already imported by fit_and_save_scaler

        scaler = joblib.load(Path(settings.SCALER_PATH))

        batch: list = []
        count = 0
        for reading in SensorReading.objects.filter(
            status_class='problem', feature_vector__isnull=False
        ).only('id', 'feature_vector'):
            raw = reading.feature_vector
            if hasattr(raw, 'tolist'):
                raw = raw.tolist()
            normalized = scaler.transform(np.array(raw, dtype=float).reshape(1, -1))[0].tolist()
            reading.feature_vector = normalized
            batch.append(reading)
            if len(batch) >= BATCH_SIZE:
                SensorReading.objects.bulk_update(batch, ['feature_vector'])
                count += len(batch)
                batch = []

        if batch:
            SensorReading.objects.bulk_update(batch, ['feature_vector'])
            count += len(batch)

        self.stdout.write(
            self.style.SUCCESS(
                f'Scaler fitted and saved to {settings.SCALER_PATH}. '
                f'{count} problem readings normalised.'
            )
        )
