# Runbook de Resposta a Incidentes — Sandbox

**Data:** 2026-06-17
**Responsável:** Maria Eduarda Batista Henrique
**Referência:** [Issue #41](https://github.com/MariaEduardaBatt/simples-editor/issues/41)

## Níveis de severidade

| Nível | Descrição | Exemplo |
|-------|-----------|---------|
| **BAIXO** | Comportamento suspeito, sem prova de escape | Aluno consegue ler `--help` de um binário fora do esperado |
| **MÉDIO** | Indício de escape parcial | Arquivo criado fora de `/tmp`, processo filho fora do limite |
| **ALTO** | Escapou do container | Container com acesso à rede, escrita em `/etc`, leitura de secrets |
| **CRÍTICO** | Acesso ao host | Container quebrou o isolamento do Docker e executou comandos no host |

## Procedimento de contenção imediata

### 1. Isolar o container suspeito

```bash
# Identificar o container pelo nome ou PID
docker ps --filter "name=simples-runner"

# Parar imediatamente
docker kill <container_id> --signal=SIGKILL

# Remover (força, mesmo que --rm falhe)
docker rm -f <container_id>
```

### 2. Bloquear o usuário

1. Acessar o Supabase Dashboard → **Authentication → Users**
2. Suspender a conta do usuário que disparou o incidente
3. Anotar o `user_id` e `email` para o post-mortem

### 3. Revogar tokens ativos

```bash
# Se houver tokens JWT conhecidos (ex: logs), invalidar via Supabase Admin API
curl -X POST https://<project>.supabase.co/auth/v1/admin/users/<user_id>/logout \
  -H "apikey: <service_role_key>" \
  -H "Authorization: Bearer <service_role_key>"
```

### 4. Coletar evidências

```bash
# Logs do container (stdout/stderr do qemu)
docker logs <container_id> 2>&1 > incidente_<id>.log

# Inspect para ver flags reais usadas
docker inspect <container_id> > incidente_<id>.inspect.json

# Logs do backend no momento do incidente
docker logs simples-backend --since=<timestamp_incidente>
```

## Procedimento de recuperação

### Após um incidente de nível MÉDIO ou superior

1. **Isolar o nó de execução** — Remover o container do pool (se houver pool) e não escalonar novos jobs para ele
2. **Revisar as flags de segurança do sandbox** (conforme auditado na issue #40)
   - `--read-only` está presente?
   - `--network=none` está presente?
   - `--pids-limit=64` está presente?
   - `--cap-drop=ALL` está presente?
   - `--user=65534:65534` está presente?
3. **Validar a imagem do runner** — Rebuild da imagem `simples-runner` para garantir que não há camada contaminada
4. **Rodar suíte de testes de segurança** antes de reabrir o serviço
   ```bash
   cd backend
   pytest -v -m integration
   ```
5. **Restartar o backend** — `docker compose restart backend`

### Após um incidente CRÍTICO

1. Os passos acima, **mais**:
2. Rotacionar **todas** as chaves de API (Supabase `anon`/`service_role`, secrets do backend, chaves do Docker Hub se houver)
3. Escanear o host em busca de processos, cron jobs ou containers remanescentes
4. Notificar o professor/orientador imediatamente

## Post-mortem

Para todo incidente de nível MÉDIO ou superior, preencher:

| Campo | Exemplo |
|-------|---------|
| **Data/hora do incidente** | 2026-06-17T14:30:00-03:00 |
| **User ID** | `uuid-do-usuario` |
| **Email** | `aluno@exemplo.com` |
| **Código executado** | (colar o código SIMPLES que disparou) |
| **Severidade** | BAIXO / MÉDIO / ALTO / CRÍTICO |
| **Vetor** | Ex: fork bomb, escrita em `/usr`, tentativa de rede |
| **Flags que deveriam bloquear** | Ex: `--pids-limit=64`, `--read-only` |
| **Flags estavam ativas?** | Sim / Não (se não, por quê?) |
| **Ação tomada** | Kill + bloqueio de user + rebuild |
| **Responsável** | Nome de quem respondeu |
| **Lições aprendidas** | O que mudar no código ou processo para evitar recorrência |

O registro deve ser salvo em `docs/incidentes/<data>_<severidade>.md`.

## Checklist rápido (plantonista)

- [ ] `docker kill` no container suspeito
- [ ] `docker rm -f` no container
- [ ] Suspender usuário no Supabase
- [ ] Coletar logs (`docker logs` + `docker inspect`)
- [ ] Revisar flags de segurança
- [ ] Rebuild da imagem `simples-runner` (se MÉDIO+)
- [ ] Rodar `pytest -v -m integration`
- [ ] Se CRÍTICO: rotacionar chaves + notificar orientador

## Referências

- [Auditoria de Sandbox Escape #40](audit-sandbox-escape-40.md)
- [PRD §11.6 — Threat model resumido](../prd_simples_online.md#11-6-threat-model-resumido)
- [PRD §19 — Riscos e mitigações](../prd_simples_online.md#19-riscos-e-mitigações)
- [SPRINTS.md — Sprint 5](../SPRINTS.md#sprint-5--hardening-observability)
