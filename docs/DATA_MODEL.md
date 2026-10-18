# Modelo de dados

## Persistência implementada

A tabela `portfolio_events` é criada pelo SQLAlchemy no startup. SQLite local fica em `services/api/.data/nexo.sqlite3`; produção exige PostgreSQL persistente.

| Coluna | Tipo lógico | Uso |
|---|---|---|
| `id` | UUID em texto, chave primária | ID do evento para evitar inserção duplicada. |
| `site_id` | string até 100 caracteres, indexada | ID público validado contra `PORTFOLIO_SITE_ID`. |
| `session_id` | UUID em texto, indexada junto do site | Agrupa eventos nesta sessão/aba do navegador. |
| `event_name` | string até 80 caracteres | `page_view` ou interação curta como `contact_click`. |
| `path` | string até 300 caracteres | Caminho sem query string e fragmento. |
| `created_at` | timestamp UTC | Horário atribuído pelo servidor na recepção. |

Não são armazenados IP, `Referer`, propriedades livres, conteúdo de formulário, dispositivo ou geolocalização. Eventos são removidos quando a API inicia e encontram-se além de `TRACKER_EVENT_RETENTION_DAYS`; veja o limite operacional de limpeza em [docs/PRIVACY_LGPD.md](./PRIVACY_LGPD.md).

## Dados fora do banco Nexo

O login é configurado por variáveis de ambiente; esta versão não tem tabela de usuários. Dados agregados da Vercel são consultados em tempo real pela API Web Analytics e não são copiados para o banco. Eles não compartilham os identificadores de sessão do Nexo.

## Evolução futura

Se o projeto passar a suportar múltiplos administradores ou sites, o modelo pode ganhar entidades de usuários, sites, domínios verificados, chaves, auditoria e métricas diárias. Antes de alterações incompatíveis, adicionar migrations versionadas. Não coletar por padrão query strings completas, dados de formulários, conteúdo digitado ou informação sensível.
