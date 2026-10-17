# Contrato inicial da API

As rotas implementadas nesta primeira versão estão listadas abaixo. O restante deste documento descreve a expansão planejada para múltiplos projetos e coleta própria.

## Rotas implementadas

- `GET /health`: estado mínimo da API.
- `POST /api/v1/auth/login`: valida o administrador configurado e devolve token bearer com validade de 30 minutos.
- `GET /api/v1/auth/me`: retorna o administrador associado a um token válido.
- `POST /api/v1/auth/logout`: confirma um token válido e responde `204`; por ser assinado e stateless, o token só deixa de ser aceito ao expirar. A interface atual limpa seu token em memória ao sair.
- `GET /api/v1/analytics/overview?days=7|30|90`: exige token bearer; consulta a Vercel, compara períodos e retorna totais, tráfego diário, páginas populares, eventos personalizados e insights.

A API não persiste dados analíticos nesta versão. As respostas vêm da API de Web Analytics da Vercel.

## Convenções

- Prefixo: `/api/v1`.
- Transporte: HTTPS em ambientes publicados.
- Corpo: JSON UTF-8.
- Datas: ISO 8601 com fuso horário definido.
- Erros: respostas consistentes, sem stack traces ou detalhes internos.
- Listagens: paginação e limites explícitos.
- Relatórios: intervalo máximo configurável para evitar consultas excessivas.

## Saúde

### `GET /health`
Retorna estado mínimo da aplicação. Não deve expor segredos, configuração sensível ou dados pessoais.

## Autenticação administrativa

- `POST /api/v1/auth/login`: valida credenciais e inicia sessão segura.
- `POST /api/v1/auth/logout`: responde `204` para uma sessão autenticada.
- `GET /api/v1/auth/me`: retorna informações mínimas da conta autenticada.

Nesta versão, a sessão usa bearer token assinado com validade curta. O frontend mantém o token apenas em memória. A rota de logout não revoga o token no servidor; ele deixa de valer quando expira.

## Sites

- `GET /api/v1/sites`: lista apenas sites acessíveis pelo usuário.
- `POST /api/v1/sites`: cria um site.
- `GET /api/v1/sites/{site_id}`: consulta um site autorizado.
- `PATCH /api/v1/sites/{site_id}`: altera campos permitidos.
- `DELETE /api/v1/sites/{site_id}`: inicia exclusão controlada, com confirmação e tratamento dos dados relacionados.

## Domínios

- `GET /api/v1/sites/{site_id}/domains`
- `POST /api/v1/sites/{site_id}/domains`
- `DELETE /api/v1/sites/{site_id}/domains/{domain_id}`

A verificação de propriedade do domínio deve ser planejada se for necessária para o nível de proteção pretendido.

## Coleta pública

### `POST /api/v1/collect`

Recebe eventos enviados pelo SDK. O payload deve conter somente campos permitidos, por exemplo:

```json
{
  "project_id": "public-project-id",
  "event_type": "page_view",
  "page_path": "/projects/example",
  "occurred_at": "2026-01-01T12:00:00Z",
  "session_id": "ephemeral-session-id",
  "properties": {}
}
```

Esse JSON é um exemplo de contrato, não um formato já validado pelo servidor. O backend deve validar tipo, tamanho, timestamp, projeto, domínio e propriedades. Deve rejeitar tipos desconhecidos e payloads excessivos, aplicar rate limiting e não confiar no cliente para dados sensíveis.

## Analytics

- `GET /api/v1/sites/{site_id}/analytics/overview?from=...&to=...`
- `GET /api/v1/sites/{site_id}/analytics/pages?from=...&to=...`
- `GET /api/v1/sites/{site_id}/analytics/events?from=...&to=...`
- `GET /api/v1/sites/{site_id}/analytics/opportunities?from=...&to=...`

Os endpoints de analytics planejados por `site_id` ainda não foram implementados. A rota funcional atual é `GET /api/v1/analytics/overview?days=7|30|90`, autenticada, que consulta o projeto Vercel configurado no backend.

## Exportação e privacidade

Endpoints de exportação e exclusão serão definidos após estabelecer política de retenção, verificação de identidade e controles contra abuso. A exportação não deve permitir que um usuário consulte dados de outro projeto.

## Códigos HTTP esperados

- `200`: consulta ou atualização concluída.
- `201`: recurso criado.
- `204`: ação concluída sem corpo.
- `400`: requisição inválida.
- `401`: não autenticado.
- `403`: sem autorização.
- `404`: recurso não encontrado ou ocultado por política de acesso.
- `409`: conflito de estado.
- `413`: payload excessivo.
- `422`: falha de validação.
- `429`: limite de requisições excedido.
- `500`: erro interno genérico, sem detalhes sensíveis.

## Testes mínimos

- Entrada válida e inválida no coletor.
- Projeto inexistente ou inativo.
- Domínio não permitido.
- Rate limiting.
- Tentativa de ler dados de outro site.
- Períodos de relatório inválidos ou excessivos.
- Respostas sem credenciais ou detalhes internos.
