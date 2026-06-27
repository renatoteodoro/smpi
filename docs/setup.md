# Configuração local

## Pré-requisitos

- Python 3.13+
- Git

## Instalação

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd smpi

# 2. Criar e ativar o ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
# Copie o .env e preencha os valores (veja docs/environment.md)
cp .env .env.local   # opcional — o projeto lê .env por padrão

# 5. Aplicar migrações (banco SQLite por padrão em desenvolvimento)
python manage.py migrate

# 6. Rodar o servidor
python manage.py runserver
```

O servidor estará disponível em `http://127.0.0.1:8000`.

## Django Admin

```bash
python manage.py createsuperuser
```

Acesse em `http://127.0.0.1:8000/admin/`.

## Dependências atuais

| Pacote | Versão |
|---|---|
| Django | 6.0.6 |
| asgiref | 3.11.1 |
| sqlparse | 0.5.5 |
| tzdata | 2026.2 |

> O `requirements.txt` será expandido conforme os sprints avançam (PostgreSQL, pgvector, Celery, LangChain, etc.).

## Banco de dados em desenvolvimento

Por padrão, o `settings.py` usa **SQLite** (`db.sqlite3`). Para usar PostgreSQL (recomendado a partir do Sprint 3), defina `DATABASE_URL` no `.env` e ajuste o `settings.py` para lê-lo com `django-environ`.
