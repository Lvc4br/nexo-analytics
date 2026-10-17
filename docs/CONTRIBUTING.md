# Contribuição e fluxo de desenvolvimento

## Antes de começar

Leia:
1. [README](../README.md)
2. [Arquitetura](ARCHITECTURE.md)
3. [Roadmap](ROADMAP.md)
4. [Segurança](SECURITY.md)
5. [Privacidade e LGPD](PRIVACY_LGPD.md)

## Branches

Usar branches curtas para cada tarefa:
- `feat/nome-da-funcionalidade`
- `fix/nome-do-problema`
- `docs/assunto`
- `test/escopo`
- `chore/ferramenta`

Manter `main` estável e integrar mudanças pequenas, preferencialmente via Pull Request.

## Commits

Preferir mensagens claras no estilo Conventional Commits:
- `feat: add site registration`
- `fix: validate event payload size`
- `docs: explain local setup`
- `test: cover project isolation`
- `chore: configure linting`

## Definition of Done

Uma tarefa está pronta quando:
- atende aos critérios de aceitação da Issue;
- inclui testes apropriados;
- não quebra a execução documentada;
- atualiza a documentação pertinente;
- não inclui segredos ou dados reais de visitantes;
- respeita autorização, minimização e isolamento;
- passa pelas verificações automatizadas.

## Issues

Cada Issue deve conter:
- contexto e problema;
- resultado esperado;
- critérios de aceitação;
- possíveis impactos de segurança e privacidade;
- testes necessários.

Evitar Issues vagas como “fazer todo o sistema”.

## Qualidade

- Preferir funções pequenas e responsabilidades claras.
- Não duplicar regras de negócio em endpoints.
- Usar schemas para entrada e saída.
- Usar migrações para mudanças no banco.
- Não registrar payloads sensíveis.
- Fixar versões e atualizar dependências de forma revisada.
- Criar testes para permissões e acesso cruzado.

## Segredos

Nunca enviar arquivos `.env` reais, senhas, tokens, chaves privadas, dumps de banco com dados pessoais ou credenciais de produção. Se um segredo for publicado acidentalmente, revogá-lo/rotacioná-lo imediatamente; apagar o commit não garante que deixou de estar exposto.