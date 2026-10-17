# SDK JavaScript de rastreamento

## Objetivo

O SDK será um pacote pequeno para integrar sites ao Nexo Analytics. Sua responsabilidade é enviar eventos de telemetria permitidos; não deve administrar contas nem consultar relatórios privados.

## Instalação planejada

A forma final de distribuição ainda será definida. Uma opção é disponibilizar um script hospedado pelo próprio serviço:

```html
<script
  defer
  src="https://SEU-DOMINIO/sdk.js"
  data-project="PUBLIC_PROJECT_ID">
</script>
```

O domínio e o atributo acima são placeholders. Não copiar para produção antes de a distribuição estar implementada.

## Eventos iniciais

- `page_view`: visualização de página.
- `custom_event`: evento de uma lista permitida.
- `resume_open`: abertura de página de currículo, se configurado.
- `project_view`: visualização de projeto.
- `outbound_click`: clique em link profissional permitido.

Não capturar conteúdo de formulários, teclas digitadas, senhas, dados de pagamento, conteúdo privado, query strings completas ou dados sensíveis.

## Sessões e visitantes

O SDK pode usar identificadores de sessão e, se justificado e configurado, identificadores pseudônimos persistentes. A política deve explicar finalidade, duração, armazenamento e escolha de consentimento quando aplicável. Não usar fingerprinting invasivo. Um ID não prova identidade civil nem representa necessariamente um dispositivo físico único.

## Privacidade

- Respeitar configurações de consentimento e preferências do usuário quando aplicáveis.
- Permitir desativar eventos não essenciais.
- Minimizar dados e tamanho do payload.
- Remover query strings e fragmentos da URL por padrão.
- Não incluir IP no payload do SDK.
- Não registrar conteúdo arbitrário de DOM.
- Não bloquear a navegação se a coleta falhar.
- Oferecer mecanismo para desativar o tracker em ambientes de desenvolvimento.

## Robustez e segurança

- Enviar por HTTPS.
- Aplicar timeout e tratamento de falhas.
- Limitar o tamanho e a frequência dos eventos.
- Evitar loops de envio e duplicação quando possível.
- Validar novamente todos os campos no backend; a validação do SDK não é uma barreira de segurança.
- O identificador público do projeto pode ser exposto no navegador; segredos administrativos não podem.

## API pública planejada

Uma interface possível:

```ts
type NexoConfig = {
  projectId: string;
  endpoint?: string;
  enabled?: boolean;
};

type NexoTracker = {
  track(eventName: string, properties?: Record<string, unknown>): void;
  page(): void;
  disable(): void;
};
```

Essa assinatura é uma proposta. Antes de publicar, definir nomes finais, tipos permitidos, comportamento de consentimento, versionamento semântico e compatibilidade entre SDK e API.

## Testes

- Eventos aceitos e rejeitados.
- Falha de rede sem bloquear a página.
- Remoção de query strings.
- Desativação da coleta.
- Respeito a consentimento quando configurado.
- Limites de payload e de frequência.
- Compatibilidade com navegação tradicional e aplicações SPA.