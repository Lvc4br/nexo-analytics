# Tracker JavaScript Nexo

O pacote local está em `packages/tracker-sdk`. Ele é JavaScript ESM sem dependências e não depende de React, Vite, Vercel nem de um provedor de hospedagem.

## Uso

Como o portfólio atual está em outro repositório e o pacote ainda não foi publicado no npm, copie `packages/tracker-sdk/src/index.js` para o código do site e importe a função:

```js
import { createNexoTracker } from "./nexo-tracker.js";

const tracker = createNexoTracker({
  endpoint: "https://SUA-API-NEXO/api/v1/collect",
  siteId: "lvc4br-lv-portfolio",
  trackDevelopment: import.meta.env.DEV,
});

tracker.track("resume_open");
```

No LV_Portfolio, leia `endpoint` de `VITE_NEXO_COLLECT_URL` e `siteId` de `VITE_NEXO_SITE_ID`; não hardcode a URL de API por ambiente. O snippet React completo está em [docs/INTEGRATION_TRACKER.md](./INTEGRATION_TRACKER.md).

## Opções e métodos

- `endpoint` (obrigatório): URL pública HTTPS de `POST /api/v1/collect`.
- `siteId` (obrigatório): valor igual a `PORTFOLIO_SITE_ID` na API.
- `autoPageViews` (opcional, padrão `true`): registra a rota inicial e transições de History API/`popstate` sem query strings ou fragmentos.
- `enabled` (opcional, padrão `true`): permite desligar o tracker.
- `trackDevelopment` (opcional, padrão `false`): libera a coleta em `localhost` para testar.
- `track(eventName)`: registra interação personalizada sem propriedades arbitrárias.
- `page()`: registra manualmente a rota atual; chamadas repetidas para a mesma rota não duplicam a visualização automática.
- `destroy()`: remove listeners e wrappers de histórico.

Por padrão, o SDK pausa a coleta quando `navigator.doNotTrack === "1"`, quando `window.__nexoAnalyticsDisabled` é `true`, quando `enabled` é `false` ou quando executa em localhost sem `trackDevelopment`.
Se `endpoint` ou `siteId` estiver ausente, ele fica inativo sem interromper o site.

## Payload

O navegador envia `event_id`, `site_id`, `session_id`, `event_name` e `path`. O `session_id` aleatório é mantido em `sessionStorage`; o evento usa um ID aleatório para permitir deduplicação. Não há cookie persistente, fingerprinting, propriedades livres, IP, referenciador, query string, fragmento ou conteúdo de formulário no payload.

O coletor valida o payload novamente. `Origin` ajuda a limitar as origens aceitas, mas é público e pode ser falsificado fora do navegador; produção deve aplicar rate limiting compartilhado no gateway além do limite local em memória.

## Testar

Dentro de `packages/tracker-sdk`, execute `npm test`. Os testes verificam pageviews, eventos, navegação SPA, remoção de query/fragment e respeito a Do Not Track.
