from django.db import migrations


class Migration(migrations.Migration):
    """Add IVFFlat ANN index on SensorReading.feature_vector for fast L2 similarity search."""

    dependencies = [
        ('monitoring', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS monitoring_sensorreading_fv_ivfflat "
                "ON monitoring_sensorreading USING ivfflat (feature_vector vector_l2_ops) "
                "WITH (lists = 100);"
            ),
            reverse_sql="DROP INDEX IF EXISTS monitoring_sensorreading_fv_ivfflat;",
        ),
    ]
