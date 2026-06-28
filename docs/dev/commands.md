# Comandos úteis

## Docker (desenvolvimento)

```bash
# Subir toda a stack
docker compose up -d

# Ver status dos containers
docker compose ps

# Logs em tempo real
docker logs smpi-app-1 -f
docker logs smpi-celery_worker-1 -f

# Reiniciar serviço específico
docker compose restart app
docker compose restart celery_worker

# Parar tudo
docker compose down
```

## Django Management

```bash
# Migrações
docker exec smpi-app-1 python manage.py migrate_with_lock
docker exec smpi-app-1 python manage.py makemigrations <app>

# Superusuário
docker exec smpi-app-1 python manage.py createsuperuser

# Importar dados históricos (banner.csv → 166k leituras)
docker exec smpi-app-1 python manage.py import_banner

# Indexar documentos para RAG
docker exec smpi-app-1 python manage.py ingest_documents --dir data/

# Shell Django
docker exec -it smpi-app-1 python manage.py shell

# Check do sistema
docker exec smpi-app-1 python manage.py check
docker exec smpi-app-1 python manage.py check --deploy  # validações de produção

# Static files
docker exec smpi-app-1 python manage.py collectstatic --noinput --clear
```

## Celery (desenvolvimento local sem Docker)

```bash
# Ativar venv primeiro
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

# Worker
celery -A core worker -l info

# Beat (agendador de tarefas periódicas)
celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Purgar fila (apagar tasks pendentes)
celery -A core purge -f
```

## Evolution API (WhatsApp)

```bash
# Estado da conexão
curl http://localhost:8080/instance/connectionState/smpi \
  -H "apikey: $(grep EVOLUTION_API_KEY .env | cut -d= -f2)"

# Verificar webhook configurado
curl http://localhost:8080/webhook/find/smpi \
  -H "apikey: $(grep EVOLUTION_API_KEY .env | cut -d= -f2)"

# Enviar mensagem de teste
curl -X POST http://localhost:8080/message/sendText/smpi \
  -H "apikey: $(grep EVOLUTION_API_KEY .env | cut -d= -f2)" \
  -H "Content-Type: application/json" \
  -d '{"number":"5548999999999","text":"Teste SMPI"}'
```

## Deploy (produção)

```bash
# Deploy completo (build + push + rollout)
DOMAIN=www.techteo.com.br ./scripts/deploy.sh

# Deploy sem rebuild (usa imagem existente)
./scripts/deploy.sh --skip-build

# Status dos serviços Swarm
docker service ls | grep smpi_v1
docker service ps smpi_v1_app

# Logs em produção
docker service logs smpi_v1_app --follow
docker service logs smpi_v1_celery_worker --follow

# Backup do banco
./scripts/backup.sh
```

## Pipeline IA (verificação)

```bash
# Verificar grafo LangGraph
docker exec smpi-app-1 python manage.py shell -c "
from ai.agent import _get_agent
agent = _get_agent()
print('Agente OK:', type(agent).__name__)
"

# Testar prescrição manualmente
docker exec -it smpi-app-1 python manage.py shell -c "
from prescriptions.tasks import analyse_reading
from monitoring.models import SensorReading
reading = SensorReading.objects.filter(status_class='problem').first()
if reading:
    analyse_reading.delay(reading.pk)
    print(f'Task disparada para leitura #{reading.pk}')
"
```
