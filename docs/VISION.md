# Visão do produto — Nexo Analytics

## Resumo

O Nexo Analytics será uma plataforma própria para administrar múltiplos sites e centralizar suas métricas em um painel. O produto terá quatro blocos principais: dashboard, API, banco de dados e SDK de coleta.

## Problema

Quando vários sites são mantidos separadamente, seus dados de tráfego e eventos ficam espalhados. O objetivo é centralizar a observação e facilitar a comparação entre sites, preservando a separação de projetos.

## Público inicial

O primeiro cenário é o uso pelo proprietário de vários sites pessoais e profissionais. A arquitetura poderá evoluir para equipes e múltiplos usuários, mas o MVP deve priorizar um fluxo simples e seguro.

## Proposta de valor

- Um painel para vários sites.
- Métricas próprias controladas pelo operador.
- Eventos configuráveis para entender quais conteúdos recebem atenção.
- Relatórios por projeto e visão consolidada.
- Transparência sobre o que é observado e o grau de incerteza das estimativas.

## Funcionalidades planejadas

### MVP
- Cadastro e listagem de sites.
- Autenticação administrativa.
- Domínios permitidos por site.
- SDK com visualização de página e eventos simples.
- Endpoint de coleta validado.
- PostgreSQL e migrações.
- Dashboard com visualizações, sessões estimadas e páginas populares.
- Configurações mínimas de retenção e privacidade.

### Pós-MVP
- Eventos personalizados com esquemas permitidos.
- Dispositivos, navegador e sistema operacional em categorias.
- Geolocalização aproximada por IP, somente quando necessária e justificada.
- Exportação e exclusão de dados.
- Métricas agregadas e relatórios comparativos.
- Integrações externas, se houver APIs e permissões adequadas.
- Permissões para equipes e múltiplos administradores.

### Sinais de interesse profissional
Eventos como abrir currículo, visitar páginas de projetos e clicar em links de GitHub, LinkedIn ou contato podem indicar interesse. Esses sinais devem ser explicáveis e apresentados como hipóteses, nunca como identificação confirmada de recrutador, empresa ou intenção de contratação.

## Não objetivos

- Ser uma plataforma de hospedagem e deploy.
- Identificar pessoas por técnicas invasivas.
- Coletar conteúdo de formulários, senhas, campos de texto ou dados sensíveis.
- Garantir que um identificador de navegador equivale a uma pessoa física.
- Garantir precisão de localização ou distância com base em IP.
- Reconstruir dados individuais de serviços que fornecem somente métricas agregadas.

## Princípios de produto

1. Privacidade por padrão.
2. Dados minimizados.
3. Segurança multi-site.
4. Métricas compreensíveis e auditáveis.
5. Funcionalidades entregues incrementalmente.
6. Nenhuma promessa sobre dados que o sistema não consegue observar.

## Critérios de sucesso do MVP

- Um administrador consegue cadastrar mais de um site.
- Cada site tem identificador e domínios permitidos próprios.
- Um site de teste envia eventos válidos.
- O dashboard apresenta dados coerentes com os eventos de teste.
- Tentativas de acesso cruzado entre sites são bloqueadas e testadas.
- O ambiente local pode ser iniciado seguindo a documentação.
- Há política inicial de retenção, aviso de privacidade e procedimento de exclusão definidos.