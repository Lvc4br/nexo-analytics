# Modelo de dados

Este documento descreve um modelo lógico inicial. Os tipos, restrições e migrações finais deverão ser definidos durante a implementação.

## Entidades

### users
- `id`: identificador primário.
- `email`: e-mail normalizado, único.
- `password_hash`: hash seguro de senha; nunca armazenar senha em texto puro.
- `created_at`, `updated_at`: auditoria temporal.
- `is_active`: estado da conta.

### sites
- `id`: identificador interno.
- `owner_id`: usuário proprietário.
- `name`: nome de exibição.
- `status`: ativo, pausado ou excluído.
- `public_id`: identificador usado pelo SDK; não é segredo.
- `created_at`, `updated_at`.

### site_members
Opcional no MVP se houver apenas um proprietário por site; permite evoluir para equipes.
- `site_id`, `user_id`, `role`, `created_at`.

### site_domains
- `id`, `site_id`, `domain`, `verified_at`, `created_at`.
- Normalizar domínio e validar conforme o procedimento definido.
- Não confiar exclusivamente no cabeçalho Origin como mecanismo de autenticação.

### api_keys
- `id`, `site_id`, `key_hash`, `key_prefix`, `created_at`, `revoked_at`.
- Segredos não devem ser armazenados em texto puro quando não houver necessidade operacional.
- Chaves públicas usadas no navegador não devem conceder acesso a relatórios privados.

### events
- `id`: chave primária.
- `site_id`: obrigatório e indexado.
- `event_type`: valor de uma lista ou esquema permitido.
- `page_path`: caminho normalizado sem query strings desnecessárias.
- `occurred_at`: horário validado.
- `session_id`: referência opcional à sessão.
- `properties`: propriedades permitidas, com limites de tamanho e sem conteúdo arbitrário.
- `created_at`: momento de ingestão.

Evitar coletar query strings completas, fragmentos, dados de formulários, conteúdo digitado ou URLs que possam conter tokens e informações pessoais.

### sessions
- `id`, `site_id`, `visitor_id` pseudônimo, `started_at`, `last_seen_at`, `ended_at`.
- `device_category`, `browser_family`, `os_family`: categorias opcionais.
- `country_code`, `region`, `city`: dados geográficos aproximados opcionais, quando justificados.
- `geo_confidence`: rótulo de confiança/qualidade, se houver fonte apropriada.
- Não assumir que visitor_id identifica uma pessoa ou um dispositivo físico único.

### daily_metrics
Agregações para acelerar relatórios:
- `site_id`, `date`.
- `page_views`, `sessions`, `visitors_estimated`, `events_count`.
- Restrição única por site e data, com métricas derivadas dos eventos aceitos.

### privacy_requests
Opcional no MVP, mas útil para registrar pedidos de titulares:
- `id`, `site_id`, `request_type`, `status`, `received_at`, `completed_at`.
- Evitar guardar dados pessoais adicionais desnecessários no registro.

### audit_logs
- `id`, `actor_user_id`, `site_id` opcional, `action`, `created_at`, metadados minimizados.
- Não registrar tokens, senhas ou payloads sensíveis nos logs.

## Relacionamentos

- Um usuário pode possuir vários sites.
- Um site pode ter vários domínios permitidos.
- Um site possui muitos eventos e sessões.
- Um site pode ter métricas agregadas por data.
- Membros adicionais podem receber papéis limitados em um site.

## Índices e restrições sugeridos

- Índice em `events(site_id, occurred_at)`.
- Índice em `events(site_id, event_type, occurred_at)` se consultas demonstrarem benefício.
- Índice em `sessions(site_id, started_at)`.
- Índice único em `daily_metrics(site_id, date)`.
- Chaves estrangeiras e regras explícitas de exclusão.
- Limites de tamanho para propriedades e caminhos.
- Restrições para impedir eventos sem site válido.

## Isolamento

Toda consulta de relatório deve incluir o escopo de projeto e validar permissões no backend. Considerar PostgreSQL Row-Level Security como defesa adicional, sem substituir a autorização da aplicação. Testes devem provar que usuário A não consegue ler ou modificar dados do site de usuário B.

## Retenção e exclusão

Definir prazo por categoria de dado. Implementar tarefas idempotentes para eliminar ou agregar dados expirados. A exclusão de um site deve tratar eventos, sessões, chaves, domínios e agregações de acordo com política documentada e requisitos legais.