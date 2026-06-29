# Manual do Usuário — SMPI
## Sistema de Manutenção Prescritiva Inteligente

- **Acesso ao site em produção:** https://www.techteo.com.br
- **Acesso ao GitHub:** https://github.com/renatoteodoro/smpi#

---

## O que é o SMPI?

O SMPI monitora equipamentos industriais em tempo real. Quando um sensor detecta uma anomalia, o sistema identifica o tipo de problema, busca ocorrências históricas semelhantes e gera automaticamente uma recomendação de manutenção — baseada nos manuais técnicos da empresa.

---

## Perfis de Acesso

| Perfil | Quem é | O que pode fazer |
|---|---|---|
| **Administrador** | Gestor da planta | Acesso total: usuários, equipamentos, configurações |
| **Técnico de Manutenção** | Técnico responsável | Visualizar e agir sobre eventos, prescrições e documentos |
| **Visualizador** | Engenheiro/Gestor | Somente leitura — dashboards e relatórios |

---

## 1. Acesso ao Sistema

### Entrar

1. Acesse https://www.techteo.com.br
2. Digite o **e-mail:** *renatoteodoro2@gmail.com*
3. Digite a**senha:** *Smpi@2026*
4. Clique em **Entrar**

### Esqueci minha senha

1. Na tela de login, clique em **Esqueceu a senha?**
2. Informe seu e-mail
3. Você receberá um link por e-mail para redefinir a senha

> **No momento esta função está desativada!** O cadastro de novos usuários é feito pelo **Administrador** — não há autocadastro.

---

## 2. Dashboard Principal

Após o login, você é direcionado ao **Dashboard** — a visão geral do sistema.

### O que você vê

- **Total de equipamentos** monitorados
- **Leituras recebidas** (total histórico)
- **Eventos com problema** detectados
- **Defeitos mais frequentes**

### Gráficos disponíveis

- Ocorrências ao longo do tempo (linha)
- Frequência por tipo de defeito (barras)
- Ranking de equipamentos com mais problemas

> Acesso rápido pelo menu lateral: **Dashboard**

---

## 3. Equipamentos

Caminho: menu lateral → **Equipamentos**

### Ver lista de equipamentos

Exibe todos os equipamentos cadastrados com status (ativo, inativo, em manutenção).

### Ver detalhes de um equipamento

Clique no nome do equipamento para ver:
- Informações gerais (tipo, setor, status)
- Últimas leituras de sensor
- Pontos de medição instalados

### Resumo com IA

Na tela de detalhes do equipamento, clique em **Resumir com IA**. O sistema gera um resumo inteligente do histórico do equipamento. Você será notificado quando estiver pronto.

### Cadastrar equipamento *(somente Admin e Técnico)*

1. Clique em **Novo Equipamento**
2. Preencha: nome, tipo, setor, status
3. Clique em **Salvar**

### Adicionar ponto de medição *(somente Admin e Técnico)*

Na tela de detalhes do equipamento, clique em **Adicionar Ponto de Medição** e informe o eixo (X ou Z) e tipo de sensor.

---

## 4. Eventos de Sensor (Monitoramento)

Caminho: menu lateral → **Monitoramento**

### O que é um evento?

Cada vez que o sensor envia uma leitura de vibração, temperatura ou aceleração, ela é registrada como um **evento**. O sistema analisa automaticamente se é um estado normal ou um problema.

### Lista de eventos

Exibe todos os eventos com filtros por:
- Equipamento
- Tipo de defeito
- Data (início e fim)
- Status (estado / problema)

### Detalhes de um evento

Clique no evento para ver:
- Métricas do sensor (velocidade, aceleração, temperatura, etc.)
- Classificação: **Estado** (normal, baseline, etc.) ou **Problema**
- Prescrição gerada (se houver)

### Iniciar análise manualmente

Se o evento ainda não foi analisado, clique em **Analisar**. O sistema executa o pipeline de IA e gera a prescrição. Você será notificado quando concluir.

### Resumo com IA

Clique em **Resumir evento** para obter uma análise contextualizada do evento em linguagem natural.

### Registrar evento manualmente *(somente Admin e Técnico)*

1. Clique em **Novo Evento**
2. Selecione o ponto de medição
3. Preencha as métricas disponíveis
4. Clique em **Salvar** — a análise é disparada automaticamente

---

## 5. Prescrições (Recomendações)

Caminho: menu lateral → **Prescrições**

### O que é uma prescrição?

É a recomendação gerada pelo sistema após analisar um evento problemático. Contém:

- **Tipo de defeito** identificado
- **Quantidade de ocorrências** históricas similares
- **Frequência** com que esse defeito ocorre
- **Instruções de solução** — baseadas nos manuais técnicos da empresa

### Indicador de confiabilidade

Cada prescrição exibe se é **fundamentada** (baseada em documentação existente) ou **sem documentação**:

- ✅ **Fundamentada** — instruções geradas a partir dos manuais da empresa, com citação das fontes
- ⚠️ **Sem documentação** — o sistema identificou o defeito mas não encontrou manual correspondente. Neste caso, ele **não inventa** uma solução — apenas informa e sugere cadastrar um novo documento técnico

---

## 6. Base de Conhecimento (Documentos)

Caminho: menu lateral → **Documentos**

### O que é a base de conhecimento?

É o repositório de manuais técnicos, procedimentos e relatórios de manutenção da empresa. O sistema lê e indexa esses documentos automaticamente para fundamentar as prescrições.

