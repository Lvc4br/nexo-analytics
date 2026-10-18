# Contrato da API

Prefixo funcional: `/api/v1`. O backend é FastAPI e usa JSON UTF-8. Em ambientes publicados, a API deve ser acessada por HTTPS.

## Rotas

| Método e rota | Acesso | Função |
|---|---|---|
| `GET /health` | Público | Verifica se o processo responde. |
| `POST /api/v1/auth/login` | Público | Valida as credenciais do administrador e devolve bearer token curto. |
| `GET /api/v1/auth/me` | Bearer | Retorna o e-mail da sessão autenticada. |
| `POST /api/v1/auth/logout` | Bearer | Confirma a sessão; a interface apaga o token local. O token assinado expira pelo próprio prazo. |
| `POST /api/v1/collect` | Público com origem e site validados | Recebe um evento minimizado do tracker. |
| `GET /api/v1/analytics/overview?days=7\|30\|90` | Bearer | Combina Vercel e Nexo e devolve métricas agregadas. |

## Coleta de eventos

`POST /api/v1/collect` recebe eventos do navegador. Não exige login, porque o tracker roda publicamente no portfólio; valida `Origin`, `site_id`, formato, caminho e limite de requisições. O identificador do site é público, não é uma credencial.

Exemplo:

```json
{
  "event_id": "c25395c7-49ef-4bbb-a24d-0f9f719b4fd1",
  "site_id": "lvc4br-lv-portfolio",
  "session_id": "f79f232b-bb71-4a77-95c7-21691b096458",
  "event_name": "page_view",
  "path": "/projects",
  "device_type": "desktop",
  "browser_name": "chrome",
  "os_name": "windows"
}
```

`event_name` aceita letras, números e `_ . : -`, começa com letra e tem até 80 caracteres. `path` começa com `/`, tem até 300 caracteres e não aceita query string nem fragmento. `device_type`, `browser_name` e `os_name` são categorias permitidas, não o user-agent bruto. `duration_ms` só é aceito em `page_duration`, entre 0 e 86.400.000 ms. O horário é definido pelo servidor, não pelo relógio do navegador. IP e `Referer` não são gravados na tabela de eventos.

Exemplo de amostra de tempo ativo:

```json
{
  "event_id": "c25395c7-49ef-4bbb-a24d-0f9f719b4fd2",
  "site_id": "lvc4br-lv-portfolio",
  "session_id": "f79f232b-bb71-4a77-95c7-21691b096458",
  "event_name": "page_duration",
  "path": "/projects",
  "device_type": "desktop",
  "browser_name": "chrome",
  "os_name": "windows",
  "duration_ms": 18400
}
```

Respostas `202` indicam evento aceito. Repetições do mesmo `event_id` retornam `202` com `duplicate: true` sem criar nova linha. A origem deve estar em `PORTFOLIO_ALLOWED_ORIGINS` e o site precisa coincidir com `PORTFOLIO_SITE_ID`; caso contrário a API responde `403` ou `404`. O limite padrão em memória é 120 eventos por minuto e por origem.

## Resposta de analytics

`GET /api/v1/analytics/overview?days=30` requer `Authorization: Bearer <token>`. A resposta inclui:

- `sources`: estado das integrações `vercel`, `nexo` e `vercel_events`;
- `metrics.pageviews_source`: `vercel` quando a consulta Vercel funciona ou `nexo` como fallback;
- `metrics.pageviews` e `metrics.visitors`: fonte principal selecionada, sem somar pageviews dos dois provedores;
- `metrics.nexo_pageviews`, `metrics.nexo_sessions` e `metrics.engaged_sessions`: coleta própria em separado;
- `events`: eventos personalizados recebidos pelo Nexo;
- `vercel_events`: eventos agregados pela Vercel, mantidos separados;
- `traffic`, `popular_pages`, `comparison` e `insights`: análises calculadas para o período escolhido.
- `devices`, `browsers` e `operating_systems`: contagens agregadas com a fonte indicada em cada item. Para Nexo, `visitors` significa sessões observadas, não aparelhos/pessoas únicas;
- `regions`: países/regiões aproximados vindos da Vercel ou dos cabeçalhos confiáveis do proxy da API;
- `time_metrics` e os tempos em `popular_pages`: amostras de duração ativa coletadas pelo Nexo; cada resumo contém média, mínimo, máximo e quantidade de amostras;
- `metrics.bounce_rate_percent`: porcentagem estimada de sessões Nexo com exatamente um pageview;
- `metrics.device_profile_count`: número de combinações distintas tipo/navegador/sistema observadas, não número de aparelhos.

Os valores de visitantes da Vercel são somas de contagens diárias. Os valores Nexo são sessões pseudônimas baseadas em `sessionStorage`; nenhum dos dois representa identidade civil.

`GEOLOCATION_PROXY` aceita `none`, `vercel` ou `cloudflare`. A API só lê os cabeçalhos de localização do provedor explicitamente configurado. Para `vercel`, use `x-vercel-ip-country` e `x-vercel-ip-country-region`; para `cloudflare`, usa-se apenas o país de `cf-ipcountry`. Configure um valor diferente de `none` somente quando a API estiver realmente atrás desse proxy. A API local padrão não recebe localização confiável. País/região nunca são localização precisa.

## Autenticação

O token administrativo é assinado e expira conforme `SESSION_TTL_MINUTES` (30 minutos por padrão). O frontend o mantém somente em memória. `/logout` não revoga tokens previamente emitidos; eles deixam de valer ao expirar.

## Persistência e erros

O desenvolvimento local usa SQLite em `services/api/.data/nexo.sqlite3`. A produção exige PostgreSQL persistente via `DATABASE_URL`; a API falha no início se `APP_ENV=production` sem banco durável. Tabelas são inicializadas no startup da aplicação e eventos antigos são removidos conforme `TRACKER_EVENT_RETENTION_DAYS`.

FastAPI usa `422` para entrada malformada, `401` para sessão ausente/expirada, `403` para origem rejeitada, `404` para site ID desconhecido e `429` para limite de coleta excedido. Falhas da Vercel não derrubam o dashboard: a API recorre às métricas Nexo se houver eventos próprios.
