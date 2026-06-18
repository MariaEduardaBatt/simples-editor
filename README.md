# Simples Editor

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

IDE web para escrever, compilar e executar programas na linguagem **SIMPLES** — uma linguagem didática em português estruturado — diretamente no navegador, sem instalação local.

Projeto final da disciplina de **Compiladores** — [IFSULDEMINAS - Campus Poços de Caldas](https://portal.pcs.ifsuldeminas.edu.br).

## Funcionalidades

- **Editor de código** com Monaco Editor, syntax highlighting para SIMPLES, temas dark e suporte a markers de erro
- **Compilação** on-line via pipeline `simplesc → nasm → ld` com timeouts e feedback de erros por linha
- **Execução interativa** via WebSocket + terminal xterm.js com suporte a `leia` e `escreva`
- **Painel NASM** read-only com o assembly gerado lado a lado
- **Autenticação** via Supabase (email/senha)
- **Sandbox seguro** com Docker: sem rede, sem root, sem escrita, limite de memória e kill em loop infinito
- **Rate limiting**, logs estruturados e métricas Prometheus
- **Exemplos prontos**: Hello World, Fatorial, Fibonacci, Tabuada

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS |
| Editor | Monaco Editor + xterm.js |
| Backend | Python 3.11+ / Flask + Gunicorn |
| Compilador | [simples-compiler](https://github.com/LucaS4nt0s/simples-compiler) (C) |
| Execução | Docker + QEMU user-mode (i386) |
| Autenticação | Supabase Auth |
| Infra | Docker Compose + Nginx |

## Layout

```
┌──────────────────────────────────────────────┐
│  Header  │  usuário@email  │  Sair           │
├───────────────────────┬──────────────────────┤
│                       │                      │
│   Editor SIMPLES      │   NASM Gerado       │
│   (Monaco Editor)     │   (read-only)       │
│                       │                      │
├───────────────────────┴──────────────────────┤
│  Terminal (xterm.js)                         │
│  $ Executando programa...                    │
│  Digite um número:                           │
└──────────────────────────────────────────────┘
```

## Screenshots

> _Nota: Adicionar screenshots da aplicação em funcionamento._

## Demonstração

Assista ao vídeo de demonstração (2-3 min):

📹 [`docs/demo.mp4`](docs/demo.mp4)

## Pré-requisitos

- Docker Engine 24+ ou Docker Desktop
- Docker Compose v2
- Conta no [Supabase](https://supabase.com) (free tier)

## Setup local

```bash
# 1. Clonar o repositório
git clone git@github.com:MariaEduardaBatt/simples-editor.git
cd simples-editor

# 2. Inicializar submódulo do compilador
git submodule update --init --recursive

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com SUPABASE_URL, SUPABASE_ANON_KEY e SUPABASE_API_KEY

# 4. Subir os serviços
docker compose up --build -d

# 5. Acessar
open http://localhost
```

## Estrutura do projeto

```
simples-editor/
├── backend/                # API Flask + integração Supabase
│   ├── src/simples_backend/
│   │   ├── app.py          # App factory, blueprints & WebSocket
│   │   ├── auth.py         # JWT verification (HS256 / JWKS)
│   │   ├── config.py       # Config via env vars
│   │   ├── metrics.py      # Prometheus metrics
│   │   ├── rate_limiter.py # Sliding-window rate limiter
│   │   ├── routes/         # health, compile, auth, limits, run_ws
│   │   └── services/       # compiler_service, execution_service, execution_strategy
│   └── tests/              # Testes unitários e de integração
├── frontend/               # SPA React + Monaco + xterm.js
│   ├── src/
│   │   ├── auth/           # AuthContext, ProtectedRoute
│   │   ├── components/     # SimplesEditor, NasmPanel, TerminalPanel, Toolbar
│   │   ├── hooks/          # useRunWebSocket
│   │   └── pages/          # LoginPage, AppShell
│   ├── e2e/                # Playwright E2E tests
│   └── test/               # Vitest unit tests
├── runner/                 # Docker image do sandbox (Debian + QEMU)
├── nginx/                  # Reverse proxy config
├── simples-compiler/       # Submódulo — compilador SIMPLES (C)
├── docs/                   # Documentação complementar
├── docker-compose.yml
├── prd_simples_online.md   # Product Requirements Document
├── SPRINTS.md              # Plano de sprints e entregas
└── PROGRESS.md             # Acompanhamento do progresso
```

## API Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/health` | Health check com status dos componentes |
| `POST` | `/api/compile` | Compila código SIMPLES e retorna NASM ou erros |
| `POST` | `/api/auth/verify` | Verifica token JWT |
| `GET` | `/api/limits` | Retorna limites de execução configurados |
| `WS` | `/ws/run` | WebSocket para compilar + executar interativamente |
| `GET` | `/metrics` | Métricas Prometheus (acesso interno apenas) |

## Testes

```bash
# Backend (pytest)
cd backend
pytest                          # unit + integration
pytest --cov --cov-report=term  # com cobertura (>70%)

# Frontend (vitest)
cd frontend
npm run test                    # unit

# E2E (Playwright)
npm run test:e2e                # requer stack rodando
```

## Equipe

| Membro | Papel |
|---|---|
| [Luca Samuel dos Santos](https://github.com/LucaS4nt0s) | Desenvolvimento |
| [Maria Eduarda Batista Henrique](https://github.com/MariaEduardaBatt) | Desenvolvimento |

## Licença

MIT.
