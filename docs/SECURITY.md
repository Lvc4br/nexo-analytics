# Baseline de segurança

Este documento define controles a implementar e verificar antes de coletar dados reais.

## Modelo de ameaça

Considerar:
- tentativas de acesso não autorizado ao dashboard;
- leitura cruzada de dados entre sites;
- abuso do endpoint público de coleta;
- payloads malformados ou excessivos;
- exposição acidental de segredos;
- injeção em consultas, logs ou interface;
- falsificação de eventos e tráfego automatizado;
- dependências vulneráveis;
- backups ou exportações expostos.

## Controles obrigatórios

### Autenticação
- Armazenar apenas hashes de senha com algoritmo adequado e parâmetros atuais.
- Aplicar limitação de tentativas e respostas que não revelem se uma conta existe.
- Usar sessões com expiração, revogação e cookies protegidos.
- Exigir reautenticação para ações administrativas sensíveis quando apropriado.

### Autorização e isolamento
- Verificar permissão no backend em cada operação protegida.
- Escopar toda consulta por site e usuário/membro autorizado.
- Considerar Row-Level Security do PostgreSQL como camada adicional.
- Testar sistematicamente acesso cruzado entre contas e projetos.

### Chaves e segredos
- Nunca versionar arquivos `.env` reais, senhas, tokens ou chaves privadas.
- Manter `.env.example` apenas com nomes e valores de exemplo não funcionais.
- Separar chave pública do SDK e segredos administrativos.
- Permitir revogação e rotação de chaves.
- Evitar segredos em logs, mensagens de erro e URLs.

### Coletor público
- HTTPS.
- Validação de schema, tamanho, frequência e timestamp.
- Rate limiting por sinais disponíveis, projeto e infraestrutura.
- Lista de eventos e propriedades permitidas.
- Proteção contra abuso e monitoramento de taxas anormais.
- Não confiar apenas em CORS ou no cabeçalho Origin.
- Tratar eventos do cliente como dados não confiáveis.

### Banco e API
- Consultas parametrizadas/ORM seguro.
- Privilégios mínimos para o usuário do banco.
- Backups protegidos e teste periódico de restauração.
- Migrações revisadas e versionadas.
- Timeouts e limites de consulta.
- Logs sem payloads sensíveis.

### Frontend
- Escapar conteúdo dinâmico e evitar HTML não confiável.
- Não armazenar credenciais administrativas em localStorage sem análise de risco.
- Aplicar proteção CSRF se a estratégia de autenticação exigir.
- Configurar políticas de segurança de conteúdo e cabeçalhos HTTP conforme o deploy.

## Auditoria e resposta a incidentes

Registrar ações administrativas relevantes sem armazenar segredos. Definir procedimento para investigar abuso, revogar credenciais, conter incidentes, restaurar serviços e avaliar obrigações de comunicação aplicáveis.

## Checklist de lançamento

- [ ] Testes de autenticação e autorização.
- [ ] Testes de isolamento entre sites.
- [ ] Rate limiting no coletor.
- [ ] Segredos fora do Git.
- [ ] Dependências verificadas.
- [ ] Backups e restauração testados.
- [ ] Política de retenção implementada.
- [ ] Logs minimizados e protegidos.
- [ ] HTTPS e cabeçalhos de segurança configurados.
- [ ] Processo de incidentes documentado.