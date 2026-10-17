# Nexo Analytics

**Plataforma independente de analytics para administrar e analisar múltiplos sites em um único painel.**

O Nexo Analytics está começando por um painel administrativo para o portfólio Luca Toniolo. A interface React conversa com uma API Python/FastAPI, que consulta os dados agregados do Web Analytics da Vercel, calcula comparações e indicadores e devolve os resultados ao dashboard.

> **Status:** primeira versão funcional em desenvolvimento. O login de administrador e a consulta do Web Analytics foram implementados; as credenciais da Vercel e do administrador ainda precisam ser configuradas no ambiente local ou no provedor da API.

## Objetivos

- Administrar vários sites/projetos em uma única conta.
- Coletar visualizações de página e eventos permitidos.
- Estimar sessões, recorrência e tempo ativo aproximado.
- Apresentar métricas por site e uma visão consolidada.
- Acompanhar eventos profissionais explícitos, como abertura do currículo e cliques em links de contato.
- Aplicar isolamento entre projetos, minimização de dados e controles de privacidade desde o início.

## Fora do escopo inicial

- Hospedagem, builds e deploys como os oferecidos pela Vercel.
- Identificação de pessoas reais ou de empresas a partir de visitas anônimas.
- Fingerprinting invasivo.
- Localização precisa baseada em IP.
- Associação automática entre visitantes individuais e métricas agregadas de terceiros.

## Stack atual e próximos passos

| Camada | Tecnologia | Responsabilidade |
|---|---|---|
| Dashboard | React, JSX, Vite | Interface administrativa |
| API | Python, FastAPI | Autenticação, validação e regras de negócio |
| Fonte de métricas nesta versão | Vercel Web Analytics API | Visualizações, visitantes por dia, páginas e eventos personalizados |
| Banco | PostgreSQL (futuro) | Persistir projetos, dados próprios e configurações |
| SDK próprio | TypeScript/JavaScript (futuro) | Eventos que não são enviados pelo Web Analytics |
| Gráficos | SVG no dashboard | Gráfico de tráfego sem dependência adicional |
| Ambiente local | Docker Compose (planejado) | Execução coordenada dos serviços |
| Qualidade | unittest e build Vite | Testes automatizados da API e validação do bundle frontend |

As dependências da interface e da API estão nos manifests de cada serviço.

## Arquitetura

1. O administrador entra no dashboard e recebe um token de sessão curto.
2. O dashboard chama a API FastAPI com esse token.
3. A API consulta a Vercel usando um token secreto guardado apenas no backend.
4. A API agrega visualizações por dia, compara períodos e calcula páginas populares e resumos.
5. O dashboard apresenta os dados agregados e as análises.

Esta primeira versão usa os dados agregados da Vercel e não requer banco de dados. O SDK próprio, projetos múltiplos e persistência são etapas futuras.

