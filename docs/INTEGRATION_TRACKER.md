# Instalar o tracker Nexo no LV_Portfolio

O tracker envia eventos do navegador para a API Nexo. Ele é JavaScript independente de Vercel, React e do provedor de hospedagem. A Vercel continua sendo uma fonte agregada opcional; o tracker cobre interações e mantém a coleta própria se o portfólio mudar de hospedagem.

## 1. Configure a API Nexo

No `.env` do Nexo:

```dotenv
PORTFOLIO_SITE_ID=lvc4br-lv-portfolio
PORTFOLIO_ALLOWED_ORIGINS=http://localhost:4173,https://luca-toniolo.vercel.app
TRACKER_RATE_LIMIT_PER_MINUTE=120
TRACKER_EVENT_RETENTION_DAYS=365
GEOLOCATION_PROXY=none
```

`PORTFOLIO_ALLOWED_ORIGINS` recebe origens completas, separadas por vírgula, sem caminhos. Adicione todos os domínios de produção e preview que devem enviar dados. Reinicie a API após editar `.env`.

O coletor é `POST /api/v1/collect`. Para desenvolvimento local, a base SQLite é criada automaticamente. Em produção, configure a API com uma URL pública HTTPS e PostgreSQL persistente. Não use SQLite no disco de funções serverless.

`GEOLOCATION_PROXY=none` é o padrão e é adequado para desenvolvimento local. Se a própria API Nexo for hospedada atrás da Vercel, configure `GEOLOCATION_PROXY=vercel` para ler os cabeçalhos de país/região adicionados pela Vercel. Se estiver atrás do Cloudflare, use `cloudflare` para país. Só habilite o provedor que realmente está na frente da API. Isso não exige nem envia IP ao tracker. Se a API estiver local, a região dos visitantes não é inferível pela coleta própria; os dados de país da Vercel só aparecem se a integração Web Analytics também estiver configurada.

## 2. Copie o tracker ao repositório do portfólio

Como `LV_Portfolio` é outro repositório, copie o arquivo [packages/tracker-sdk/src/index.js](../packages/tracker-sdk/src/index.js) para `src/lib/nexo-tracker.js` dentro dele. O arquivo não requer dependências externas e pode ser usado pelo projeto React JSX atual.

Crie `src/lib/analytics.js`:

```js
import { createNexoTracker } from "./nexo-tracker.js";

const tracker = createNexoTracker({
  endpoint: import.meta.env.VITE_NEXO_COLLECT_URL,
  siteId: import.meta.env.VITE_NEXO_SITE_ID,
  trackDevelopment: import.meta.env.DEV,
});

export default tracker;
```

Importe `./lib/analytics.js` uma vez no ponto de entrada do portfólio, como `src/main.jsx`. Isso ativa o pageview inicial e observa `pushState`, `replaceState` e `popstate` para acompanhar as rotas de uma SPA. Se o aplicativo não usa React Router nem navegação SPA, o carregamento inicial ainda é registrado.

Para interações relevantes, use `tracker.track()` no handler já existente:

```jsx
import tracker from "../lib/analytics.js";

function ResumeLink() {
  return (
    <a href="/resume.pdf" onClick={() => tracker.track("resume_open")}>
      Abrir currículo
    </a>
  );
}
```

Use nomes curtos, como `resume_open`, `contact_click` e `project_open`. O método não recebe nem envia propriedades arbitrárias; não coloque nome, e-mail, telefone, empresa ou texto digitado no nome do evento.

## 3. Variáveis no projeto LV_Portfolio

Adicione ao `.env.local` para desenvolvimento e às Environment Variables do projeto de produção na Vercel:

```dotenv
VITE_NEXO_COLLECT_URL=https://SUA-API-NEXO/api/v1/collect
VITE_NEXO_SITE_ID=lvc4br-lv-portfolio
```

Esses dois valores aparecem no bundle do navegador e são identificadores públicos. Não coloque `VERCEL_ACCESS_TOKEN`, senha de administrador ou `SESSION_SECRET` no repositório do portfólio.

Ao alterar as variáveis na Vercel, faça um novo deploy do portfólio. Aponte `VITE_NEXO_COLLECT_URL` para a API Nexo, não para a URL do dashboard.

## 4. Desenvolvimento local ponta a ponta

1. Rode o backend Nexo em `http://127.0.0.1:8000`.
2. Inicie o portfólio em uma origem permitida, por exemplo `npm run dev -- --port 4173`.
3. Mantenha o dashboard Nexo em `http://localhost:5173`.
4. Deixe `trackDevelopment: import.meta.env.DEV` ativo. O tracker bloqueia coleta em localhost por padrão se essa opção estiver desativada.
5. Navegue pelo portfólio e clique nos links instrumentados; entre no dashboard e escolha o período que inclui hoje.

O identificador público precisa coincidir com `PORTFOLIO_SITE_ID`; a origem enviada pelo navegador precisa estar em `PORTFOLIO_ALLOWED_ORIGINS`. Um `403` da rota de coleta indica uma origem não permitida e um `404` indica site ID divergente.

## 5. Mudar a hospedagem depois

Mantenha as mesmas variáveis `VITE_NEXO_COLLECT_URL` e `VITE_NEXO_SITE_ID` após mover o site para outro provedor. Adicione a origem nova a `PORTFOLIO_ALLOWED_ORIGINS` e atualize `PORTFOLIO_DOMAIN` com o novo domínio, sem `https://`. O tracker continuará enviando ao Nexo; a integração de leitura da Vercel pode ser desligada. Dados históricos agregados da Vercel não são importados automaticamente para o banco Nexo.

## O que é contado

- `page_view`: caminho acessado; query string e fragmento da URL são removidos pelo navegador antes do envio.
- `page_duration`: amostra interna do tempo em que a página permaneceu visível; o relógio pausa quando a aba fica oculta e o evento é enviado ao trocar de rota ou sair/fechar a página. Uma página que ainda está aberta pode não ter amostra.
- Eventos personalizados: contagem e sessões distintas associadas a cada nome de evento.
- Dispositivo/navegador/sistema: famílias técnicas estimadas do user-agent; o user-agent completo não é enviado. As contagens Nexo são sessões por categoria, não dispositivos físicos únicos.
- Sessão: ID aleatório em `sessionStorage`, que persiste durante a sessão da aba e não identifica uma pessoa nem deduplica o mesmo aparelho em sessões diferentes.
- Engajamento: sessões Nexo com pelo menos um evento personalizado dividido pelas sessões Nexo do período.
- Taxa de uma página: porcentagem de sessões Nexo com exatamente um pageview; não é métrica identificada de uma pessoa.
- Região: país/região aproximados, obtidos de agregados Vercel ou dos cabeçalhos de um proxy confiável configurado no backend; API local não determina a localização.

O endpoint rejeita origens fora da lista, site IDs divergentes, caminhos com query/fragmento, nomes inválidos e formatos malformados. Requisições repetidas com o mesmo ID de evento são idempotentes. O coletor não persiste IP nem cabeçalho de referência. O limite em memória ajuda em uma instância; ambientes de produção distribuídos também devem configurar limitação de taxa compartilhada no gateway.
