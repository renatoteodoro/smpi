# API REST

O SMPI expõe uma API REST completa via Django REST Framework com documentação OpenAPI automática.

## Acesso

- **Swagger UI:** `/api/docs/`
- **ReDoc:** `/api/redoc/`
- **Schema OpenAPI (JSON):** `/api/schema/`

## Autenticação

Use o header `X-API-Key` com uma chave gerada no Django Admin (`/admin/api/apikey/`):

```http
GET /api/v1/equipment/ HTTP/1.1
X-Api-Key: sua-chave-aqui
```

## Endpoints principais

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/v1/equipment/` | Lista equipamentos |
| GET | `/api/v1/faults/` | Lista defeitos |
| GET | `/api/v1/readings/` | Lista leituras |
| POST | `/api/v1/readings/` | Cria leitura (dispara análise) |
| GET | `/api/v1/prescriptions/` | Lista prescrições |
| GET | `/api/v1/knowledge/` | Lista documentos |

## Criando uma leitura via API

```bash
curl -X POST /api/v1/readings/ \
  -H "X-Api-Key: sua-chave" \
  -H "Content-Type: application/json" \
  -d '{
    "measurement_point": 1,
    "metrics": {
      "rpm": 1780,
      "x_rms": 2.3,
      "temperature_c": 42.1
    }
  }'
```

A análise é disparada automaticamente em background via Celery.
