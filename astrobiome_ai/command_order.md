# Ordem de Comando Final

## Decisão Consolidada
Após análise detalhada do relatório de telemetria, plano de tratamento botânico e impacto de recursos, as seguintes ações serão executadas para corrigir os desvios críticos no setor Alpha-3 (Alface Hidropônica).

## 1. Atualização do Dashboard da Colônia
Atualizar o dashboard para refletir o status em tempo real das anomalias corrigidas e métricas atuais de desempenho dos setores.

- Progresso de Correção de Umidade do Substrato: Status e relatórios de sensores.
- Parâmetros de Controle Climático Atualizados: Temperatura e umidade relativa com dados em tempo real.
- Ajustes de Luminosidade e Nível de pH: Monitoramento contínuo.
- Status de Estresse Foliar: Relatório de sintomas visuais pós-correção.

## 2. Comandos de Automação para o ESP32
Formatar e enviar o seguinte payload JSON ao ESP32 para execução automatizada das correções:

```json
{
  "irrigation": {
    "frequency": "increase",
    "target_moisture": 40
  },
  "temperature": {
    "target": 23
  },
  "humidity": {
    "target": 60
  },
  "lighting": {
    "intensity": 1000
  },
  "nutrients": {
    "ph_target": 6.0
  }
}
```

## 3. Prioridade e Sequência de Execução
1. **Irrigação**: Prioridade máxima - aumentar a umidade do substrato nas linhas afetadas.
2. **Clima interno**: Ajustar temperatura e umidade relativa.
3. **Iluminação e pH**: Corrigir a intensidade da luz e o nível de pH.
4. **Monitoramento contínuo de Estresse Foliar**: Aplicar ajustes contínuos conforme necessário.

## 4. Critérios de Verificação Pós-Execução
- Confirme com sensores a leitura de umidade adequada (35-45%).
- Revise a temperatura ambiente - alvo entre 22-24ºC.
- Certifique-se de que a umidade relativa está entre 55-65%.
- Verifique que a intensidade da luz se mantenha entre 800-1200 lux.
- Assegure que o pH está estabilizado entre 5.8-6.2.

## 5. Alertas de Rollback
Acionar rollback se qualquer uma das métricas não melhorar após 6 horas. Retornar ao estado anterior e reanalisar:
- Se a umidade não alcançar 35% ou mais.
- Se a temperatura ambiente não estiver ajustada.
- Se a luminosidade ou pH permanecerem fora do alvo.
Iniciar protocolo de escalonamento de suporte técnico caso ocorra rollback.

Estas instruções garantirão a manutenção e otimização das condições necessárias para o crescimento saudável das alfaces hidropônicas no setor Alpha-3.