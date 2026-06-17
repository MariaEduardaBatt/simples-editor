# Auditoria de Sandbox Escape — Issue #40

**Data:** 2026-06-17  
**Responsável:** Maria Eduarda Batista Henrique  
**Referência:** [Issue #40](https://github.com/MariaEduardaBatt/simples-editor/issues/40)

## Escopo

Auditar os vetores óbvios de escape do sandbox de execução de código SIMPLES.

## Flags de Segurança do Container

| Flag | Status | Verificado por |
|------|--------|---------------|
| `--read-only` | ✅ Corrigido nesta issue | `test_write_to_root_is_blocked` |
| `--network=none` | ✅ OK | `test_network_is_blocked` |
| `--pids-limit=64` | ✅ OK | `test_fork_bomb_is_blocked` |
| `--memory=128m --memory-swap=128m` | ✅ OK | `test_memory_limit_enforced` |
| `--user=65534:65534` | ✅ OK | `test_non_root_user_cannot_write_to_system_dirs` |
| `--cap-drop=ALL` | ✅ OK | `test_cap_drop_all_prevents_raw_sockets` |
| `tmpfs=/tmp:size=8m` | ✅ OK | `test_write_to_tmp_is_allowed` |

## Cenários Testados

### 1. Escrita em `/` (read-only filesystem)

**Resultado:** ✅ BLOQUEADO  
O container é iniciado com `--read-only`, impedindo escrita fora de `/tmp`.  
**Gap encontrado:** `read_only=True` não estava implementado no `create_host_config()` — foi corrigido nesta auditoria.

### 2. Fork bomb

**Resultado:** ✅ BLOQUEADO  
`pids_limit=64` impede a criação excessiva de processos. O container é morto pelo Docker ao atingir o limite.

### 3. Acesso à rede

**Resultado:** ✅ BLOQUEADO  
`network_mode="none"` remove completamente a interface de rede. Tentativas de `wget`, `ping` e conexões TCP falham.

### 4. Capacidades Linux

**Resultado:** ✅ BLOQUEADO  
`cap_drop=["ALL"]` remove todas as capacidades Linux. `ping` e operações que exigem `CAP_NET_RAW`, `CAP_SYS_ADMIN` etc. são bloqueadas.

### 5. Usuário não-root

**Resultado:** ✅ BLOQUEADO  
Container roda como `uid=65534` (nobody). Escrita em diretórios do sistema (ex: `/usr`) é bloqueada pelo kernel.

### 6. Limite de memória

**Resultado:** ✅ BLOQUEADO  
`mem_limit=128m` com `memswap_limit=128m` (sem swap) faz com que alocações acima de 128 MB resultem em OOM kill.

## Gaps Encontrados e Corrigidos

| Gap | Gravidade | Correção |
|-----|-----------|----------|
| `read_only` ausente no `create_host_config()` | Média | Adicionado `read_only=True` em `execution_strategy.py:47` |
| Ausência de logs de auditoria de segurança | Baixa | Adicionados logs estruturados (`sandbox_container_created`, `sandbox_container_started`, `sandbox_container_timeout`, `sandbox_container_finished`) em `execution_strategy.py` |
| Nenhum teste de integração real | Média | Criado `backend/tests/test_sandbox_audit.py` com 8 cenários de escape |

## Testes de Integração

Os testes de integração em `backend/tests/test_sandbox_audit.py` sobem containers Docker reais e verificam cada flag de segurança individualmente. Para executar:

```bash
cd backend
pytest -v -m integration
```

Os testes regulares (unitários) continuam sem necessidade de Docker:

```bash
cd backend
pytest -v -m "not integration"
```

## Conclusão

O sandbox está configurado corretamente para bloquear os vetores de escape mais óbvios. O gap mais relevante (`--read-only`) foi corrigido durante esta auditoria. Recomenda-se repetir esta auditoria a cada sprint ou sempre que flags de segurança forem alteradas.
