# TECH_DEBT.md — Interactive TODO for Technical Debt

> Track bugs, incompatibilities, mocks, and incomplete implementations.
> Update this file whenever you find something that needs attention later.

## Legend

- `[ ]` — Open (needs work)
- `[~]` — In progress
- `[x]` — Resolved

---

## Bootstrap Phase

- [x] **mount() API mismatch** — `feature.py` used `mount("/path", server)` instead of FastMCP v3's `mount(server, namespace=name)`. Fixed.
- [x] **list_tools() accessed private API** — `_tool_manager._tools` is private FastMCP internals. Removed method to avoid mypy strict failures.
- [x] **_shared/http_client.py** — `create_client()` + `http_get()` with retry + exponential backoff + 429/5xx.
- [x] **_shared/formatting.py** — `markdown_table`, `format_brl`, `format_number_br`, `format_percent`, `truncate_list`.
- [x] **_shared/cache.py** — `TTLCache` class + `@ttl_cache(ttl=300)` decorator for async functions.
- [x] **settings.py** — Env var overrides: `HTTP_TIMEOUT`, `HTTP_MAX_RETRIES`, `HTTP_BACKOFF_BASE`, `USER_AGENT`.
- [x] **pyproject.toml dependency-groups** — Migrated from `[project.optional-dependencies]` to `[dependency-groups]`. `make dev` uses `uv sync --group dev`.
- [x] **justfile removed** — Replaced by Makefile.

## Core — Open

- [x] **Response size limiting for LLM context** — APIs can return huge payloads (e.g., 5000+ municipios). Need a strategy to truncate/summarize responses to avoid blowing LLM context windows. See `_shared/formatting.py:truncate_list` as starting point.

## Transparência Feature

- [x] **Resources e prompts faltando** — Feature tinha apenas tools/client/schemas. Adicionados resources.py (endpoints, bases de sanções, info da API) e prompts.py (auditoria_fornecedor, analise_despesas, verificacao_compliance) + server.py atualizado + 27 testes novos.
- [x] **API response shapes unverified** — Resolvido. Adicionado `_safe_parse_list()` com logging de warning para respostas inesperadas, guards em `_parse_bolsa_*` contra strings no lugar de dicts, e 20+ testes de edge cases (non-list, null fields, string fields).
- [x] **Rate limiting not enforced client-side** — Resolvido. Adicionado `_shared/rate_limiter.py` (sliding window 80 req/min) aplicado via `_get()`. `buscar_sancoes` refatorado para usar `_get()` ao invés de `http_get()` direto.
- [x] **Pagination not automatic** — Resolvido. Adicionado `_pagination_hint()` em tools.py que mostra "Use pagina=N+1" quando resultados >= DEFAULT_PAGE_SIZE e "Última página" quando < PAGE_SIZE em pagina > 1.
- [x] **Pre-existing mypy errors in lifespan.py and ibge/client.py** — Resolvido. mypy passa limpo em todos os 35+ arquivos.

## Câmara Feature

- [x] **Envelope extraction** — API wraps all responses in `{"dados": [...], "links": [...]}`. Handled by `_get()` helper that auto-extracts `dados` field. Tested with empty/missing dados.
- [x] **No client-side rate limiting** — Resolvido. RateLimiter(60 req/min) aplicado via `_get()`.
- [x] **Pagination is server-controlled** — By design. `_pagination_hint()` provides LLM-facing hints ("Use pagina=N+1"). Auto-pagination is not needed for MCP tools since the LLM controls iteration.

## Senado Feature

- [x] **Deeply nested JSON responses** — API returns structures like `data.ListaParlamentarEmExercicio.Parlamentares.Parlamentar`. Handled by `_deep_get(*keys)` helper with safe navigation.
- [x] **Single result as dict instead of list** — When only 1 result, API returns `{}` instead of `[{}]`. Handled by `_ensure_list()` coercion in all parsers.
- [x] **JSON via Accept header** — API requires `Accept: application/json` header. `JSON_HEADERS` constant passed through all requests.
- [x] **No client-side rate limiting** — Resolvido. RateLimiter(60 req/min) aplicado via `_get()`.
- [x] **No pagination support** — By design. `_pagination_hint()` suggests refining filters. Senado API returns full datasets; LLM-facing hints guide users to narrow queries.
- [x] **Votação nominal endpoint may vary** — Resolvido. Old plenário endpoint (`/plenario/lista/votacao`) deprecated and deactivated 2026-02-01. Migrated `listar_votacoes`, `obter_votacao`, `votacoes_recentes` to new `/votacao` API (flat JSON, camelCase). Parsers handle both old PascalCase and new camelCase formats. `votos_materia` still uses `/materia/votacoes/{id}` which remains active.
- [ ] **E-Cidadania tools not implemented** — Plan includes 9 web-scraping tools for e-Cidadania. Deferred to future sessions.
- [ ] **dados_abertos auxiliary tools not implemented** — Plan includes 4 additional tools. Deferred to future sessions.

## Known Limitations

- [x] **No CONTRIBUTING.md** — Resolvido. CONTRIBUTING.md criado com getting started, estrutura, como adicionar features, convenções, testes e PR guidelines.

---

*Last updated: 2026-03-22*
