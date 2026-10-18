# Nexo Analytics

Painel privado para combinar dados agregados do Web Analytics da Vercel com eventos coletados diretamente do portfólio. O dashboard é React com JSX e Vite; a API é Python/FastAPI.

## Como as fontes se combinam

- **Pageviews principais:** Vercel quando a consulta ao Web Analytics funciona; eventos `page_view` do tracker Nexo quando a Vercel não está configurada ou indisponível.
- **Sessões e interações próprias:** coletadas pelo Nexo, independentemente de onde o portfólio está hospedado.
- **Eventos personalizados da Vercel:** apresentados separados dos eventos Nexo.
- **Sem duplicidade:** pageviews da Vercel e do tracker nunca são somados. A resposta da API indica qual fonte está sendo usada.
- **Troca de hospedagem:** depois que o tracker estiver instalado e apontando para a API Nexo, mudar a hospedagem do portfólio não muda o endpoint de coleta.

Além das métricas agregadas da Vercel, o Nexo mede duração ativa das páginas, duração de sessão, taxa estimada de saída após uma única página, páginas populares e interações instrumentadas. O tracker classifica a família do dispositivo, navegador e sistema operacional; não envia o user-agent completo nem cria uma identificação persistente de aparelho.

Os números de dispositivos do Nexo são sessões por categoria técnica. O mesmo aparelho pode aparecer em sessões diferentes, e aparelhos diferentes podem compartilhar a mesma combinação; o Nexo não afirma contar aparelhos físicos únicos. Região é aproximada: pode vir do agregado de país da Vercel ou de cabeçalhos de país/região de um proxy confiável configurado na API. A API local não determina a região do visitante. O tracker respeita `Do Not Track` e não envia IP, referenciador, formulário, query string ou dados de usuário.

O tempo é contado enquanto a página está visível e pausado quando fica em segundo plano; a amostra é enviada ao trocar de rota ou quando a página é encerrada. Uma página que continua aberta ainda não tem amostra de duração. Vercel e Nexo não compartilham identificadores; as métricas de uma fonte não podem ser atribuídas a uma sessão individual da outra.

## Estrutura

```text
apps/dashboard/             Interface administrativa React/JSX
services/api/               API Python/FastAPI, SQLite local, PostgreSQL em produção
packages/tracker-sdk/       Tracker JavaScript independente do framework e da hospedagem
docs/                       Integração, API, privacidade e arquitetura
```

## Executar localmente

Pré-requisitos: Git, Node.js/npm e Python 3.11 ou superior.

1. Na raiz, copie o exemplo de configuração:

   ```powershell
   Copy-Item .env.example .env
   ```

   Preencha `DASHBOARD_EMAIL` e as credenciais administrativas. Para ler a Vercel, configure também `VERCEL_ACCESS_TOKEN` e `VERCEL_PROJECT_ID`; elas são opcionais porque o Nexo pode funcionar apenas com o tracker próprio. `GEOLOCATION_PROXY` fica `none` por padrão. Use `vercel` ou `cloudflare` somente se a própria API Nexo estiver atrás desse proxy confiável.

2. Instale e prepare a API:

   ```powershell
   cd services/api
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   py -m pip install -r requirements.txt
   py -m app.hash_password
   ```

   Copie o hash da senha para `DASHBOARD_PASSWORD_HASH` no `.env`. Não guarde a senha em texto puro.

3. Inicie a API em um terminal:

   ```powershell
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

   No primeiro início, a API cria `services/api/.data/nexo.sqlite3` automaticamente.

4. Em outro terminal, inicie o painel:

   ```powershell
   cd apps/dashboard
   npm install
   npm run dev
   ```

   Abra `http://localhost:5173`. A documentação da API fica em `http://127.0.0.1:8000/docs`.

## Conectar o repositório LV_Portfolio

O tracker do Nexo é JavaScript simples e funciona com React, Vite ou outro site. Como o portfólio está em outro repositório, instale-o nele:

