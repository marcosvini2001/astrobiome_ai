#!/usr/bin/env python3
"""
Simula um sensor ESP32 enviando dados de telemetria e visão para a API Astrobiome AI.
"""

import random
from datetime import datetime, timezone

import requests

API_URL = "http://localhost:8000/analyze"

SECTOR = "Setor Alpha-3 (Alface Hidroponica)"

COLONY_CONTEXT = """Colonia: AstroBiome Station-1
Populacao: 48 habitantes | Modulo cultivos fechados: 6 setores ativos

Recursos globais:
  - Reservatorio hidrico principal: 68% (~14 dias de autonomia no consumo atual)
  - Reservatorio nutrientes: 54%
  - Energia solar + baterias: 71% carga (consumo diario projetado: 82% da geracao)
  - Capacidade maxima irrigacao emergencial: 240 L/dia sem comprometer reserva critica

Setor Alpha-3:
  - Cultura: alface (Lactuca sativa) ciclo dia 18/28
  - Producao esperada semanal: 12 kg | Risco de perda parcial se estresse > 6h"""


def _r(base: float, spread: float, decimals: int = 1) -> float:
    value = base + random.uniform(-spread, spread)
    return round(value, decimals)


def _pct(base: float, spread: float) -> float:
    return round(max(0.0, min(100.0, base + random.uniform(-spread, spread))), 1)


def generate_telemetry(timestamp: str) -> str:
    umidade_a = _pct(18, 4)
    umidade_b = _pct(22, 4)
    umidade_c = _pct(34, 3)
    temp_ambiente = _r(28.4, 1.5)
    temp_nutriente = _r(26.1, 1.2)
    umidade_rel = _pct(41, 5)
    luminosidade = int(_r(420, 80, 0))
    ph = _r(6.8, 0.2, 2)
    ec = _r(1.9, 0.2, 2)
    fluxo = round(max(0.0, random.choices([0.0, _r(1.2, 0.4, 2)], weights=[0.6, 0.4])[0]), 2)
    mins_sem_irrigacao = random.randint(40, 60) if fluxo == 0.0 else 0
    nivel_reservatorio = _pct(12, 3)

    def alerta_umidade(v: float) -> str:
        if v < 25:
            return "ALERTA: abaixo do limiar 35%"
        if v < 35:
            return "ATENCAO: proximo ao limiar"
        return "OK"

    fluxo_status = (
        f"{fluxo} L/min nos ultimos {mins_sem_irrigacao} min [FALHA CRITICA]"
        if fluxo == 0.0
        else f"{fluxo} L/min [OK]"
    )

    return f"""Timestamp: {timestamp} | Sensor ESP32 node_id=alpha3-esp32-01

Umidade do substrato (%):
  - Linha A (plantas 1-20): {umidade_a}%  [{alerta_umidade(umidade_a)}]
  - Linha B (plantas 21-40): {umidade_b}%  [{alerta_umidade(umidade_b)}]
  - Linha C (plantas 41-60): {umidade_c}%  [{alerta_umidade(umidade_c)}]

Temperatura ambiente (C): {temp_ambiente} (alvo: 22-24)
Temperatura nutriente (C): {temp_nutriente} (alvo: 20-22)
Umidade relativa (%): {umidade_rel} (alvo: 55-65)
Luminosidade (lux): {luminosidade} (alvo diurno: 800-1200)
pH solucao nutritiva: {ph} (alvo: 5.8-6.2)
EC (mS/cm): {ec} (alvo: 1.2-1.6)
Fluxo bomba irrigacao (L/min): {fluxo_status}
Nivel reservatorio local setor (%): {nivel_reservatorio}
Ultima irrigacao registrada: {timestamp}"""


def generate_vision(timestamp: str) -> str:
    manchas = _pct(14, 4)
    enrolamento = _pct(8, 3)
    ndvi = round(random.uniform(0.4, 0.8), 2)
    confianca = _pct(91, 3)
    pragas = False

    if ndvi < 0.55:
        correlacao = "padrao compativel com deficit hidrico agudo"
    elif ndvi < 0.65:
        correlacao = "padrao compativel com estresse hidrico moderado"
    else:
        correlacao = "padrao dentro dos limites normais de variacao"

    return f"""Timestamp: {timestamp} | Camera CV node_id=alpha3-cam-north

Deteccoes:
  - Manchas cloroticas (amareladas) em {manchas}% das copas - Linha A e B
  - Enrolamento foliar leve em {enrolamento}% das plantas - Linha A
  - Indice de vigor vegetativo (NDVI proxy): {ndvi} (baseline setor: 0.78)
  - Presenca de pragas visiveis: {pragas}
  - Confianca media das deteccoes: {confianca}%

Correlacao sugerida pelo pipeline CV: {correlacao}"""


def build_payload(timestamp: str) -> dict:
    return {
        "sector": SECTOR,
        "telemetry_data": generate_telemetry(timestamp),
        "vision_data": generate_vision(timestamp),
        "colony_context": COLONY_CONTEXT,
    }


def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = build_payload(timestamp)

    print("=" * 60)
    print("ASTROBIOME AI — ESP32 Simulator")
    print("=" * 60)
    print(f"\n[SETOR]  {payload['sector']}")
    print(f"\n[TELEMETRIA]\n{payload['telemetry_data']}")
    print(f"\n[VISAO]\n{payload['vision_data']}")
    print(f"\n[CONTEXTO]\n{payload['colony_context']}")
    print("\n" + "=" * 60)
    print(f"Enviando POST para {API_URL} ...")

    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Resposta [{response.status_code}]: {response.json()}")
    except requests.exceptions.ConnectionError:
        print(f"ERRO: nao foi possivel conectar em {API_URL}. A API esta rodando?")
    except requests.exceptions.Timeout:
        print("ERRO: timeout ao conectar na API.")
    except requests.exceptions.HTTPError as exc:
        print(f"ERRO HTTP {exc.response.status_code}: {exc.response.text}")

    print("=" * 60)


if __name__ == "__main__":
    main()
