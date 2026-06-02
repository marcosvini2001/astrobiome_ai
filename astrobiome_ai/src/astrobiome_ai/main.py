#!/usr/bin/env python
import sys
import warnings

from astrobiome_ai.crew import AstrobiomeAi

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def _default_inputs() -> dict:
    """Cenário de exemplo: falha de irrigação e estresse foliar no Setor Alpha-3."""
    return {
        "sector": "Setor Alpha-3 (Alface Hidroponica)",
        "telemetry_data": """
Timestamp: 2026-06-01T14:32:00Z | Sensor ESP32 node_id=alpha3-esp32-01

Umidade do substrato (%):
  - Linha A (plantas 1-20): 18%  [ALERTA: abaixo do limiar 35%]
  - Linha B (plantas 21-40): 22%  [ALERTA: abaixo do limiar 35%]
  - Linha C (plantas 41-60): 34%  [ATENCAO: proximo ao limiar]

Temperatura ambiente (C): 28.4 (alvo: 22-24)
Temperatura nutriente (C): 26.1 (alvo: 20-22)
Umidade relativa (%): 41 (alvo: 55-65)
Luminosidade (lux): 420 (alvo diurno: 800-1200)
pH solucao nutritiva: 6.8 (alvo: 5.8-6.2)
EC (mS/cm): 1.9 (alvo: 1.2-1.6)
Fluxo bomba irrigacao (L/min): 0.0 nos ultimos 47 min [FALHA CRITICA]
Nivel reservatorio local setor (%): 12
Ultima irrigacao registrada: 2026-06-01T13:45:00Z
        """.strip(),
        "vision_data": """
Timestamp: 2026-06-01T14:30:00Z | Camera CV node_id=alpha3-cam-north

Deteccoes:
  - Manchas cloroticas (amareladas) em 14% das copas - Linha A e B
  - Enrolamento foliar leve em 8% das plantas - Linha A
  - Indice de vigor vegetativo (NDVI proxy): 0.52 (baseline setor: 0.78)
  - Sem presenca de pragas visiveis
  - Confiança media das deteccoes: 91%

Correlacao sugerida pelo pipeline CV: padrao compativel com deficit hidrico agudo
        """.strip(),
        "colony_context": """
Colonia: AstroBiome Station-1
Populacao: 48 habitantes | Modulo cultivos fechados: 6 setores ativos

Recursos globais:
  - Reservatorio hídrico principal: 68% (~14 dias de autonomia no consumo atual)
  - Reservatorio nutrientes: 54%
  - Energia solar + baterias: 71% carga (consumo diario projetado: 82% da geracao)
  - Capacidade maxima irrigacao emergencial: 240 L/dia sem comprometer reserva critica

Setor Alpha-3:
  - Cultura: alface (Lactuca sativa) ciclo dia 18/28
  - Producao esperada semanal: 12 kg | Risco de perda parcial se estresse > 6h
        """.strip(),
    }


def run():
    """
    Run the crew.
    """
    inputs = _default_inputs()

    try:
        AstrobiomeAi().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = _default_inputs()
    try:
        AstrobiomeAi().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        AstrobiomeAi().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = _default_inputs()

    try:
        AstrobiomeAi().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        **_default_inputs(),
        **{k: v for k, v in trigger_payload.items() if k in ("sector", "telemetry_data", "vision_data", "colony_context")},
    }

    try:
        result = AstrobiomeAi().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
