# Ordem de Comando Final

## Decisão Consolidada

Dadas as áreas críticas identificadas no Relatório de Telemetria, o Plano de Tratamento Botânico e o Relatório de Impacto de Recursos, as ações devem centralizar-se na restauração imediata do sistema de irrigação, ajustes de parâmetros climáticos e correção do desequilíbrio na solução nutritiva para mitigar os efeitos do estresse hídrico e garantir a produtividade esperada.

## Ações Prioritárias para Atualização do Dashboard

1. Atualizar status da operação da bomba de irrigação e seus fluxos, garantindo visibilidade em tempo real.
2. Atualizar parâmetros climáticos padronizados para temperaturas e umidades relativas recomendadas.
3. Atualizar níveis de pH e EC da solução nutritiva para refletir os novos padrões estabelecidos.

## Payload de Comandos ESP32

```json
{
  "Irrigacao": {
    "Acao": "Reparo",
    "Fluxo": "1.5-2 L/min",
    "BombaBackup": "Ativar"
  },
  "Clima": {
    "Temperatura": "Configurar entre 22-24C",
    "UmidadeRelativa": "Incrementar para 55-65%",
    "Nebulizacao": "300-500 L/dia"
  },
  "Nutrientes": {
    "pH": "Ajustar para 5.8-6.2",
    "EC": "Ajustar para 1.2-1.6 mS/cm"
  }
}
```

## Cronograma de Execução

1. **Imediato (0-2 horas):**
   - Reparo ou substituição da bomba de irrigação.
   - Configuração inicial dos sistemas de ventilação e nebulização.
   
2. **Médio Prazo (2-6 horas):**
   - Monitoramento e ajuste fino das condições climáticas.
   - Ajustes iniciais na solução nutritiva conforme necessário.

3. **Curto Prazo (6-12 horas):**
   - Implementação de procedimentos de backup e contingência.
   - Inspeção e verificação dos ajustes realizados.

## Checklist de Verificação Pós-Implementação

- [ ] Verificar reinício e fluxo estável do sistema de irrigação.
- [ ] Certificar que as temperaturas ambiente e da solução nutritiva estejam nos parâmetros ajustes.
- [ ] Verificar precisão nos ajustes do pH e EC do reservatório de solução.
- [ ] Avaliar recuperação do índice de vigor vegetativo (NDVI) como esperado.
- [ ] Monitorar e anotar qualquer incidência de estresse hídrico visual após aplicação dos tratamentos.

## Alertas de Rollback

Se qualquer uma das métricas abaixo não mostrar tendência de melhoria dentro de 12 horas, desencadear rolbaks e ajustes adicionais:

- Umidade do substrato permanecer <35%.
- NDVI não melhorar continuamente em direção ao baseline de 0.78.
- Sinais de estresse hídrico não diminuírem significativamente.
- Flutuações de temperatura e umidade relativa continuarem fora dos valores aceitáveis.