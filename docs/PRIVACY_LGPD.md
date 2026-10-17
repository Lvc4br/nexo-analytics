# Privacidade e LGPD — planejamento técnico

> Este documento é uma base de engenharia e não constitui parecer jurídico. Antes de operar com visitantes reais, avaliar finalidades, bases legais, transparência, contratos, segurança e orientações aplicáveis da ANPD com apoio qualificado quando necessário.

## Princípios de desenho

- Finalidade específica e documentada.
- Adequação e necessidade: coletar somente o necessário.
- Transparência sobre o que é observado.
- Segurança durante transmissão, armazenamento, acesso e exclusão.
- Retenção limitada e descarte verificável.
- Capacidade de atender solicitações pertinentes dos titulares.
- Separação de dados entre projetos.

## Categorias de dados possíveis

- Eventos de navegação permitidos.
- Caminho de página normalizado.
- Horário aproximado do evento.
- Identificador de sessão e, se justificado, identificador pseudônimo.
- Categoria de dispositivo, navegador e sistema operacional.
- Localização aproximada derivada de IP, se necessária e com confiança explicitada.
- Eventos de interação profissional configurados pelo operador.

Não coletar por padrão conteúdo de formulário, campos digitados, senhas, dados de pagamento, conteúdo privado, query strings completas ou informações sensíveis.

## Endereço IP e geolocalização

O endereço IP pode ser dado pessoal dependendo do contexto. Evitar armazenar o IP completo. Se houver necessidade de processá-lo temporariamente para segurança ou geolocalização aproximada, documentar a finalidade, restringir o acesso e descartar o valor bruto conforme prazo definido.

Geolocalização por IP é aproximada e pode indicar a saída de uma rede, VPN ou provedor, não a localização física exata do visitante. Qualquer regra como “dentro de 80 km de São Paulo” deve ser apresentada como estimativa, com opção de “desconhecido” e sem inferir endereço ou identidade.

## Identificadores e recorrência

Um identificador pseudônimo pode ajudar a estimar recorrência dentro das limitações do navegador e das configurações de privacidade. Ele não identifica necessariamente uma pessoa, não garante reconhecimento entre dispositivos e pode ser apagado ou redefinido. Não usar fingerprinting invasivo.

Avaliar a necessidade de consentimento ou outra base legal para identificadores persistentes e tecnologias não essenciais. Oferecer mecanismos de preferência e respeitar a escolha definida pelo projeto.

## Sinais profissionais

Abertura de currículo, visita a projetos ou clique em contato podem ser apresentados como eventos ou sinais agregados. Não declarar que um visitante é recrutador, funcionário de determinada empresa ou pessoa específica sem evidência independente legítima. Evitar decisões automatizadas de alto impacto com base nesses sinais.

## Transparência

O aviso de privacidade do site monitorado deve explicar, conforme aplicável:
- quais eventos são coletados;
- finalidades e base legal;
- identificadores utilizados e duração;
- uso de estimativas geográficas;
- compartilhamentos e operadores envolvidos;
- prazos de retenção;
- canais para exercer direitos e entrar em contato;
- mecanismos de consentimento e preferências.

## Retenção e exclusão

Definir prazos separados para eventos detalhados, sessões, métricas agregadas, logs de segurança e backups. Criar rotinas idempotentes para expiração e documentar como a exclusão se propaga para dados derivados. Dados agregados podem continuar sendo dados pessoais se ainda permitirem identificação; avaliar caso a caso.

## Direitos e governança

Planejar fluxo para receber, verificar e responder a solicitações pertinentes de acesso, correção, eliminação ou outras aplicáveis. Registrar o mínimo necessário para acompanhar a solicitação. Definir quem controla os dados e quem atua como operador em cada implantação, de acordo com os papéis reais e os contratos.

## Antes de produção

- [ ] Inventário de dados e finalidades.
- [ ] Bases legais avaliadas.
- [ ] Aviso de privacidade publicado.
- [ ] Consentimento/preferências implementados quando necessários.
- [ ] Prazos de retenção aprovados e automatizados.
- [ ] Procedimento de direitos dos titulares.
- [ ] Contratos e fornecedores avaliados.
- [ ] Segurança, backups e resposta a incidentes revisados.
- [ ] Avaliação de riscos documentada.