Veja [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Estrutura planejada

```text
nexo-analytics/
├── apps/
│   └── dashboard/
├── services/
│   └── api/
├── packages/
│   └── tracker-sdk/
├── infra/
├── docs/
├── .github/
├── .env.example
├── .gitignore
├── .editorconfig
└── README.md
```

A pasta `packages/tracker-sdk` e a infraestrutura de banco ainda são etapas futuras.

## Documentação

- [Visão do produto](docs/VISION.md)
- [Arquitetura](docs/ARCHITECTURE.md)
- [Integração com Vercel e portfólio](docs/INTEGRATION_VERCEL.md)
- [Modelo de dados](docs/DATA_MODEL.md)
- [Contrato inicial da API](docs/API.md)
- [SDK de rastreamento](docs/SDK.md)
- [Segurança](docs/SECURITY.md)
- [Privacidade e LGPD](docs/PRIVACY_LGPD.md)
- [Roadmap](docs/ROADMAP.md)
- [Contribuição e fluxo Git](docs/CONTRIBUTING.md)
- [Decisões arquiteturais](docs/DECISIONS.md)

## Pré-requisitos

Para executar a aplicação localmente, utilize:

- Git;
- Node.js compatível com o Vite 8 e npm;
- Python 3.11 ou superior;
- Editor de código, como Visual Studio Code.

PostgreSQL e Docker não são necessários para esta primeira versão.

## Estado atual e execução

O dashboard em `apps/dashboard` autentica o administrador na API e mostra métricas reais do projeto Vercel configurado. A API está em `services/api`; não são exibidos números fictícios. Para páginas vistas, é usada a agregação existente do Web Analytics. Eventos personalizados aparecem somente quando o portfólio os registra com `track()`.

1. Na raiz do repositório, copie `.env.example` para `.env` (`Copy-Item .env.example .env` no PowerShell). Preencha `DASHBOARD_EMAIL`, `VERCEL_ACCESS_TOKEN` e `VERCEL_PROJECT_ID`. Se o projeto Vercel estiver em um Team, configure o `VERCEL_TEAM_ID` ou `VERCEL_TEAM_SLUG`. O token da Vercel fica somente no backend.

2. Na pasta `services/api`, crie um ambiente virtual, instale as dependências e gere o hash da senha do administrador:

```powershell
cd services/api
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m app.hash_password
```

Copie o hash impresso para `DASHBOARD_PASSWORD_HASH` no arquivo `.env`. Não salve a senha em texto puro.

3. Em um terminal com o ambiente Python ativado, inicie a API:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

4. Em outro terminal, inicie o dashboard:

```sh
cd apps/dashboard
npm install
npm run dev
```

O dashboard fica em `http://localhost:5173`; a documentação interativa da API fica em `http://127.0.0.1:8000/docs`. O build frontend pode ser gerado com `npm run build` dentro de `apps/dashboard`.

### Testes e verificações

Com o ambiente virtual ativado e estando em `services/api`, execute os testes da API:

```powershell
py -m unittest discover -s tests -v
```

Os testes cobrem a autenticação, a proteção das rotas e a análise de uma resposta simulada da Vercel. Eles não usam credenciais nem fazem chamadas externas. Para conferir o build do dashboard, estando em `apps/dashboard`, execute:

```powershell
npm run build
```

### Como alterar o projeto

- **Tela de login:** edite `apps/dashboard/src/pages/LoginPage.jsx`.
- **Dashboard e apresentação das métricas:** edite `apps/dashboard/src/pages/DashboardPage.jsx`.
- **Estilos e comportamento responsivo:** edite `apps/dashboard/src/styles.css`.
- **Chamadas do React à API:** edite `apps/dashboard/src/lib/api.js`.
- **Rotas de login e regras de sessão:** edite `services/api/app/routers/auth.py` e `services/api/app/security.py`.
- **Consulta à Vercel, cálculos e insights:** edite `services/api/app/routers/analytics.py` e `services/api/app/integrations/vercel.py`.
- **Configurações e nomes das variáveis de ambiente:** atualize `services/api/app/config.py` e documente valores de exemplo em `.env.example`. Segredos reais ficam somente no `.env` local ou nas variáveis privadas do provedor.

Durante o desenvolvimento, mantenha a API e o dashboard rodando em terminais separados. Depois de alterar a API, rode `py -m unittest discover -s tests -v`; depois de alterar o frontend, rode `npm run build`. O guia [docs/INTEGRATION_VERCEL.md](docs/INTEGRATION_VERCEL.md) explica a conexão ao portfólio e a publicação dos dois serviços.

### Publicação

O dashboard e a API podem ser publicados como projetos separados na Vercel. Use `apps/dashboard` como Root Directory do frontend e `services/api` como Root Directory da API Python/FastAPI. Configure `VITE_API_BASE_URL` no build do dashboard e `APP_ENV=production`, `CORS_ALLOWED_ORIGINS`, `SESSION_SECRET`, `DASHBOARD_EMAIL`, `DASHBOARD_PASSWORD_HASH` e as credenciais do projeto Vercel no host da API. Não coloque o token da Vercel em variáveis `VITE_*`. Veja o [guia de integração](docs/INTEGRATION_VERCEL.md).

### Limites desta versão

- Os visitantes são contados por dia e somados ao longo do período; não representam pessoas únicas em todo o intervalo.
- O Web Analytics fornece valores agregados. O dashboard não vê identidades nem eventos individuais.
- Páginas vistas são automáticas quando o Web Analytics do projeto Vercel está habilitado. Cliques em currículo ou contato precisam ser instrumentados como eventos personalizados no portfólio, e a disponibilidade depende do plano Vercel.
- A sessão do dashboard dura 30 minutos e fica na memória do navegador; atualizar a página pede novo login.

## Princípios do projeto

1. Segurança e isolamento por projeto.
2. Privacidade e minimização por padrão.
3. Métricas transparentes, com limitações explicitadas.
4. Arquitetura modular sem microsserviços prematuros.
5. Código testável, documentação atualizada e mudanças pequenas.
6. Nenhum segredo ou dado real de visitante em commits.

## Licença

A licença ainda precisa ser definida. Até que exista um arquivo de licença, não presuma que o código pode ser reutilizado, redistribuído ou comercializado livremente.

## Aviso

Este projeto não é afiliado à Vercel. A documentação sobre privacidade é orientação técnica inicial, não aconselhamento jurídico. Antes de coletar dados reais, revisar segurança, base legal, aviso de privacidade, retenção e controles de titulares.
