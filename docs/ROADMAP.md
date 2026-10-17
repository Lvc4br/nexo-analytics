# Roadmap

O roadmap organiza entregas verificáveis. As fases podem mudar conforme testes, capacidade e riscos encontrados.

## M0 — Planejamento e repositório
- [x] Definir visão inicial e stack planejada.
- [x] Documentar arquitetura, modelo de dados, API, SDK, segurança e privacidade.
- [ ] Definir licença e política de contribuição.
- [ ] Criar manifests e ferramentas de qualidade.
- [ ] Configurar integração contínua básica.

**Concluído quando:** documentação e ambiente inicial são consistentes e reproduzíveis.

## M1 — Fundação executável
- [ ] Criar aplicação React + TypeScript + Vite.
- [ ] Criar API FastAPI com `GET /health`.
- [ ] Configurar PostgreSQL local.
- [ ] Configurar migrações.
- [ ] Adicionar testes iniciais frontend e backend.
- [ ] Documentar comandos de execução.

**Concluído quando:** dashboard, API e banco podem ser iniciados localmente e os testes passam.

## M2 — Autenticação e projetos
- [ ] Criar modelo de usuário.
- [ ] Implementar login/logout e sessão segura.
- [ ] Criar cadastro/listagem/edição de sites.
- [ ] Criar domínios permitidos.
- [ ] Implementar autorização por projeto.
- [ ] Criar testes de isolamento entre usuários.

**Concluído quando:** usuário não acessa sites de outra conta.

## M3 — Coleta
- [ ] Definir esquema de evento.
- [ ] Implementar endpoint de coleta.
- [ ] Implementar validação, rate limiting e limites de payload.
- [ ] Implementar SDK mínimo.
- [ ] Implementar eventos de visualização de página.
- [ ] Adicionar testes de payload e abuso.

**Concluído quando:** site de teste envia eventos válidos e eventos inválidos são rejeitados.

## M4 — Analytics
- [ ] Definir cálculo de sessão e inatividade.
- [ ] Implementar métricas de páginas e eventos.
- [ ] Criar filtros por período.
- [ ] Criar dashboard com gráficos.
- [ ] Comparar relatórios com dados de teste conhecidos.

**Concluído quando:** os números apresentados são reproduzíveis e explicáveis.

## M5 — Privacidade e controles
- [ ] Definir e implementar retenção.
- [ ] Criar fluxo de exportação e exclusão.
- [ ] Implementar preferências de coleta conforme o desenho legal.
- [ ] Documentar aviso de privacidade de referência.
- [ ] Revisar minimização de URLs, logs e propriedades.
- [ ] Testar expiração e exclusão.

**Concluído quando:** os prazos e preferências são aplicados pelo sistema, não apenas descritos.

## M6 — Sinais profissionais
- [ ] Definir eventos permitidos.
- [ ] Implementar abertura de currículo e cliques configurados.
- [ ] Definir pesos e explicações para indicadores.
- [ ] Evitar identificação de pessoas ou empresas sem evidência.
- [ ] Validar utilidade e risco de falsos positivos.

**Concluído quando:** cada sinal mostra a origem e as limitações da interpretação.

## M7 — Preparação para produção
- [ ] Configurar deploy de frontend e API.
- [ ] Configurar domínio, HTTPS e segredos.
- [ ] Configurar backups e testar restauração.
- [ ] Configurar logs, métricas e alertas.
- [ ] Fazer revisão de segurança e dependências.
- [ ] Documentar resposta a incidentes.
- [ ] Definir plano de atualização e rollback.

## Prioridade recomendada

Não implementar geolocalização, integrações complexas, filas ou análises sofisticadas antes de autenticação, isolamento, coleta confiável e relatórios básicos.