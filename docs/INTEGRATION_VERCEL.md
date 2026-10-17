# Integração do portfólio com a Vercel

Esta versão usa os dados agregados do Web Analytics do projeto Vercel que hospeda o portfólio. O dashboard não consulta o navegador do visitante: o backend Python conversa com a API da Vercel e entrega ao frontend apenas os totais e agregações.

## 1. Habilitar Web Analytics

No projeto do portfólio na Vercel, abra **Analytics** e habilite **Web Analytics**. Confirme que o site está implantado e que o script/componente `@vercel/analytics` está carregado em produção. A integração automática de páginas precisa ter dados recebidos pela Vercel.

O Nexo consulta os recursos `visits` e `events` da API oficial. São dados de produção agregados por período, rota e nome do evento.

## 2. Obter as credenciais

1. Gere um Access Token na conta Vercel com permissão para consultar o projeto.
2. Copie o **Project ID** em **Settings → General** do projeto do portfólio.
3. Para um projeto de Team, copie também o Team ID ou o slug do Team. Projetos pessoais não precisam dessas variáveis.
4. No `.env` local, preencha `VERCEL_ACCESS_TOKEN`, `VERCEL_PROJECT_ID` e as variáveis de Team aplicáveis.

Não adicione o token a `VITE_*`, ao código React, ao repositório Git ou ao projeto do portfólio. Ele é usado exclusivamente por `services/api`.

## 3. Criar o acesso de administrador

Preencha `DASHBOARD_EMAIL` no `.env`. Dentro de `services/api`, ative o ambiente virtual e execute:

```powershell
py -m app.hash_password
```

Cole o hash produzido em `DASHBOARD_PASSWORD_HASH`. Defina `SESSION_SECRET` com um valor aleatório longo. A sessão expira em 30 minutos e o token não é salvo em `localStorage`.

## 4. Executar localmente

Em um terminal, na pasta `services/api` e com o ambiente virtual ativado:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Em outro terminal:

```powershell
cd apps/dashboard
npm run dev
```

Abra `http://localhost:5173` e entre com o e-mail e a senha configurados. A API aparece em `http://127.0.0.1:8000/docs`.

## 5. Publicar

É possível publicar a interface e a API como dois projetos na Vercel:

- Projeto do dashboard: Root Directory `apps/dashboard`; defina `VITE_API_BASE_URL` com a URL pública da API, incluindo `/api/v1`.
- Projeto da API: Root Directory `services/api`; configure as variáveis Python do `.env` nas Environment Variables da Vercel. Defina `APP_ENV=production`, `CORS_ALLOWED_ORIGINS` com a origem pública do dashboard e use um `SESSION_SECRET` aleatório com pelo menos 32 caracteres.

Após configurar variáveis, faça um novo deploy para que os builds passem a usá-las. A entrada `services/api/index.py` exporta a aplicação ASGI `app` para o runtime Python da Vercel. Consulte também a documentação atual de [FastAPI na Vercel](https://vercel.com/docs/frameworks/backend/fastapi).

## 6. Eventos de interação opcionais

Visitas a páginas são coletadas automaticamente pelo Web Analytics. Eventos como abrir o currículo ou clicar em contato são separados e precisam ser enviados pelo código do portfólio. Com o pacote `@vercel/analytics` instalado, o handler do botão pode chamar:

```tsx
import { track } from "@vercel/analytics";

track("resume_open");
track("contact_click", { channel: "email" });
```

O painel mostra apenas o nome do evento, a quantidade e a contagem agregada de visitantes. Evite enviar e-mail, telefone ou outras informações pessoais como propriedades do evento. A disponibilidade de eventos personalizados depende do plano da Vercel.

## Métricas e limites

- Visualizações de página: agregadas por dia e por rota.
- Visitantes: somados a partir das contagens diárias da Vercel. A definição de visitante tem validade diária; a soma não significa pessoas únicas em todo o período.
- Comparação: período escolhido contra os dias imediatamente anteriores.
- Eventos: somente interações que o portfólio enviar com `track()`.
- A API não recebe eventos brutos, identificadores de pessoas nem métricas de tempo ativo.

Referências: [Vercel Web Analytics API](https://vercel.com/docs/analytics/web-analytics-api), [contagem de visualizações](https://vercel.com/docs/rest-api/web-analytics/counts-page-views), [agregações de visualizações](https://vercel.com/docs/rest-api/web-analytics/aggregates-page-views), [eventos personalizados](https://vercel.com/docs/analytics/custom-events) e [FastAPI na Vercel](https://vercel.com/docs/frameworks/backend/fastapi).
