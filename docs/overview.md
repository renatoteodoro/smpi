# Visão geral

## O que é

O **SMPI** é um sistema **single-tenant** de manutenção prescritiva para equipamentos rotativos industriais instrumentados com sensores de vibração.

Ele vai além da manutenção preditiva (prever *quando* falha) para a manutenção prescritiva (indicar *o que fazer*), combinando:

1. **Análise de dados** dos sensores de vibração.
2. **Busca por similaridade vetorial** sobre o histórico operacional.
3. **RAG** sobre a base documental da empresa para gerar recomendações fundamentadas.

## Objetivos

- Detectar e contextualizar anomalias a partir de dados de sensores, **sem classificação prévia de falhas conhecidas** (abordagem por similaridade).
- Entregar para cada evento: **tipo de defeito**, **quantidade de ocorrências**, **frequência** e **instruções de solução**.
- Garantir que toda recomendação seja **grounded** em documentos — na ausência de documentação, reportar e solicitar registro, nunca inventar.
- Operar em estação de trabalho comercial (≤ 32 GB RAM / 16 GB GPU).

## Personas

| Persona | Responsabilidades |
|---|---|
| **Administrador da planta** | Gerencia usuários, equipamentos e a base documental. |
| **Técnico de manutenção** | Analisa eventos, recebe recomendações e executa ações. |
| **Técnico de campo (WhatsApp)** | Consulta e registra eventos pelo WhatsApp sem acesso ao desktop. |
| **Sistema industrial / Gateway** | Envia eventos automaticamente via API REST com API key. |
| **Engenheiro de confiabilidade** | Acompanha dashboards, tendências e frequência de defeitos. |

## KPIs

| KPI | Meta |
|---|---|
| Recomendações grounded (sem alucinação) | 100% com fonte documental |
| Tempo de análise de um evento | ≤ 30 s (assíncrono) |
| Latência do chat (primeiro token) | ≤ 3 s (stream) |
| Operação dentro do limite de hardware | 100% |
