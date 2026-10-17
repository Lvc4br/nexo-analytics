# Nexo Analytics

**Plataforma independente de analytics para administrar e analisar múltiplos sites em um único painel.**

O Nexo Analytics é um projeto em desenvolvimento que pretende reunir métricas próprias de vários sites, com painel administrativo, API, banco de dados e um SDK JavaScript de coleta. A proposta é oferecer uma experiência centralizada de gestão, inspirada na simplicidade de plataformas modernas de deploy, sem tentar reproduzir toda a infraestrutura de hospedagem da Vercel.

> **Status:** planejamento e fundação. Endpoints, funcionalidades e estruturas descritas neste repositório são propostas até serem implementadas e testadas.

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

## Stack planejada

| Camada | Tecnologia | Responsabilidade |
|---|---|---|
| Dashboard | React, TypeScript, Vite | Interface administrativa |
| API | Python, FastAPI | Autenticação, validação e regras de negócio |
| Banco | PostgreSQL | Projetos, eventos, sessões e métricas |
| SDK | TypeScript/JavaScript | Envio de eventos autorizados pelos sites |
| Gráficos | Recharts (planejado) | Visualização de métricas |
| Ambiente local | Docker Compose (planejado) | Execução coordenada dos serviços |
| Qualidade | Pytest, testes frontend e GitHub Actions (planejados) | Testes e automação |

As dependências e versões serão fixadas nos manifests quando a implementação começar.

## Arquitetura

1. O administrador cadastra um site no dashboard.
2. A API registra o projeto e sua configuração.
3. O SDK instalado no site envia eventos ao endpoint público de coleta.
4. A API valida o identificador do projeto, domínio, payload e limites de requisição.
5. Os dados minimizados são persistidos no PostgreSQL.
6. Endpoints autenticados consultam somente projetos aos quais o usuário tem acesso.
7. O dashboard apresenta métricas e eventos agregados.

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

A árvore é o destino arquitetural, não a afirmação de que todos os módulos já estão implementados. Os diretórios e arquivos serão adicionados progressivamente.

## Documentação

- [Visão do produto](docs/VISION.md)
- [Arquitetura](docs/ARCHITECTURE.md)
- [Modelo de dados](docs/DATA_MODEL.md)
- [Contrato inicial da API](docs/API.md)
- [SDK de rastreamento](docs/SDK.md)
- [Segurança](docs/SECURITY.md)
- [Privacidade e LGPD](docs/PRIVACY_LGPD.md)
- [Roadmap](docs/ROADMAP.md)
- [Contribuição e fluxo Git](docs/CONTRIBUTING.md)
- [Decisões arquiteturais](docs/DECISIONS.md)

## Pré-requisitos

Para a implementação local, a expectativa é utilizar:

- Git;
- Node.js em versão LTS compatível com a versão do Vite escolhida;
- Python em versão compatível com a versão do FastAPI escolhida;
- Docker Desktop com Docker Compose, ou PostgreSQL local;
- Editor de código, como Visual Studio Code.

As versões exatas devem ser registradas quando os manifests e arquivos de configuração forem criados.

## Estado atual e execução

Este repositório está sendo documentado antes da implementação. Os comandos de execução, endpoints e exemplos de SDK descritos nos documentos são especificações propostas; não os considere implementados até que o código e os testes correspondentes sejam adicionados.

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