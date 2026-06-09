import { useCallback, useEffect, useRef, useState } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'

const API = 'https://jubilant-chainsaw-4j6rxj7j95x92qgr9-8000.app.github.dev'

// ── Payload de sensor simulado (mesmo formato do esp32_simulator.py) ─────────
const SIMULATED_SECTOR = 'Setor Alpha-3 (Alface Hidroponica)'

const SIMULATED_TELEMETRY = `Timestamp: 2026-06-08T12:00:00Z | Sensor ESP32 node_id=alpha3-esp32-01

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
Ultima irrigacao registrada: 2026-06-08T11:13:00Z`

const SIMULATED_VISION = `Timestamp: 2026-06-08T12:00:00Z | Camera CV node_id=alpha3-cam-north

Deteccoes:
  - Manchas cloroticas (amareladas) em 14% das copas - Linha A e B
  - Enrolamento foliar leve em 8% das plantas - Linha A
  - Indice de vigor vegetativo (NDVI proxy): 0.52 (baseline setor: 0.78)
  - Presenca de pragas visiveis: False
  - Confianca media das deteccoes: 91%

Correlacao sugerida pelo pipeline CV: padrao compativel com deficit hidrico agudo`

const SIMULATED_CONTEXT = `Colonia: AstroBiome Station-1
Populacao: 48 habitantes | Modulo cultivos fechados: 6 setores ativos

Recursos globais:
  - Reservatorio hidrico principal: 68% (~14 dias de autonomia no consumo atual)
  - Reservatorio nutrientes: 54%
  - Energia solar + baterias: 71% carga (consumo diario projetado: 82% da geracao)
  - Capacidade maxima irrigacao emergencial: 240 L/dia sem comprometer reserva critica

Setor Alpha-3:
  - Cultura: alface (Lactuca sativa) ciclo dia 18/28
  - Producao esperada semanal: 12 kg | Risco de perda parcial se estresse > 6h`

// ── Helpers para parsear last_sensor_data ────────────────────────────────────
function parseField(text, regex, group = 1) {
  if (!text) return null
  const m = text.match(regex)
  return m ? m[group].trim() : null
}

function parseSensorData(telemetry) {
  if (!telemetry) return null
  return {
    umidadeA: parseField(telemetry, /Linha A[^:]*:\s*([\d.]+)%/),
    umidadeB: parseField(telemetry, /Linha B[^:]*:\s*([\d.]+)%/),
    umidadeC: parseField(telemetry, /Linha C[^:]*:\s*([\d.]+)%/),
    tempAmbiente: parseField(telemetry, /Temperatura ambiente \(C\):\s*([\d.]+)/),
    ph: parseField(telemetry, /pH solucao nutritiva:\s*([\d.]+)/),
    ec: parseField(telemetry, /EC \(mS\/cm\):\s*([\d.]+)/),
    luminosidade: parseField(telemetry, /Luminosidade \(lux\):\s*(\d+)/),
    bomba: parseField(telemetry, /Fluxo bomba irrigacao \(L\/min\):\s*([^\n]+)/),
  }
}

// ── Lógica de alertas por métrica ────────────────────────────────────────────
function umidadeColor(v) {
  if (v === null) return '#666'
  const n = parseFloat(v)
  if (n < 25) return '#ef4444'
  if (n < 35) return '#f59e0b'
  return '#22c55e'
}

function tempColor(v) {
  if (v === null) return '#666'
  const n = parseFloat(v)
  if (n > 27) return '#ef4444'
  if (n > 24) return '#f59e0b'
  return '#22c55e'
}

function phColor(v) {
  if (v === null) return '#666'
  const n = parseFloat(v)
  if (n < 5.6 || n > 6.5) return '#ef4444'
  if (n < 5.8 || n > 6.2) return '#f59e0b'
  return '#22c55e'
}

function ecColor(v) {
  if (v === null) return '#666'
  const n = parseFloat(v)
  if (n > 2.2 || n < 0.8) return '#ef4444'
  if (n > 1.6 || n < 1.2) return '#f59e0b'
  return '#22c55e'
}

function luxColor(v) {
  if (v === null) return '#666'
  const n = parseFloat(v)
  if (n < 300 || n > 1500) return '#ef4444'
  if (n < 800) return '#f59e0b'
  return '#22c55e'
}

function bombaColor(v) {
  if (v === null || v === undefined) return '#666'
  if (v.includes('FALHA CRITICA')) return '#ef4444'
  return '#22c55e'
}

