# Simples Editor

IDE web para escrever, compilar e executar programas na linguagem **SIMPLES** — uma linguagem didática em português estruturado — diretamente no navegador, sem instalação local.

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS + TanStack Router |
| Editor | Monaco Editor + xterm.js |
| Backend | Python 3.11+ / Flask |
| Infra | Docker Compose + Nginx |

## Pré-requisitos

- Docker Engine 24+ ou Docker Desktop
- Docker Compose v2
- Conta no [Supabase](https://supabase.com) (free tier)

## Setup local

```bash
# 1. Clonar o repositório
git clone https://github.com/MariaEduardaBatt/simples-editor.git
cd simples-editor

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com SUPABASE_URL, SUPABASE_ANON_KEY e SUPABASE_API_KEY

# 3. Subir os serviços
docker compose up --build -d

# 4. Acessar
# Frontend: http://localhost
# Health check: http://localhost/api/health
```

> **Nota:** Os arquivos `docker-compose.yml` e `.env.example` ainda estão em desenvolvimento (Sprint 1). Consulte o [PRD](prd_simples_online.md#14-6-deployment-local-desenvolvimento) para a configuração de referência.

## Estrutura do projeto

```
simples-editor/
├── backend/          # API Flask + integração Supabase
├── frontend/         # SPA React + Monaco + xterm.js
├── docs/             # Documentação complementar
├── prd_simples_online.md   # Product Requirements Document
├── SPRINTS.md        # Plano de sprints e entregas
└── PROGRESS.md       # Acompanhamento do progresso
```

## Documentação

- **PRD** — [prd_simples_online.md](prd_simples_online.md) — visão completa do produto, arquitetura, requisitos e decisões técnicas.
- **Sprints** — [SPRINTS.md](SPRINTS.md) — plano de entregas por sprint com Definition of Done.
- **Progresso** — [PROGRESS.md](PROGRESS.md) — acompanhamento das tarefas concluídas e pendentes.

## Projeto original

Este trabalho é baseado no repositório [LucaS4nt0s/simples-online](https://github.com/LucaS4nt0s/simples-online).
