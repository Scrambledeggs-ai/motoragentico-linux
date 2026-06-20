# 🧠 Motor Agéntico — Linux

Dashboard local, privado y de solo lectura para visualizar tu operación con IA.

> Versión Linux del Motor Agéntico creado por la comunidad de aprendizaje de IA de Benjamín.

---

## ¿Qué hace?

Responde las 4 preguntas que todo operador de IA debería poder ver:

| Tab | Pregunta |
|-----|----------|
| 💸 **Costos** | ¿Cuánto gastás de verdad? Suma Claude Code con costos reales por token |
| 📈 **ROI** | ¿Te conviene suscripción o API? Comparativa con tu uso actual |
| 🧠 **Memoria** | ¿Qué sabe la IA de vos? Visualiza tu vault de Obsidian y detecta archivos obsoletos |
| 👀 **Actividad** | ¿Qué está pasando ahora? Sesiones recientes de Claude Code y Hermes |
| 🌙 **El Sueño** | Analiza cómo trabajás y sugiere optimizaciones automáticas |

**100% local · privado · sin servidores externos · cada uno ve sus propios datos**

---

## Requisitos

- Linux (cualquier distro)
- Claude Code instalado y con uso previo
- Hermes instalado (opcional, para ver esas sesiones)
- Obsidian (opcional, para el tab de Memoria)

---

## Instalación

### 1. Instalar `uv` (si no lo tenés)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # o abrí una terminal nueva
```

### 2. Clonar el repositorio

```bash
git clone https://github.com/Scrambledeggs-ai/motoragentico-linux.git
cd motoragentico-linux
```

### 3. Correr el dashboard

```bash
./run.sh
```

Se abre automáticamente en **http://localhost:8501**

---

## Configuración

Al abrir el dashboard, en el panel lateral izquierdo podés configurar:

- **Ruta de tu vault Obsidian** — para el tab de Memoria
- **Período de análisis** — de 7 a 90 días
- **Tu plan de Claude Code** — para el cálculo de ROI
- **Tu plan de Hermes** — ídem

No hay archivo de configuración que editar, todo se hace desde la interfaz.

---

## ¿Cómo funciona?

El dashboard lee datos **solo de tu máquina local**:

| Fuente | Ruta |
|--------|------|
| Claude Code | `~/.claude/projects/**/*.jsonl` |
| Hermes | CLI (`hermes insights`, `hermes sessions`) |
| Obsidian | La carpeta que configurés en el sidebar |

No envía ningún dato a internet. No necesita API keys propias.

---

## Precios Claude Code incluidos

Los costos se calculan con los precios actuales de Anthropic:

| Modelo | Input | Output | Cache read |
|--------|-------|--------|------------|
| Sonnet 4.6 | $3/MTok | $15/MTok | $0.30/MTok |
| Opus 4.8 | $15/MTok | $75/MTok | $1.50/MTok |
| Haiku 4.5 | $0.80/MTok | $4/MTok | $0.08/MTok |

---

## Estructura del proyecto

```
motoragentico-linux/
├── app.py                  # App principal Streamlit
├── run.sh                  # Script de inicio
├── modules/
│   ├── claude_data.py      # Lector de sesiones Claude Code
│   ├── hermes_data.py      # Integración con Hermes CLI
│   ├── obsidian_data.py    # Análisis del vault Obsidian
│   └── pricing.py          # Precios de modelos
└── .streamlit/
    └── config.toml         # Tema oscuro
```

---

## Comunidad

Este proyecto nació como reto dentro de la comunidad de IA de Benjamín — la idea era demostrar que con vibe coding se puede portar y construir herramientas reales en Linux sin ser programador.

Si lo mejorás, mandá un PR.
