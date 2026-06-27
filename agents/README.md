# Agentes de IA — SMPI

Cada arquivo define o papel, responsabilidades, ferramentas e regras de um agente de IA especialista em uma camada do projeto. Use o agente correto para cada tarefa para obter código preciso, atualizado e alinhado aos padrões do projeto.

## Índice

| Agente | Arquivo | Quando usar |
|---|---|---|
| [Backend Django](#backend-django) | [backend.md](backend.md) | Models, views, DRF, Celery, management commands, pgvector |
| [Frontend Django](#frontend-django) | [frontend.md](frontend.md) | Templates DTL, TailwindCSS, design system, acessibilidade |
| [Pipeline de IA](#pipeline-de-ia) | [ai-pipeline.md](ai-pipeline.md) | LangGraph, RAG, embeddings, integração LLM, similaridade vetorial |
| [QA / Tester](#qa--tester) | [qa.md](qa.md) | Testes E2E com Playwright, verificação de UI/UX e acessibilidade |

---

## Backend Django

**Arquivo:** `backend.md`

Especialista em toda a camada de servidor: modelos Django, APIs REST com DRF, tarefas Celery, management commands (`import_banner`, `ingest_documents`), autenticação por email, middleware de proteção de media, integração pgvector e Evolution API.

**Use quando precisar de:**
- Criar ou alterar models, migrations, serializers, viewsets
- Implementar tarefas Celery (análise de evento, RAG, notificações)
- Escrever management commands de ingestão de dados
- Configurar autenticação por API key do sistema
- Integrar pgvector (feature_vector, busca ANN)
- Implementar webhook da Evolution API

---

## Frontend Django

**Arquivo:** `frontend.md`

Especialista em interfaces com Django Template Language (DTL) e TailwindCSS, seguindo o design system FIESC (`design_system/design-system.html`). Garante HTML semântico, acessibilidade (VLibras, ARIA, WCAG) e renderização de markdown via SSE stream.

**Use quando precisar de:**
- Criar ou alterar templates HTML com DTL e TailwindCSS
- Implementar componentes do design system (tokens `--fsi-clr-*`, MuseoSans)
- Construir dashboards, formulários, listagens e telas de detalhe
- Implementar o chat SSE (stream de tokens) e o chatbot flutuante
- Garantir responsividade, contraste e navegação por teclado

---

## Pipeline de IA

**Arquivo:** `ai-pipeline.md`

Especialista em LangGraph, LangChain, RAG, embeddings locais (sentence-transformers) e integração com LLMs (OpenAI / local via Ollama). Implementa o grafo prescritivo, as tools de acesso ao banco e à base documental, e garante a regra de guarda anti-alucinação.

**Use quando precisar de:**
- Construir ou alterar o grafo LangGraph (nós, edges, estado)
- Implementar tools de acesso a dados e RAG
- Configurar embeddings locais e busca vetorial por defeito
- Integrar o LLM (provider configurável `openai` | `local`)
- Garantir que toda resposta seja grounded e cite fontes

---

## QA / Tester

**Arquivo:** `qa.md`

Especialista em testes E2E usando o **MCP Playwright**. Acessa o sistema pelo navegador, verifica fluxos funcionais, conformidade com o design system e acessibilidade. Gera relatórios de bugs e melhorias acionáveis.

**Use quando precisar de:**
- Verificar se um fluxo implementado funciona de ponta a ponta
- Confirmar que o design system está sendo aplicado corretamente
- Auditar acessibilidade (VLibras, contraste, teclado, ARIA)
- Testar o chat SSE (stream), o chatbot flutuante e notificações
- Validar a ingestão de eventos e geração de prescrições
