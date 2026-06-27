from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('knowledge', '0001_initial'),
    ]
    operations = [
        migrations.RunSQL(
            sql=(
                'CREATE INDEX IF NOT EXISTS knowledge_documentchunk_emb_ivfflat '
                'ON knowledge_documentchunk USING ivfflat (embedding vector_cosine_ops) '
                'WITH (lists = 10);'
            ),
            reverse_sql='DROP INDEX IF EXISTS knowledge_documentchunk_emb_ivfflat;',
        ),
    ]
