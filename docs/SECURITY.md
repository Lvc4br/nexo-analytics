# Segurança

## Controles presentes

- Login de administrador protegido por bearer token assinado e de curta duração; o dashboard mantém o token apenas em memória.
- Senha verificada com hash Argon2; não há senha administrativa no frontend.
- Token Vercel usado somente pelo backend e nunca como variável VITE.
- Coletor valida schema, site, origem configurada, nome do evento e caminho; os tamanhos dos campos são limitados.
- IDs de evento deduplicados por chave primária; consultas usam SQLAlchemy.
- Origin e ID do site são controles complementares, não segredos nem autenticação forte.
- Produção exige SESSION_SECRET forte e PostgreSQL persistente.

## Cobertura automatizada relevante

A suíte de API cobre autenticação ausente/inválida, origem e site não autorizados, deduplicação, limite de coleta, validação do payload e separação entre métricas Nexo/Vercel. Esses testes não substituem teste de penetração, rate limiting distribuído nem validação da infraestrutura publicada.

## Antes de produção

- Configure rate limiting compartilhado no proxy/gateway. O limite atual é local ao processo e não protege sozinho um deployment serverless distribuído.
- Habilite HTTPS e configure CORS somente para as origens reais do dashboard e do portfólio.
- Defina backups/restauração e uma rotina agendada para retenção; a limpeza atual roda no startup da API.
- Restrinja a rede e os privilégios da conta PostgreSQL; exija TLS conforme o provedor.
- Configure limite de tentativas de login no gateway e monitore erros e volume anormal do coletor.
- Guarde segredos em Environment Variables privadas. Revogue ou rotacione tokens Vercel se houver exposição.
- Revise logs do host, política de conteúdo do dashboard e dependências antes do lançamento.
- Adicione migrations versionadas antes de alterações incompatíveis no banco.

## Limites conhecidos

O endpoint público aceita eventos anônimos do navegador e pode receber tráfego falso; pageviews e interações do cliente são estimativas, não evidência de identidade. Logout apaga o token no navegador, mas não revoga imediatamente tokens já emitidos; eles expiram no prazo assinado. Esta versão usa um administrador fixado por configuração e ainda não oferece contas ou membros por site.
