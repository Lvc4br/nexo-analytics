# Registro de decisões arquiteturais

Este documento registra decisões iniciais e pontos ainda pendentes. Decisões importantes podem ser movidas para arquivos ADR individuais conforme o projeto crescer.

## DEC-001 — Monólito modular no início
**Estado:** aceito provisoriamente.

**Decisão:** manter uma única API FastAPI dividida em módulos.

**Motivo:** reduz complexidade de deploy, observabilidade e desenvolvimento enquanto o produto e o volume ainda são pequenos.

**Revisar quando:** métricas demonstrarem necessidade real de separar ingestão, relatórios ou workers.

## DEC-002 — Monorepositório
**Estado:** aceito.

**Decisão:** manter dashboard, API, SDK e documentação no mesmo repositório.

**Motivo:** facilita mudanças coordenadas, onboarding e revisão do contrato entre SDK e API.

**Revisar quando:** ciclos de publicação ou permissões exigirem repositórios separados.

## DEC-003 — PostgreSQL como banco principal
**Estado:** aceito provisoriamente.

**Decisão:** usar PostgreSQL para dados transacionais e eventos iniciais.

**Motivo:** suporte a relações, índices, transações, agregações e controles de acesso por linha.

**Revisar quando:** volume e padrão de consulta justificarem particionamento ou armazenamento especializado.

## DEC-004 — Identificador público separado de credenciais privadas
**Estado:** aceito.

**Decisão:** o SDK usa apenas identificadores/chaves públicas com permissões limitadas; nunca recebe segredo administrativo.

**Motivo:** código executado no navegador é visível e pode ser copiado.

## DEC-005 — Privacidade por padrão
**Estado:** aceito.

**Decisão:** minimizar URLs e propriedades, evitar persistência de IP bruto e definir retenção antes de produção.

**Motivo:** reduzir riscos, exposição e coleta desnecessária.

## DEC-006 — Sinais profissionais explicáveis
**Estado:** aceito.

**Decisão:** apresentar eventos observados e indicadores com limitações, sem declarar identidade ou intenção não comprovada.

**Motivo:** evita interpretações enganosas de dados de navegação.

## Decisões pendentes

- Estratégia exata de autenticação e gestão de sessão.
- ORM e biblioteca de migrações.
- Versões suportadas de Node.js e Python.
- Estratégia de consentimento e identificadores persistentes.
- Provedor de hospedagem e gestão de segredos.
- Retenção por categoria de dado.
- Quando adicionar filas e agregações assíncronas.