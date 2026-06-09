# Ordem de Comando Final para Setor Alpha-3

## Decisão Consolidada
Este plano de ação visa resolver as anomalias críticas no Setor Alpha-3, abordando falhas de irrigação, problemas climáticos e nutricionais. As ações são ordenadas por prioridade para assegurar a restauração eficiente das condições ideais de cultivo para a alface hidropônica.

## Lista de Ações Priorizadas para o Dashboard
1. **Irrigação**: Restabelecer o fluxo da bomba de irrigação.
2. **Clima**: Ajustar os níveis térmicos e de umidade.
3. **Nutrientes**: Corregir os níveis de pH e EC da solução nutritiva.
4. **Monitoramento Contínuo**: Acompanhar as métricas de retorno à normalidade.

## Payload de Comandos ESP32 (Formato JSON):
```
{
  "irrigation": {
    "action": "restore",
    "frequency": "4-6 hours",
    "target_moisture": "60-70%"
  },
  "climate_control": {
    "temperature_target": "22-24°C",
    "humidity_target": "55-65%"
  },
  "nutrient_control": {
    "adjust_ph": "5.8-6.2",
    "adjust_ec": "1.4 mS/cm"
  }
}
```

## Cronograma de Execução
- **Primeira Hora**: Restabelecimento da irrigação e monitoramento da bomba.
- **Próximas 12 Horas**: Ajustes de temperatura e umidade.
- **Próximas 24 Horas**: Ajuste dos níveis de pH e EC e verificação de melhorias visuais.
- **Verificação de 48 Horas**: Indicadores de restauração completados com sucesso.

## Checklist de Verificação Pós-Implementação
1. **Irrigação**:
   - Ligar e monitorar fluxo da bomba.
   - Confirmar umidade entre 60-70% nas Linhas A e B.
2. **Clima**:
   - Verificar temperatura entre 22-24°C.
   - Confirmar umidade relativa entre 55-65%.
3. **Nutrientes**:
   - Estabiliizar pH em 5.8-6.2.
   - Confirmar EC em 1.4 mS/cm.
4. **Saúde Vegetal**:
   - Monitorar sinais de redução de estresse hídrico.
   - NDVI aumento relevante em 72 horas.

## Alertas de Rollback e Contingência
- **Se o fluxo de irrigação não estabilizar em 1 hora**: Ativar bomba de reserva e aumentar verificação manual.
- **Se temperatura ou umidade não se ajustarem em 12 horas**: Reavaliar sensores climáticos e ativar suporte técnico.
- **Se pH ou EC não estabilizarem em 48 horas**: Diluir solução nutritiva adicionalmente e preparar ajustes químicos detalhados.
- **Monitoramento Contínuo de Saúde Vegetal**: Se NDVI não melhorar em 72 horas, considerar consulta de especialista em saúde vegetal.