// ── Estilos ───────────────────────────────────────────────────────────────────
const S = {
  root: {
    minHeight: '100vh',
    backgroundColor: '#0a0e1a',
    color: '#e2e8f0',
    fontFamily: "'Segoe UI', system-ui, sans-serif",
    padding: '0 0 48px',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '20px 32px',
    borderBottom: '1px solid #1e2a40',
    backgroundColor: '#0d1220',
  },
  headerTitle: {
    margin: 0,
    fontSize: '1.25rem',
    fontWeight: 700,
    letterSpacing: '0.05em',
    color: '#7dd3fc',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  badge: (status) => ({
    padding: '4px 14px',
    borderRadius: '999px',
    fontSize: '0.75rem',
    fontWeight: 700,
    letterSpacing: '0.08em',
    backgroundColor:
      status === 'processing' ? '#78350f' :
      status === 'completed'  ? '#14532d' :
      status === 'error'      ? '#7f1d1d' : '#1e293b',
    color:
      status === 'processing' ? '#fde68a' :
      status === 'completed'  ? '#86efac' :
      status === 'error'      ? '#fca5a5' : '#94a3b8',
    border: `1px solid ${
      status === 'processing' ? '#d97706' :
      status === 'completed'  ? '#16a34a' :
      status === 'error'      ? '#dc2626' : '#334155'
    }`,
  }),
  btn: (disabled) => ({
    padding: '8px 20px',
    borderRadius: '6px',
    border: 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontWeight: 600,
    fontSize: '0.875rem',
    backgroundColor: disabled ? '#1e3a5f' : '#1d4ed8',
    color: disabled ? '#64748b' : '#fff',
    transition: 'background 0.2s',
  }),
  main: {
    padding: '32px',
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '32px',
  },
  sectionTitle: {
    margin: '0 0 16px',
    fontSize: '0.75rem',
    fontWeight: 700,
    letterSpacing: '0.12em',
    color: '#475569',
    textTransform: 'uppercase',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '12px',
  },
  card: (accentColor) => ({
    backgroundColor: '#0d1628',
    border: `1px solid ${accentColor}44`,
    borderLeft: `3px solid ${accentColor}`,
    borderRadius: '8px',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  }),
  cardLabel: {
    fontSize: '0.7rem',
    fontWeight: 600,
    letterSpacing: '0.08em',
    color: '#64748b',
    textTransform: 'uppercase',
  },
  cardValue: (color) => ({
    fontSize: '1.4rem',
    fontWeight: 700,
    color,
    fontFamily: 'monospace',
    lineHeight: 1.1,
  }),
  cardSub: {
    fontSize: '0.7rem',
    color: '#475569',
    fontFamily: 'monospace',
  },
  bombaCard: (color) => ({
    backgroundColor: '#0d1628',
    border: `1px solid ${color}44`,
    borderLeft: `3px solid ${color}`,
    borderRadius: '8px',
    padding: '16px',
    gridColumn: '1 / -1',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  }),
  bombaValue: (color) => ({
    fontSize: '0.9rem',
    fontWeight: 600,
    fontFamily: 'monospace',
    color,
    wordBreak: 'break-word',
  }),
  commandPanel: {
    backgroundColor: '#0d1628',
    border: '1px solid #1e2a40',
    borderRadius: '8px',
    padding: '24px',
  },
  commandEmpty: {
    color: '#334155',
    fontFamily: 'monospace',
    fontSize: '0.875rem',
    textAlign: 'center',
    padding: '32px 0',
  },
  errorBanner: {
    backgroundColor: '#7f1d1d22',
    border: '1px solid #dc2626',
    borderRadius: '8px',
    padding: '12px 16px',
    color: '#fca5a5',
    fontSize: '0.875rem',
    fontFamily: 'monospace',
  },
  lastUpdated: {
    fontSize: '0.7rem',
    color: '#334155',
    marginTop: '4px',
  },
}

// ── Componente principal ──────────────────────────────────────────────────────
export default function App() {
  const [status, setStatus] = useState('idle')
  const [sensors, setSensors] = useState(null)
  const [commandOrder, setCommandOrder] = useState(null)
  const [apiError, setApiError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [firing, setFiring] = useState(false)

  const fetchStatus = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API}/status`)
      setStatus(data.status ?? 'idle')
      setSensors(parseSensorData(data.last_sensor_data?.telemetry_data ?? null))
      setCommandOrder(data.command_order ?? null)
      setApiError(data.error ?? null)
      setLastUpdated(new Date().toLocaleTimeString('pt-BR'))
    } catch {
      // API offline — não sobrescreve estado anterior
    }
  }, [])

  useEffect(() => {
    fetchStatus()
    const id = setInterval(fetchStatus, 5000)
    return () => clearInterval(id)
  }, [fetchStatus])

  async function handleAnalyze() {
    setFiring(true)
    try {
      await axios.post(`${API}/analyze`, {
        sector: SIMULATED_SECTOR,
        telemetry_data: SIMULATED_TELEMETRY,
        vision_data: SIMULATED_VISION,
        colony_context: SIMULATED_CONTEXT,
      })
      setStatus('processing')
    } catch (err) {
      setApiError(err.message)
    } finally {
      setFiring(false)
    }
  }

  const s = sensors
  const isProcessing = status === 'processing'

  return (
    <div style={S.root}>
      {/* ── Header ── */}
      <header style={S.header}>
        <h1 style={S.headerTitle}>⊕ ASTROBIOME AI — MISSION CONTROL</h1>
        <div style={S.headerRight}>
          <span style={S.badge(status)}>{status.toUpperCase()}</span>
          <button
            style={S.btn(isProcessing || firing)}
            disabled={isProcessing || firing}
            onClick={handleAnalyze}
          >
            {firing ? 'Enviando…' : '▶ Disparar Análise'}
          </button>
        </div>
      </header>

      <main style={S.main}>
        {/* ── Banner de erro ── */}
        {apiError && (
          <div style={S.errorBanner}>⚠ Erro: {apiError}</div>
        )}

        {/* ── Cards de métricas ── */}
        <section>
          <p style={S.sectionTitle}>Telemetria dos Sensores</p>
          <div style={S.grid}>
            <MetricCard
              label="Umidade — Linha A"
              value={s?.umidadeA ? `${s.umidadeA}%` : '—'}
              sub="alvo: ≥ 35%"
              color={umidadeColor(s?.umidadeA)}
            />
            <MetricCard
              label="Umidade — Linha B"
              value={s?.umidadeB ? `${s.umidadeB}%` : '—'}
              sub="alvo: ≥ 35%"
              color={umidadeColor(s?.umidadeB)}
            />
            <MetricCard
              label="Umidade — Linha C"
              value={s?.umidadeC ? `${s.umidadeC}%` : '—'}
              sub="alvo: ≥ 35%"
              color={umidadeColor(s?.umidadeC)}
            />
            <MetricCard
              label="Temp. Ambiente"
              value={s?.tempAmbiente ? `${s.tempAmbiente} °C` : '—'}
              sub="alvo: 22–24 °C"
              color={tempColor(s?.tempAmbiente)}
            />
            <MetricCard
              label="pH"
              value={s?.ph ?? '—'}
              sub="alvo: 5.8–6.2"
              color={phColor(s?.ph)}
            />
            <MetricCard
              label="EC"
              value={s?.ec ? `${s.ec} mS/cm` : '—'}
              sub="alvo: 1.2–1.6"
              color={ecColor(s?.ec)}
            />
            <MetricCard
              label="Luminosidade"
              value={s?.luminosidade ? `${s.luminosidade} lux` : '—'}
              sub="alvo: 800–1200 lux"
              color={luxColor(s?.luminosidade)}
            />
            {/* Bomba — largura total */}
            <div style={S.bombaCard(bombaColor(s?.bomba))}>
              <span style={S.cardLabel}>Status da Bomba de Irrigação</span>
              <span style={S.bombaValue(bombaColor(s?.bomba))}>
                {s?.bomba ?? '— sem dados'}
              </span>
            </div>
          </div>
          {lastUpdated && (
            <p style={S.lastUpdated}>Última atualização: {lastUpdated}</p>
          )}
        </section>

        {/* ── Ordem de Comando ── */}
        <section>
          <p style={S.sectionTitle}>Ordem de Comando</p>
          <div style={S.commandPanel}>
            {commandOrder ? (
              <div className="markdown-body">
                <ReactMarkdown>{commandOrder}</ReactMarkdown>
              </div>
            ) : (
              <p style={S.commandEmpty}>
                {isProcessing
                  ? '⟳ Crew em execução — aguardando resultado…'
                  : 'Nenhuma ordem de comando disponível ainda.'}
              </p>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

function MetricCard({ label, value, sub, color }) {
  return (
    <div style={S.card(color)}>
      <span style={S.cardLabel}>{label}</span>
      <span style={S.cardValue(color)}>{value}</span>
      <span style={S.cardSub}>{sub}</span>
    </div>
  )
}
