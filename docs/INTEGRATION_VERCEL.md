# Integração com a Vercel

A Vercel é uma das fontes do Nexo, não o coletor exclusivo. O backend Python consulta os agregados oficiais da Vercel. O tracker próprio envia eventos do `LV_Portfolio` diretamente para a API Nexo, permitindo medições complementares e portabilidade para outra hospedagem. Para adicionar o tracker ao outro repositório, siga [docs/INTEGRATION_TRACKER.md](./INTEGRATION_TRACKER.md).

## Ativar Web Analytics

No projeto do portfólio na Vercel, habilite Web Analytics e confirme que os deploys de produção estão recebendo dados. A API do Nexo consulta agregados de `visits` e `events`, incluindo dimensões de caminho, país, tipo de dispositivo e navegador quando disponíveis; esses valores são fornecidos pela Vercel e não identificam visitas individuais. Tempo ativo, sessões por aba, sistemas operacionais e interações instrumentadas vêm do tracker próprio.

## Credenciais do backend

1. Gere um Access Token com permissão para consultar o projeto.
2. Copie o Project ID em **Settings → General** no projeto Vercel do portfólio.
3. Para projeto de Team, configure `VERCEL_TEAM_ID` ou `VERCEL_TEAM_SLUG`; projeto pessoal pode deixar ambos vazios.
4. Na configuração privada da API Nexo, preencha:

   ```dotenv
   VERCEL_ACCESS_TOKEN=...
   VERCEL_PROJECT_ID=prj_...
   VERCEL_PROJECT_DOMAIN=luca-toniolo.vercel.app
   ```

Nunca adicione o token a `VITE_*`, ao frontend, ao repositório, ou às variáveis do `LV_Portfolio`. Ele pertence apenas à API Nexo.

## Como o Nexo combina as fontes

- Se as consultas Vercel respondem, pageviews e visitantes diários da Vercel são a fonte principal.
- Se a Vercel não está configurada ou falha, pageviews e sessões Nexo viram fallback.
- Eventos personalizados enviados diretamente ao Nexo são analisados separadamente dos eventos agregados Vercel.
- A API nunca soma pageviews Vercel e Nexo para formar uma contagem, porque ambos podem descrever a mesma navegação.
- O Web Analytics da Vercel pode fornecer contagens agregadas de país, dispositivo e navegador. Para país/região obtidos diretamente pela API Nexo, hospede a API atrás de um proxy compatível e ajuste `GEOLOCATION_PROXY` (`vercel` ou `cloudflare`).
- Se desativar Web Analytics ou trocar o portfólio de hospedagem, a coleta própria continua enquanto o tracker mantiver a URL da API Nexo.

Os dados Vercel têm semântica própria: visitantes são somados por dia e não equivalem a pessoas únicas no intervalo todo. IDs de sessão Nexo não são associados aos agregados Vercel.

## Publicação do Nexo

Painel e API são projetos diferentes se forem hospedados na Vercel. Para o frontend, use `apps/dashboard` como Root Directory e configure `VITE_API_BASE_URL` com a URL da API mais `/api/v1`. Para a API, use `services/api` como Root Directory e configure `APP_ENV=production`, `SESSION_SECRET`, `DASHBOARD_EMAIL`, `DASHBOARD_PASSWORD_HASH`, `CORS_ALLOWED_ORIGINS`, `PORTFOLIO_ALLOWED_ORIGINS` e `DATABASE_URL`.

A API exige PostgreSQL persistente em produção, pois disco de função não é banco durável. `CORS_ALLOWED_ORIGINS` permite que o painel chame a API; `PORTFOLIO_ALLOWED_ORIGINS` permite que o site envie eventos ao coletor. Após mudar variáveis, faça um novo deploy. O entrypoint ASGI está em `services/api/index.py`.

## Referências oficiais

- [Vercel Web Analytics API](https://vercel.com/docs/analytics/web-analytics-api)
- [Project ID nas configurações](https://vercel.com/docs/project-configuration/general-settings)
- [Web Analytics Quickstart](https://vercel.com/docs/analytics/quickstart)
- [FastAPI na Vercel](https://vercel.com/docs/frameworks/backend/fastapi)
