# Privacidade e LGPD

Este é um documento de engenharia, não aconselhamento jurídico. Antes de operar com visitantes reais, defina finalidade, base legal, transparência, contratos, retenção e atendimento de direitos com avaliação adequada ao contexto.

## O que o tracker envia nesta versão

O navegador envia à API Nexo somente:

- nome do evento, como `page_view` ou `contact_click`;
- caminho da página sem query string e fragmento;
- ID aleatório de sessão guardado em `sessionStorage`;
- ID aleatório do evento, usado para deduplicação.
- categorias técnicas resumidas: tipo de dispositivo, família do navegador e família do sistema operacional;
- `duration_ms` em um evento interno `page_duration`, para estimar o tempo ativo na página.

O tracker classifica as famílias técnicas no navegador; não envia user-agent completo, IP, cabeçalho `Referer`, propriedades livres, conteúdo de formulário, teclas digitadas ou identificador persistente entre sessões. Ele respeita `navigator.doNotTrack === "1"`, pode ser desabilitado pela aplicação e não coleta em localhost sem opção explícita. A Vercel permanece uma fonte separada de dados agregados; os IDs próprios do Nexo não são associados aos visitantes Vercel.

O backend armazena IDs pseudônimos de sessão, categorias técnicas, país/região estimados (se houver cabeçalho de proxy confiável), duração ativa, nome de evento, caminho e horário de recepção em SQLite local ou PostgreSQL de produção. O IP não é salvo pela tabela de eventos, mas o provedor de hospedagem, proxy ou logs operacionais podem processar dados de conexão; avalie também essa camada e seus contratos.

## Minimização e configuração

- Instrumente apenas interações úteis para a finalidade do portfólio.
- Não coloque identificadores pessoais em nomes de eventos ou caminhos de página.
- O coletor não aceita propriedades adicionais; futura expansão exige revisão de esquema e privacidade.
- O tracker não usa fingerprinting nem geolocalização do navegador. A API pode ler somente códigos amplos de país/região de um proxy confiável explicitamente configurado por `GEOLOCATION_PROXY`; a localização é aproximada e nunca coordenadas.
- Contagens Nexo por categoria são sessões, não contagens de aparelhos físicos únicos. A combinação de tipo/navegador/sistema é uma estatística técnica agregada, não um identificador.
- O limite de 365 dias por padrão é aplicado por limpeza quando a API inicia. Em serviços de longa duração, configure uma rotina/scheduler para executar a limpeza periódica e confirme que o prazo operacional atende à política definida.
- Não exponha `VERCEL_ACCESS_TOKEN`, credenciais administrativas ou `SESSION_SECRET` em código de navegador.

## Sessões e análise

O `session_id` permite agrupar eventos dentro de uma sessão/aba do navegador. Não prova que todos os eventos vieram da mesma pessoa nem representa necessariamente um único dispositivo físico. A duração é tempo com a página visível, não atenção comprovada; uma página ainda aberta pode não ter amostra enviada. A taxa de engajamento e a taxa de uma página são sinais agregados e descritivos; não identifique visitantes como recrutadores, funcionários de uma empresa ou pessoas específicas.

## Transparência e governança antes da produção

O aviso de privacidade do portfólio deve explicar, conforme aplicável, os eventos observados, finalidade, base legal, identificadores e duração, serviços envolvidos, retenção e canais de contato. Avalie cookies/armazenamento de sessão e preferências de consentimento conforme a finalidade e as regras aplicáveis. Defina procedimento para solicitações de titulares e revise contratos e controles dos fornecedores.

Checklist de produção:

- [ ] Finalidades e base legal avaliadas.
- [ ] Aviso de privacidade atualizado.
- [ ] Consentimento/preferências implementados quando necessários.
- [ ] Retenção e rotina de limpeza configuradas e verificadas.
- [ ] Origem do dashboard e do portfólio limitadas por configuração.
- [ ] PostgreSQL com backups, controles de acesso e TLS.
- [ ] Logs e dados do provedor revisados separadamente da tabela Nexo.
- [ ] Procedimento de titulares e resposta a incidentes documentados.
