# SMPI — Documentação

Sistema de Manutenção Prescritiva Inteligente.

## Índice

| Documento | Descrição |
|---|---|
| [Visão geral](overview.md) | O que é o SMPI, objetivos e personas |
| [Configuração local](setup.md) | Como rodar o projeto em desenvolvimento |
| [Arquitetura](architecture.md) | Stack, apps planejados e modelo de dados |
| [Design System](design-system.md) | Tokens visuais, tipografia e componentes |
| [Variáveis de ambiente](environment.md) | Referência do `.env` |

## Estado atual do projeto

O projeto está no início do **Sprint 0**. A estrutura presente no repositório é:

```
smpi/
├── core/               # Projeto Django (settings, urls, wsgi, asgi)
├── design_system/      # Design system HTML de referência
├── manage.py
├── requirements.txt
├── .env                # Template (não versionar com valores reais)
└── PRD.md              # Product Requirements Document completo
```

> Para o plano completo de desenvolvimento, consulte o [PRD.md](../PRD.md).