### Ver documentos indexados

Lista todos os documentos com status de indexação (processando / indexado) e número de trechos gerados.

### Adicionar novo documento *(somente Admin e Técnico)*

1. Clique em **Novo Documento**
2. Preencha o título e o tipo de defeito associado (opcional)
3. Faça o upload do arquivo (PDF, DOCX ou TXT)
4. Clique em **Salvar** — a indexação começa automaticamente em segundo plano

> Você receberá uma notificação quando o documento estiver indexado e disponível para uso nas prescrições.

### Quando adicionar um documento?

Sempre que o sistema emitir o aviso *"Defeito sem documentação"* em uma prescrição. Cadastre o manual ou procedimento correspondente para que as próximas ocorrências sejam fundamentadas.

---

## 7. Chat com IA

Caminho: menu lateral → **Chat**

### O que é o Chat?

Um assistente inteligente que responde perguntas sobre os dados do sistema — equipamentos, eventos, defeitos, prescrições e histórico. Funciona como uma conversa em tempo real.

### Exemplos de perguntas

- *"Quais defeitos ocorreram nas últimas 2 semanas?"*
- *"Qual equipamento teve mais problemas este mês?"*
- *"O que diz a prescrição do evento 114387?"*
- *"Quais são os defeitos mais frequentes no setor de produção?"*

### Como usar

1. Clique em **Nova Conversa** ou escolha uma sessão existente
2. Digite sua pergunta no campo de texto
3. A resposta aparece em tempo real, palavra por palavra
4. O histórico da conversa fica salvo para consulta posterior

### Chatbot Flutuante

O ícone de chat no canto inferior direito de qualquer tela do sistema abre o **chatbot flutuante** — acesso rápido ao assistente sem sair da página atual. Clique no ícone para abrir ou fechar.

---

## 8. Relatórios

Caminho: menu lateral → **Relatórios**

### Tipos de relatório disponíveis

| Relatório | Conteúdo |
|---|---|
| Histórico de eventos | Leituras por período e equipamento |
| Frequência de defeitos | Ranking de defeitos no período |
| Prescrições geradas | Recomendações com fontes documentais |
| Saúde dos equipamentos | Status e ocorrências por equipamento |

### Gerar um relatório

1. Clique em **Novo Relatório**
2. Selecione o tipo de relatório
3. Informe o período (data início e data fim)
4. Clique em **Gerar**

A geração ocorre em segundo plano. Você receberá uma notificação quando estiver pronto.

### Baixar o relatório

Na lista de relatórios, clique em **Baixar** para obter o arquivo em **PDF** ou **CSV**.

---

## 9. Catálogo de Defeitos

Caminho: menu lateral → **Defeitos**

Lista todos os tipos de defeito cadastrados no sistema com sua classificação (estado ou problema).

**Somente Administradores** podem cadastrar ou editar defeitos.

---

## 10. Notificações

O sino ( 🔔 ) no topo da tela exibe notificações do sistema, como:

- Prescrição gerada para um evento
- Documento indexado com sucesso
- Resumo com IA concluído
- Relatório pronto para download

Clique em uma notificação para ir diretamente à tela correspondente. Clique em **Marcar todas como lidas** para limpar a lista.

---

## 11. Atendimento via WhatsApp

Técnicos de campo podem interagir com o sistema diretamente pelo WhatsApp, sem precisar acessar o computador.

### O que é possível pelo WhatsApp

- Consultar eventos recentes
- Verificar prescrições de defeitos
- Perguntar sobre equipamentos
- Receber notificações de análise concluída

Basta enviar uma mensagem de texto para o número conectado ao sistema. O assistente responde automaticamente com base nos dados reais da planta.

---

## 12. Gestão de Usuários *(somente Administrador)*

Caminho: menu lateral → **Usuários**

### Cadastrar novo usuário

1. Clique em **Novo Usuário**
2. Preencha nome, e-mail e selecione o perfil (Administrador, Técnico ou Visualizador)
3. Clique em **Salvar**

O usuário receberá um e-mail para definir a própria senha.

### Editar usuário

Clique no ícone de edição ao lado do nome do usuário para alterar nome, e-mail, perfil ou status (ativo/inativo).

---

## 13. Meu Perfil

Clique no seu nome no topo da tela → **Meu Perfil** para atualizar seu nome e e-mail.

Para alterar a senha, use a opção **Esqueceu a senha?** na tela de login.

---

## Dúvidas frequentes

**O sistema está analisando um evento mas não aparece a prescrição — o que fazer?**
A análise é assíncrona. Aguarde a notificação no sino ( 🔔 ) que indica quando a prescrição foi gerada. Em casos de lentidão, atualize a página.

**A prescrição diz "sem documentação" — o que significa?**
O sistema identificou o tipo de defeito mas não há manual técnico cadastrado para ele. Adicione o documento correspondente em **Documentos → Novo Documento** associando-o ao defeito identificado.

**Como enviar eventos de sensores automaticamente?**
O sistema possui uma API REST. O endpoint é `POST https://www.techteo.com.br/api/v1/readings/` autenticado por API Key. Consulte a documentação em `/api/docs/` ou fale com o Administrador para obter a chave de acesso.

**Posso acessar pelo celular?**
Sim. O sistema é responsivo e funciona em navegadores de celular. Além disso, técnicos de campo podem usar o **WhatsApp** para consultar o sistema sem abrir o navegador.
