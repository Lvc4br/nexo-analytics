# Arquitetura do sistema

## 1. Estilo arquitetural

Começar com um **monólito modular** no backend e um monorepositório. A separação por módulos permite evoluir serviços de forma independente sem introduzir prematuramente a complexidade operacional de microsserviços.

## 2. Componentes

### Dashboard — `apps/dashboard`
React, TypeScript e Vite. Responsável por autenticação visual, gestão de sites, filtros, gráficos e relatórios. O frontend nunca é a autoridade final de autorização.

### API — `services/api`
Python e FastAPI. Responsável por validar entradas, autenticar administradores, aplicar autorização por projeto, receber eventos, aplicar regras de privacidade e disponibilizar relatórios.

### Tracker SDK — `packages/tracker-sdk`
Biblioteca JavaScript pequena, instalada nos sites monitorados. Envia apenas eventos permitidos e não contém segredos administrativos.

### PostgreSQL
Armazena usuários, sites, domínios, chaves, eventos, sessões e agregações. Migrações versionadas devem ser usadas para alterar o esquema.

### Infraestrutura — `infra`
Scripts, Docker e configurações de desenvolvimento e implantação.

## 3. Fluxo de coleta

1. O administrador cria um site.
2. O backend gera um identificador público e configura os domínios permitidos.
3. O SDK é instalado no site.
4. O SDK cria um evento permitido e o envia por HTTPS.
5. A API valida formato, tamanho, origem quando disponível, projeto, domínio e rate limit.
6. O serviço de coleta minimiza e normaliza o payload.
7. O evento é persistido com referência ao projeto.
8. Consultas autenticadas calculam métricas apenas para projetos autorizados.

O cabeçalho HTTP `Origin` e o identificador público ajudam a filtrar requisições, mas não são segredos e não substituem rate limiting, validação e controles contra abuso.

## 4. Fluxo de relatórios

1. O dashboard solicita um relatório para um `site_id` e período.
2. A API valida a sessão do usuário.
3. O serviço de autorização confirma acesso ao projeto.
4. O serviço de analytics executa consultas parametrizadas e limitadas.
5. A API devolve dados agregados em um esquema estável.
6. O dashboard renderiza os resultados.

## 5. Hierarquia planejada

```text
nexo-analytics/
├── apps/
│   └── dashboard/
│       └── src/
│           ├── app/
│           ├── assets/
│           ├── components/
│           ├── features/
│           │   ├── overview/
│           │   ├── sites/
│           │   ├── analytics/
│           │   ├── events/
│           │   ├── opportunities/
│           │   └── settings/
│           ├── hooks/
│           ├── lib/
│           ├── styles/
│           └── types/
├── services/
│   └── api/
│       ├── app/
│       │   ├── api/v1/endpoints/
│       │   ├── analytics/
│       │   ├── core/
│       │   ├── db/
│       │   ├── integrations/
│       │   ├── models/
│       │   ├── privacy/
│       │   ├── repositories/
│       │   ├── schemas/
│       │   └── services/
│       ├── migrations/
│       └── tests/
├── packages/
│   └── tracker-sdk/
│       ├── src/
│       └── tests/
├── infra/
├── docs/
└── .github/
```

Essa árvore é uma estrutura-alvo. Não é necessário criar todos os diretórios antes de ter código que os utilize.

## 6. Responsabilidades internas da API

- `api/v1/endpoints/`: adaptadores HTTP.
- `schemas/`: validação e serialização.
- `services/`: regras de negócio.
- `repositories/`: persistência e consultas.
- `models/`: entidades do banco.
- `analytics/`: métricas e agregações.
- `privacy/`: retenção, anonimização e exclusão.
- `core/`: configuração, autenticação e segurança.
- `integrations/`: adaptadores de serviços externos.
- `db/`: sessão, engine e dependências do banco.

Endpoints devem permanecer finos; regras de negócio não devem ser duplicadas entre rotas.

## 7. Escalabilidade

Começar com consultas indexadas e agregações SQL. Só adicionar fila, worker assíncrono, cache ou particionamento quando volume medido justificar. Registrar métricas de latência, falhas de ingestão e tamanho das tabelas antes de otimizar.

## 8. Integrações com terceiros

A integração com serviços externos deve usar APIs oficiais, respeitar planos e permissões e documentar limites. Métricas agregadas de uma plataforma não devem ser apresentadas como dados individuais próprios, nem associadas a visitantes sem uma forma legítima e tecnicamente suportada de associação.

## 9. Decisões pendentes

- Versões exatas de Node.js e Python.
- ORM e biblioteca de migrações.
- Estratégia final de sessão/autenticação.
- Provedor de hospedagem.
- Política de retenção e limiares de agregação.
- Necessidade de filas com base no volume real.