1. Copie `packages/tracker-sdk/src/index.js` para `src/lib/nexo-tracker.js` dentro do repositório `LV_Portfolio`.
2. No `.env` do Nexo, confira `PORTFOLIO_SITE_ID=lvc4br-lv-portfolio` e inclua a origem do portfólio em `PORTFOLIO_ALLOWED_ORIGINS`. Para rodar localmente, use por exemplo `http://localhost:4173`; a origem de produção padrão é `https://luca-toniolo.vercel.app`.
3. No `.env` do portfólio, adicione a URL pública da API Nexo e o ID público do site:

   ```dotenv
   VITE_NEXO_COLLECT_URL=https://SUA-API-NEXO/api/v1/collect
   VITE_NEXO_SITE_ID=lvc4br-lv-portfolio
   ```

   A URL da API e o ID do site são públicos. **Não** adicione tokens ou senha do Nexo ao frontend.

4. Crie `src/lib/analytics.js` no portfólio:

   ```js
   import { createNexoTracker } from "./nexo-tracker.js";

   const tracker = createNexoTracker({
     endpoint: import.meta.env.VITE_NEXO_COLLECT_URL,
     siteId: import.meta.env.VITE_NEXO_SITE_ID,
     trackDevelopment: import.meta.env.DEV,
   });

   export default tracker;
   ```

   Importe esse módulo uma vez no ponto de entrada React, por exemplo `src/main.jsx`. O tracker registra pageviews iniciais e mudanças de rota SPA. Em callbacks de botões, importe `tracker` e chame `tracker.track("resume_open")`, `tracker.track("contact_click")` ou outro nome curto sem dados pessoais.

5. Para teste local, rode a API e o portfólio em origens separadas. Por exemplo, inicie o Vite do portfólio com `npm run dev -- --port 4173`; o painel Nexo continua em `5173`. Depois, publique o portfólio novamente na Vercel para começar a enviar eventos de produção.

O Nexo ainda precisa estar publicado em uma URL acessível pelo portfólio para a coleta de produção. O guia completo está em [docs/INTEGRATION_TRACKER.md](docs/INTEGRATION_TRACKER.md).

## Usar o painel e administrar a conta

Com a API e o dashboard em execução, abra `http://localhost:5173` e entre com o e-mail definido em `DASHBOARD_EMAIL` e a senha usada para gerar `DASHBOARD_PASSWORD_HASH`. O dashboard permite escolher um período de 7, 30 ou 90 dias, consultar as métricas e sair da sessão pelo botão **Sair da conta**.

Esta versão tem um único administrador configurado por variáveis de ambiente. Não existe tela para criar usuários, alterar senha ou recuperar uma senha esquecida. Para trocar o e-mail, edite `DASHBOARD_EMAIL` no ambiente privado da API e reinicie/republique a API.

### Trocar ou redefinir a senha no ambiente local

No PowerShell, abra a pasta da API e ative o ambiente virtual:

```powershell
cd services/api
.venv\Scripts\Activate.ps1
py -m app.hash_password
```

O comando solicita a nova senha duas vezes e imprime um hash Argon2. A senha precisa ter entre 12 e 128 caracteres. Copie somente o hash para `DASHBOARD_PASSWORD_HASH` no `.env` da raiz do repositório. Nunca coloque a senha em texto puro no `.env`, no código ou no Git.

Reinicie a API para aplicar a alteração. Depois, saia do painel e entre usando a nova senha. Tokens de sessões que já estavam abertas continuam válidos até expirarem (30 minutos por padrão). Para invalidar imediatamente as sessões existentes, altere também `SESSION_SECRET` para um novo valor aleatório de pelo menos 32 caracteres e reinicie a API; isso encerra todas as sessões administrativas atuais.

### Trocar a senha em produção

Execute `py -m app.hash_password` localmente, com as dependências da API instaladas, e copie o hash gerado para a variável privada `DASHBOARD_PASSWORD_HASH` no serviço que hospeda a API Nexo. Atualize `DASHBOARD_EMAIL` se necessário e faça um novo deploy/reinicie a API. Não cadastre essas credenciais nas variáveis do dashboard React ou do repositório do portfolio. Se redefinir a senha, informe a nova senha ao administrador por um canal seguro; o Nexo não envia e-mail de recuperação.

