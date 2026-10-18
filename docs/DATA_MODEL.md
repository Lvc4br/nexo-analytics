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
| `device_type` | categoria até 16 caracteres | Tipo aproximado, como desktop, celular ou tablet; derivado no navegador. |
| `browser_name` | categoria até 40 caracteres | Família do navegador; não armazena o user-agent completo. |
| `os_name` | categoria até 24 caracteres | Família do sistema operacional. |
| `country_code` | código até 2 caracteres | País aproximado, somente se obtido de um proxy confiável configurado. |
| `region_code` | código até 8 caracteres | Região administrativa ampla, quando o proxy configurado fornece esse dado. |
| `duration_ms` | inteiro opcional | Duração ativa da página no evento interno `page_duration`. |
| `created_at` | timestamp UTC | Horário atribuído pelo servidor na recepção. |

Eventos de versões antigas continuam sem preencher os novos campos; a API adiciona as colunas ausentes no startup. Não são armazenados IP, `Referer`, propriedades livres, conteúdo de formulário ou user-agent bruto. A localização é apenas um país/região aproximado de cabeçalho de proxy confiável, nunca coordenadas. Eventos são removidos quando a API inicia e encontram-se além de `TRACKER_EVENT_RETENTION_DAYS`; veja o limite operacional de limpeza em [docs/PRIVACY_LGPD.md](./PRIVACY_LGPD.md).

## Dados fora do banco Nexo

O login é configurado por variáveis de ambiente; esta versão não tem tabela de usuários. Dados agregados da Vercel são consultados em tempo real pela API Web Analytics e não são copiados para o banco. Eles não compartilham os identificadores de sessão do Nexo.

## Evolução futura

Se o projeto passar a suportar múltiplos administradores ou sites, o modelo pode ganhar entidades de usuários, sites, domínios verificados, chaves, auditoria e métricas diárias. Antes de alterações incompatíveis, adicionar migrations versionadas. Não coletar por padrão query strings completas, dados de formulários, conteúdo digitado ou informação sensível.
