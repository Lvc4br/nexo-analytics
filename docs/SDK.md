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

## Payload e métricas próprias

O navegador envia `event_id`, `site_id`, `session_id`, `event_name`, `path` e categorias resumidas `device_type`, `browser_name` e `os_name`, classificadas localmente a partir do user-agent. O user-agent completo não é enviado. `session_id` aleatório é mantido em `sessionStorage`; o evento usa outro ID aleatório para permitir deduplicação. Não há cookie persistente, fingerprinting, propriedades livres, IP, referenciador, query string, fragmento ou conteúdo de formulário no payload.

Pageviews geram `page_view`. Para calcular o tempo ativo, o SDK mede com um relógio monotônico enquanto a página está visível e pausa quando a aba fica em segundo plano. Ao mudar de rota, sair da página ou fechar a aba, envia um evento interno `page_duration` com `duration_ms`. Esse nome é reservado; não deve ser enviado por `track()`. A amostra da última página só aparece depois que o navegador envia esse evento, então uma página ainda aberta pode não ter duração contabilizada.

As categorias técnicas e contagens de sessões não são uma contagem de aparelhos físicos únicos. O SDK não guarda um identificador persistente para reconhecer o mesmo aparelho em sessões diferentes. Região não vem do navegador: pode ser derivada pela API de cabeçalhos de um proxy confiável configurado no servidor ou vir do agregado da Vercel.

O coletor valida o payload novamente. `Origin` ajuda a limitar as origens aceitas, mas é público e pode ser falsificado fora do navegador; produção deve aplicar rate limiting compartilhado no gateway além do limite local em memória.

## Testar

Dentro de `packages/tracker-sdk`, execute `npm test`. Os testes verificam pageviews, eventos, navegação SPA, remoção de query/fragment e respeito a Do Not Track.
