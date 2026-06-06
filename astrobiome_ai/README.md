# 🪐 AstroBiome AI

> **Estufa automatizada e monitorada por visão computacional, controlada por um ecossistema de múltiplos agentes inteligentes para otimização de recursos vitais em missões interplanetárias.**

---

## 🚀 O Problema e a Solução

**O Problema:** Em ambientes hostis como a Lua ou Marte, os recursos (água, energia, solo nutrido, CO2) são extremamente escassos e imprevisíveis. Qualquer variação climática ou praga pode arruinar uma plantação inteira, ameaçando a sobrevivência da colônia.

**A Solução:** Uma estufa inteligente onde um sistema de **Inteligência Artificial Generativa e Multiagentes (CrewAI)** atua como o cérebro estratégico. O sistema processa telemetria em tempo real e imagens fitossanitárias para tomar decisões autônomas, garantindo a resiliência do cultivo e a gestão rigorosa de recursos.

---

## 🛠️ Arquitetura Técnica (4 Camadas)

A solução é composta pela integração direta das seguintes disciplinas:

1. **Camada de Hardware e Edge Computing (IoT / ESP32)**
   * **Sensores:** Coleta de umidade do substrato, temperatura, luminosidade (LDR) e nível de reservatório.
   * **Atuadores:** Relés controlando luz solar artificial (LEDs), minibombas de irrigação e coolers.
   * **Edge Logic:** Regras críticas locais para sobrevivência emergencial da planta caso haja perda de comunicação.

2. **Camada de Visão Computacional (Análise de Imagem)**
   * **Detecção Fitossanitária:** Modelos de Machine Learning (YOLO/CNN) analisam o feed da estufa para identificar estágios de crescimento, manchas cloróticas, fungos ou deficiências nutricionais (proxy de NDVI).

3. **Camada de IA Generativa (Agentes e RAG)**
   * Orquestração construída com **CrewAI**.
   * Fluxo de agentes especializados que traduzem alertas visuais e de sensores em comandos estruturados para o hardware.

4. **Camada de Visualização (Dashboards e Mobile)**
   * **Streamlit:** Dashboard de controle da missão exibindo gráficos em tempo real, feed de câmeras com *bounding boxes* e o log de raciocínio dos agentes.
   * **React Native:** App mobile para o "astronauta operador" receber notificações push emergenciais e acionar contingências.

---

## 🤖 O Ecossistema de Agentes

O cérebro do AstroBiome AI opera em um fluxo sequencial rígido:

* 📡 **Agente Analista de Telemetria:** Consome dados brutos do ESP32 e CV para diagnosticar crises (ex: declínio agudo de umidade cruzado com manchas foliares).
* 🌿 **Agente Botânico Aeroespacial (RAG):** Consulta uma base vetorial com manuais de hidroponia e diretrizes da NASA/FAO para prescrever o tratamento científico exato.
* ⚙️ **Agente Engenheiro de Recursos:** Calcula o impacto logístico do tratamento sugerido (ex: impacto no consumo hídrico e energético), autorizando ou vetando a ação para proteger a colônia.
* 👨‍🚀 **Agente Comandante Central:** Consolida as análises e emite a Ordem de Comando final, atualizando dashboards e enviando a automação corretiva de volta ao ESP32.

---

## ⚙️ Como Executar o Sistema de Agentes

Certifique-se de ter o Python 3.10 a 3.12 instalado. O projeto utiliza o gerenciador `uv` nativo do CrewAI para alta performance.

**1. Clone o repositório:**
```bash
git clone [https://github.com/marcosvini2001/astrobiome_ai.git](https://github.com/marcosvini2001/astrobiome_ai.git)
cd astrobiome_ai
