# Fluxo de Contribuição

## 1. Escolha uma Issue

- Navegue até a aba [Issues](https://github.com/MariaEduardaBatt/simples-editor/issues)
- Escolha uma issue atribuída a você ou peça para ser assignado
- Issues seguem o formato `feat(escopo): descrição` (ex: `feat(frontend): add mock run action`)

## 2. Crie uma Branch

Crie uma branch a partir de `dev` com o nome padronizado:

```
git checkout dev
git pull origin dev
git checkout -b feat/<numero-da-issue>-<descricao-curta>
```

Exemplos:
- `feat/3-initial-readme`
- `feat/7-supabase-auth-integration`
- `feat/10-health-endpoint`
- `feat/12-monaco-editor`

> Use `fix/` para correções, `docs/` para documentação, `chore/` para tarefas de manutenção.

## 3. Desenvolva

- Siga os padrões do projeto (ESLint, indentação, convenções de nomenclatura)
- Commits devem seguir [Conventional Commits](https://www.conventionalcommits.org/):
  ```
  feat(escopo): mensagem no imperativo
  ^     ^        ^
  |     |        ex: "add login screen", "fix token validation"
  |     escopo: frontend, backend, devops, docs, auth, security
  tipo: feat, fix, chore, docs, refactor, test, style
  ```
- Commits pequenos e atômicos são preferíveis

## 4. Abra um Pull Request

1. Faça push da sua branch:
   ```
   git push origin feat/<numero-da-issue>-<descricao-curta>
   ```
2. No GitHub, abra um PR apontando **da sua branch para `dev`**
3. Preencha o template:
   - **O que muda?** — resumo de 1-2 frases
   - **Por quê?** — contexto e `Closes #N` para vincular a issue
   - **Como testar?** — passos para o reviewer
   - **Screenshots/GIFs** — se aplicável (mudanças de UI)
4. Adicione labels (frontend, backend, devops, docs, security) e selecione o milestone (sprint)

## 5. Review

- Pelo menos um membro do time deve aprovar o PR
- O reviewer verifica:
  - Código segue os padrões do projeto
  - Testes passam
  - Não há regressões
  - Documentação foi atualizada se necessário
- Se houver sugestões, o autor faz os ajustes e solicita novo review

## 6. Merge

- O merge é feito pelo **autor do PR** após aprovação
- Estratégia: **Squash and merge** (mantém o histórico limpo)
- A branch é deletada automaticamente após o merge
- A issue vinculada é fechada automaticamente (`Closes #N` no body do PR)

## 7. Auto-sync do PROGRESS.md

- Um workflow do GitHub Actions (`sync_progress.yml`) atualiza automaticamente o `PROGRESS.md` quando PRs são mergeados ou issues fechadas
- O script `scripts/sync_progress.py` faz o matching entre issues/PRs fechados e os itens do checklist

## Resumo Visual

```
Issue → Branch (feat/N-desc) → Commits (conventional) → Push → PR (para dev)
→ Review (approval) → Squash & merge → Branch deletada → Issue fechada
→ PROGRESS.md atualizado automaticamente
```
