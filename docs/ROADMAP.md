# Roadmap

## Implementado neste repositório

- [x] Dashboard administrativo em React JSX/Vite e API Python/FastAPI.
- [x] Login de administrador configurado por ambiente.
- [x] Consulta agregada da Vercel Web Analytics.
- [x] Tracker JavaScript próprio, endpoint de coleta e persistência SQLite local/PostgreSQL para produção.
- [x] Agregação Nexo, fallback da Vercel e pageviews sem dupla contagem.
- [x] Categorias de dispositivo, navegador e sistema operacional, com contagem por sessão.
- [x] Tempo ativo de página/sessão, médias, extremos, taxa estimada de uma página e páginas populares.
- [x] País/região aproximados via agregado Vercel ou cabeçalho de proxy configurado.
- [x] Validação de origem/site, deduplicação e testes da API/SDK.
- [x] Guia para instalar o tracker em um repositório separado.

## Preparar a primeira conexão real

- [ ] Copiar o SDK para `LV_Portfolio`, instrumentar links de currículo/contato e publicar novo deploy.
- [ ] Publicar API Nexo com PostgreSQL persistente e URL HTTPS.
- [ ] Configurar URL da API, site ID e origens permitidas no portfólio e Nexo.
- [ ] Configurar credenciais Vercel no backend se Web Analytics também será usado.
- [ ] Validar tráfego de teste no dashboard com as fontes Vercel e Nexo visíveis.

## Próximas capacidades

- [ ] Rate limiting compartilhado e limpeza de retenção agendada para produção distribuída.
- [ ] Migrations versionadas antes de mudanças incompatíveis no schema.
- [ ] Gerenciar sites/domínios pelo painel e permitir múltiplos projetos.
- [ ] Exportação e exclusão de dados e controles de preferências quando necessários.
- [ ] Publicação do tracker como pacote npm para instalar sem copiar o arquivo entre repositórios.

Não adicionar precisão geográfica, filas ou identificação persistente de visitantes antes de isolamento, coleta confiável, retenção e transparência.
