# Setup — mcp-brasil (fork pessoal)

Fork de [gabrielcarvalhodev/mcp-brasil](https://github.com/gabrielcarvalhodev/mcp-brasil) com deploy automático no Google Cloud Run.

---

## Infraestrutura

| Recurso | Valor |
|---------|-------|
| **GCP Project** | `mcp-brasil-56555` |
| **Billing** | Custos Forensics (`0137E3-FD9106-71DEFA`) |
| **Região** | `southamerica-east1` (São Paulo) |
| **Artifact Registry** | `southamerica-east1-docker.pkg.dev/mcp-brasil-56555/mcp-brasil` |
| **Service Account** | `mcp-brasil-deployer@mcp-brasil-56555.iam.gserviceaccount.com` |
| **Cloud Run URL** | `https://mcp-brasil-947444474262.southamerica-east1.run.app` |
| **MCP endpoint** | `https://mcp-brasil-947444474262.southamerica-east1.run.app/mcp` |

---

## Autenticação

**Modo:** Google OAuth (`MCP_BRASIL_AUTH_MODE=oauth`)

**OAuth Client:** `MCP Brasil Claude` no projeto GCP  
**Redirect URI registrada:** `https://mcp-brasil-947444474262.southamerica-east1.run.app/auth/callback`

Para rever/editar as credenciais OAuth:  
`https://console.cloud.google.com/apis/credentials?project=mcp-brasil-56555`

---

## GitHub Secrets configurados

Todos os secrets estão em **Settings → Secrets and variables → Actions** do repositório.

| Secret | Descrição |
|--------|-----------|
| `GCP_PROJECT_ID` | `mcp-brasil-56555` |
| `GCP_REGION` | `southamerica-east1` |
| `GCP_SA_KEY` | JSON da Service Account (deploy) |
| `MCP_BRASIL_BASE_URL` | URL pública do Cloud Run |
| `MCP_BRASIL_API_TOKEN` | Token interno do servidor |
| `GOOGLE_CLIENT_ID` | OAuth Google |
| `GOOGLE_CLIENT_SECRET` | OAuth Google |
| `ANTHROPIC_API_KEY` | Claude Haiku (tools de descoberta) |
| `BRAPI_TOKEN` | Cotações B3 |
| `TRANSPARENCIA_API_KEY` | Portal da Transparência |
| `DATAJUD_API_KEY` | CNJ / DataJud |

---

## Workflows

### `deploy.yml` — Deploy automático
- **Dispara:** a cada push na `main`
- **O que faz:** build da imagem Docker → push no Artifact Registry → deploy no Cloud Run
- **Ver logs:** [Actions](../../actions/workflows/deploy.yml)

### `sync-upstream.yml` — Sync com o repositório original
- **Dispara:** toda segunda-feira às 9h (horário de Brasília)
- **O que faz:** merge do upstream → push na `main` → aciona `deploy.yml` automaticamente
- **Manual:** pode rodar pelo botão "Run workflow" na aba Actions

---

## Conectar no Claude.ai

1. Acesse **Settings → Integrations → Add custom connector**
2. Preencha:
   - **Nome:** `MCP Brasil`
   - **URL:** `https://mcp-brasil-947444474262.southamerica-east1.run.app/mcp`
3. Clique em **Adicionar** — uma janela de login do Google abrirá
4. Autentique com `meister.gui@gmail.com`

---

## Rotina de monitoramento

Uma rotina semanal no Claude.ai (toda segunda às 9h) monitora o upstream em busca de suporte a múltiplos provedores LLM (Gemini, OpenAI). Se detectado, envia notificação.

Gerenciar: `https://claude.ai/code/routines/trig_01LeRM4eqwbnpKmadVjZKijm`

---

## Comandos úteis

```bash
# Ver logs do servidor em tempo real
gcloud run services logs tail mcp-brasil \
  --region=southamerica-east1 \
  --project=mcp-brasil-56555

# Atualizar uma variável de ambiente sem redeploy completo
gcloud run services update mcp-brasil \
  --region=southamerica-east1 \
  --project=mcp-brasil-56555 \
  --set-env-vars="CHAVE=valor"

# Ver URL e status do serviço
gcloud run services describe mcp-brasil \
  --region=southamerica-east1 \
  --project=mcp-brasil-56555 \
  --format="value(status.url,status.conditions[0].status)"

# Forçar sync manual com upstream
# → Vá em Actions → "Sync from Upstream" → "Run workflow"
```

---

## Adicionar nova API key depois

1. Adicione o secret no GitHub: **Settings → Secrets → New repository secret**
2. Adicione a variável no `deploy.yml` (no bloco de `ENV_VARS`)
3. Faça push — o deploy acontece automaticamente
