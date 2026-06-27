# Comandos úteis

```bash
# Ativar venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

# Migrações
python manage.py makemigrations <app>
python manage.py migrate

# Importar dados históricos (banner.csv)
python manage.py import_banner

# Indexar documentos para RAG
python manage.py ingest_documents --dir data/

# Servidor de desenvolvimento
python manage.py runserver

# Celery (dev)
celery -A core worker -l info
celery -A core beat -l info

# Shell Django
python manage.py shell

# Criar superusuário
python manage.py createsuperuser

# Check do sistema
python manage.py check

# Verificar pipeline
python manage.py shell -c "from prescriptions.graph import build_graph; g = build_graph(); print('OK')"
```
