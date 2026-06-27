from django.db import migrations


class Migration(migrations.Migration):
    """Enable the pgvector extension in PostgreSQL.

    Must run before any migration that uses VectorField.
    """

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql='CREATE EXTENSION IF NOT EXISTS vector;',
            reverse_sql='DROP EXTENSION IF EXISTS vector;',
        ),
    ]