O arquivo `.env` contém configurações e credenciais locais e não deve ser commitado. Use [`.env.example`](.env.example) apenas como modelo, sem inserir valores secretos nele.

## Habilitar a fonte Vercel (opcional)

No projeto Vercel que hospeda `LV_Portfolio`, habilite **Web Analytics**. Gere um Access Token com permissão ao projeto, copie o Project ID e configure `VERCEL_ACCESS_TOKEN` e `VERCEL_PROJECT_ID` no ambiente da API Nexo. Para um projeto dentro de um Team, preencha também `VERCEL_TEAM_ID` ou `VERCEL_TEAM_SLUG`. Esses segredos ficam só no backend.

Ao conectar a Vercel, o painel usa seus pageviews agregados como fonte principal e mantém sessões/interações do Nexo separadas. Se a consulta Vercel falhar, o painel usa pageviews Nexo como fallback. Para mudar o domínio do portfólio, atualize `PORTFOLIO_DOMAIN` e `PORTFOLIO_ALLOWED_ORIGINS`.

## Testes e build

Na pasta `services/api`:

```powershell
py -m unittest discover -s tests -v
```

Na pasta `packages/tracker-sdk`:

```sh
npm test
```

Na pasta `apps/dashboard`:

```sh
npm run build
```

## Produção

SQLite é apenas para desenvolvimento local. A API em produção exige um PostgreSQL persistente e a variável `DATABASE_URL`, pois o disco de funções serverless não é armazenamento durável. Configure também `APP_ENV=production`, `SESSION_SECRET` aleatória com pelo menos 32 caracteres, `DASHBOARD_EMAIL`, `DASHBOARD_PASSWORD_HASH`, `CORS_ALLOWED_ORIGINS` com a origem do painel e `PORTFOLIO_ALLOWED_ORIGINS` com as origens do site. `VITE_API_BASE_URL` aponta para a API e deve incluir `/api/v1`.

A URL da API deve ser acessível tanto pelo painel quanto pelo site do portfólio. O Nexo não faz deploy da aplicação monitorada: ele recebe eventos do navegador e consulta dados agregados da Vercel quando configurado.

## Métricas e limites

- A métrica “Visitantes por dia” da Vercel é a soma dos valores diários dela; não representa pessoas únicas no intervalo inteiro.
- As sessões Nexo usam um ID temporário em `sessionStorage`, limitado à aba/sessão do navegador; não identificam uma pessoa.
- A taxa de engajamento é a porcentagem de sessões Nexo com pelo menos uma interação personalizada.
- Tempo mínimo, médio e máximo e taxa de uma página são calculados sobre amostras Nexo; não são fornecidos pelo agregado Vercel usado aqui.
- As categorias de dispositivo, navegador e sistema operacional não identificam dispositivos físicos. Região é aproximada e depende da fonte indicada no painel.
- Vercel e Nexo não compartilham identificadores; não há associação de visitas agregadas com indivíduos.
- O coletor valida origem, site, caminho e formato e aplica um limite local em memória. Em produção, configure também rate limiting compartilhado no proxy/gateway.
- Revise aviso de privacidade, base legal e retenção antes de operar com visitantes reais. Leia [docs/PRIVACY_LGPD.md](docs/PRIVACY_LGPD.md).

## Documentação

- [Arquitetura](docs/ARCHITECTURE.md)
- [Integração com Vercel](docs/INTEGRATION_VERCEL.md)
- [Integração do tracker no portfólio](docs/INTEGRATION_TRACKER.md)
- [Contrato da API](docs/API.md)
- [Tracker SDK](docs/SDK.md)
- [Modelo de dados](docs/DATA_MODEL.md)
- [Privacidade e LGPD](docs/PRIVACY_LGPD.md)
- [Segurança](docs/SECURITY.md)
- [Roadmap](docs/ROADMAP.md)

## Licença

Ainda não há licença definida. Até que ela seja publicada, não presuma que o código pode ser reutilizado, redistribuído ou comercializado livremente.
