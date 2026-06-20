import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timezone, timedelta

from modules.claude_data import get_summary as claude_summary
from modules.hermes_data import get_insights, get_stats, get_recent_sessions
from modules.obsidian_data import scan_vault
from modules.pricing import CLAUDE_SUBSCRIPTIONS, HERMES_SUBSCRIPTIONS

st.set_page_config(
    page_title="Motor Agéntico",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.metric-card {
    background: #1A1A2E;
    border: 1px solid #2D2D4E;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #7C3AED;
}
.metric-label {
    font-size: 0.85rem;
    color: #94A3B8;
    margin-top: 4px;
}
.stale-item {
    background: #2D1A1A;
    border-left: 3px solid #EF4444;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 4px 0;
    font-size: 0.85rem;
}
.recent-item {
    background: #1A2D1A;
    border-left: 3px solid #22C55E;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 4px 0;
    font-size: 0.85rem;
}
div[data-testid="stTabs"] button {
    font-size: 1rem;
    padding: 8px 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Motor Agéntico")
st.caption("Dashboard local · privado · solo lectura")

with st.sidebar:
    st.header("Configuración")
    obsidian_path = st.text_input(
        "Ruta de tu vault Obsidian",
        value="~/Developer/obsidian-code",
        help="Ruta absoluta o con ~ a tu carpeta de Obsidian",
    )
    days = st.slider("Período de análisis (días)", 7, 90, 30)
    st.divider()
    st.subheader("Plan Claude Code")
    claude_plan = st.selectbox("Suscripción", list(CLAUDE_SUBSCRIPTIONS.keys()))
    st.subheader("Plan Hermes")
    hermes_plan = st.selectbox("Suscripción", list(HERMES_SUBSCRIPTIONS.keys()))
    st.divider()
    if st.button("Actualizar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💸 Costos", "📈 ROI", "🧠 Memoria", "👀 Actividad", "🌙 El Sueño"
])


@st.cache_data(ttl=300)
def load_claude(d):
    return claude_summary(d)


@st.cache_data(ttl=300)
def load_hermes_insights(d):
    return get_insights(d)


@st.cache_data(ttl=300)
def load_hermes_stats():
    return get_stats()


@st.cache_data(ttl=300)
def load_hermes_sessions():
    return get_recent_sessions()


@st.cache_data(ttl=600)
def load_obsidian(path):
    return scan_vault(path)


with tab1:
    st.subheader(f"Gastos reales — últimos {days} días")

    claude_data = load_claude(days)
    hermes_data = load_hermes_insights(days)

    claude_cost = claude_data["total_cost_usd"]
    hermes_cost = 0.0  # local models = $0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${claude_cost:.2f}</div>
            <div class="metric-label">Claude Code (API)</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${hermes_cost:.2f}</div>
            <div class="metric-label">Hermes (local)</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        total = claude_cost + hermes_cost
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${total:.2f}</div>
            <div class="metric-label">Total combinado</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        daily = total / days if days > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${daily:.2f}</div>
            <div class="metric-label">Promedio diario</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Gasto por día (Claude Code)")
        by_day = claude_data.get("cost_by_day", {})
        if by_day:
            df_day = pd.DataFrame(
                sorted(by_day.items()), columns=["Fecha", "USD"]
            )
            fig = px.bar(
                df_day, x="Fecha", y="USD",
                color_discrete_sequence=["#7C3AED"],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#E2E8F0",
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(gridcolor="#2D2D4E"),
                yaxis=dict(gridcolor="#2D2D4E", tickprefix="$"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de costos en este período.")

    with col_right:
        st.subheader("Tokens Claude Code")
        input_t = claude_data.get("input_tokens", 0)
        output_t = claude_data.get("output_tokens", 0)
        cache_t = claude_data.get("output_tokens", 0)

        if input_t or output_t:
            fig_pie = go.Figure(data=[go.Pie(
                labels=["Input", "Output"],
                values=[input_t, output_t],
                hole=0.5,
                marker_colors=["#7C3AED", "#06B6D4"],
            )])
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#E2E8F0",
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            )
            fig_pie.add_annotation(
                text=f"{(input_t+output_t):,}<br>tokens",
                x=0.5, y=0.5, font_size=14,
                showarrow=False, font_color="#E2E8F0",
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Sin datos de tokens.")

    st.subheader("Hermes — últimos 7 días")
    h7 = load_hermes_insights(7)
    hc1, hc2, hc3 = st.columns(3)
    hc1.metric("Sesiones", h7["sessions"])
    hc2.metric("Mensajes", h7["messages"])
    hc3.metric("Tokens totales", f"{h7['total_tokens']:,}")

    if h7.get("models"):
        df_models = pd.DataFrame(h7["models"])
        st.dataframe(
            df_models.rename(columns={"name": "Modelo", "sessions": "Sesiones", "tokens": "Tokens"}),
            use_container_width=True, hide_index=True,
        )


with tab2:
    st.subheader("ROI — ¿Suscripción o API?")

    claude_sub_cost = CLAUDE_SUBSCRIPTIONS[claude_plan]
    hermes_sub_cost = HERMES_SUBSCRIPTIONS[hermes_plan]

    claude_data_roi = load_claude(30)
    api_cost_monthly = claude_data_roi["total_cost_usd"]

    st.markdown("### Claude Code")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${claude_sub_cost:.0f}/mes</div>
            <div class="metric-label">Suscripción {claude_plan}</div>
        </div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${api_cost_monthly:.2f}/mes</div>
            <div class="metric-label">Tu costo API real (30d)</div>
        </div>""", unsafe_allow_html=True)

    with col_c:
        diff = claude_sub_cost - api_cost_monthly
        if diff > 0:
            verdict = f"Pagas ${diff:.2f} de más"
            color = "#EF4444"
            recommendation = f"Con tu uso actual, la API te sale ${diff:.2f}/mes más barata que {claude_plan}."
        else:
            verdict = f"Ahorrás ${abs(diff):.2f}"
            color = "#22C55E"
            recommendation = f"La suscripción {claude_plan} te conviene — usás más de lo que pagás."

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{color}">{verdict}</div>
            <div class="metric-label">vs {claude_plan}</div>
        </div>""", unsafe_allow_html=True)

    st.info(f"**Veredicto:** {recommendation}")

    st.divider()
    st.markdown("### Proyección anual")

    months = list(range(1, 13))
    sub_cumulative = [claude_sub_cost * m for m in months]
    api_cumulative = [api_cost_monthly * m for m in months]

    fig_roi = go.Figure()
    fig_roi.add_trace(go.Scatter(
        x=months, y=sub_cumulative,
        name=f"Suscripción {claude_plan}",
        line=dict(color="#7C3AED", width=2),
        fill="tozeroy", fillcolor="rgba(124,58,237,0.1)",
    ))
    fig_roi.add_trace(go.Scatter(
        x=months, y=api_cumulative,
        name="API (uso actual)",
        line=dict(color="#06B6D4", width=2),
        fill="tozeroy", fillcolor="rgba(6,182,212,0.1)",
    ))
    fig_roi.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E2E8F0",
        xaxis=dict(title="Mes", gridcolor="#2D2D4E"),
        yaxis=dict(title="USD acumulado", gridcolor="#2D2D4E", tickprefix="$"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_roi, use_container_width=True)

    with st.expander("Simular con otro volumen de uso"):
        usage_multiplier = st.slider(
            "Si usaras X veces más de lo que usás ahora", 0.5, 10.0, 1.0, 0.5
        )
        simulated_api = api_cost_monthly * usage_multiplier
        st.write(f"API estimada: **${simulated_api:.2f}/mes**")
        if simulated_api < claude_sub_cost:
            st.success(f"Con ese volumen, la API sigue siendo más barata (${simulated_api:.2f} vs ${claude_sub_cost:.0f}).")
        else:
            breakeven = claude_sub_cost / api_cost_monthly if api_cost_monthly > 0 else 0
            st.warning(f"La suscripción empieza a convenir cuando usás {breakeven:.1f}x tu volumen actual.")


with tab3:
    st.subheader("Memoria — Vault Obsidian")

    vault_data = load_obsidian(obsidian_path)

    if vault_data.get("error"):
        st.error(vault_data["error"])
        st.info("Configurá la ruta del vault en el panel lateral izquierdo.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Archivos totales", vault_data["total_files"])
        m2.metric("Palabras totales", f"{vault_data['total_words']:,}")
        m3.metric("Archivos obsoletos", vault_data["stale_count"], help="+90 días sin editar")
        pct_stale = (vault_data["stale_count"] / vault_data["total_files"] * 100) if vault_data["total_files"] else 0
        m4.metric("% sin tocar", f"{pct_stale:.0f}%")

        col_mem1, col_mem2 = st.columns(2)

        with col_mem1:
            st.markdown("#### Tags más usados")
            if vault_data["top_tags"]:
                tags_df = pd.DataFrame(vault_data["top_tags"], columns=["Tag", "Apariciones"])
                fig_tags = px.bar(
                    tags_df, x="Apariciones", y="Tag",
                    orientation="h",
                    color_discrete_sequence=["#7C3AED"],
                )
                fig_tags.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#E2E8F0",
                    margin=dict(l=0, r=0, t=10, b=0),
                    yaxis=dict(autorange="reversed", gridcolor="#2D2D4E"),
                    xaxis=dict(gridcolor="#2D2D4E"),
                    showlegend=False,
                    height=350,
                )
                st.plotly_chart(fig_tags, use_container_width=True)
            else:
                st.info("No se encontraron tags.")

        with col_mem2:
            st.markdown("#### Editados recientemente")
            for f in vault_data["recent_files"][:8]:
                days_ago = f["days_since_edit"]
                label = "hoy" if days_ago == 0 else f"hace {days_ago}d"
                st.markdown(
                    f'<div class="recent-item">📄 <b>{f["name"]}</b> · {label} · {f["words"]} palabras</div>',
                    unsafe_allow_html=True,
                )

        if vault_data["stale_files"]:
            st.divider()
            st.markdown(f"#### ⚠️ Archivos obsoletos (+90 días) — {vault_data['stale_count']} total")
            st.caption("Estos archivos no se han editado en 3 meses. Considerá archivarlos o actualizarlos.")
            for f in vault_data["stale_files"][:15]:
                st.markdown(
                    f'<div class="stale-item">🗂️ <b>{f["name"]}</b> · {f["days_since_edit"]} días · {f["words"]} palabras</div>',
                    unsafe_allow_html=True,
                )


with tab4:
    st.subheader("Actividad en tiempo real")

    stats = load_hermes_stats()
    sessions_list = load_hermes_sessions()
    claude_recent = load_claude(7)

    col_act1, col_act2, col_act3 = st.columns(3)
    col_act1.metric("Sesiones Hermes (total)", stats["total_sessions"])
    col_act2.metric("Mensajes Hermes (total)", stats["total_messages"])
    col_act3.metric("DB Hermes", stats["db_size"])

    st.divider()
    col_a4, col_a5 = st.columns(2)

    with col_a4:
        st.markdown("#### Sesiones Claude Code recientes")
        if claude_recent["sessions"]:
            for s in claude_recent["sessions"][:8]:
                project_short = s["project"].split("/")[-1] if s["project"] else "home"
                ts = s["last_ts"].strftime("%d/%m %H:%M") if s["last_ts"] else "—"
                cost_str = f"${s['cost_usd']:.3f}"
                tokens_str = f"{s['total_tokens']:,} tok"
                st.markdown(
                    f'<div class="recent-item">🤖 <b>{project_short}</b> · {ts} · {cost_str} · {tokens_str}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No hay sesiones recientes de Claude Code.")

    with col_a5:
        st.markdown("#### Sesiones Hermes recientes")
        for s in sessions_list[:8]:
            title = s["title"][:35] + "…" if len(s["title"]) > 35 else s["title"]
            st.markdown(
                f'<div class="recent-item">🟣 <b>{title}</b> · {s["last_active"]}</div>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown("#### Actividad semanal Hermes")
    h_insights = load_hermes_insights(days)
    if h_insights.get("activity_by_day"):
        day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_labels = {"Mon": "Lun", "Tue": "Mar", "Wed": "Mié", "Thu": "Jue",
                      "Fri": "Vie", "Sat": "Sáb", "Sun": "Dom"}
        act_data = h_insights["activity_by_day"]
        df_act = pd.DataFrame([
            {"Día": day_labels.get(d, d), "Sesiones": act_data.get(d, 0)}
            for d in day_order
        ])
        fig_act = px.bar(
            df_act, x="Día", y="Sesiones",
            color_discrete_sequence=["#7C3AED"],
        )
        fig_act.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E2E8F0",
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor="#2D2D4E"),
            yaxis=dict(gridcolor="#2D2D4E"),
            showlegend=False,
        )
        st.plotly_chart(fig_act, use_container_width=True)

        if h_insights.get("peak_hours"):
            st.info(f"**Horario pico:** {h_insights['peak_hours']}")


with tab5:
    st.subheader("El Sueño — Análisis de tu operación")
    st.caption("Analiza cómo trabajás y sugiere optimizaciones automáticas.")

    claude_data_s = load_claude(30)
    hermes_data_s = load_hermes_insights(30)
    sessions_s = claude_data_s.get("sessions", [])

    st.markdown("### Tu perfil de trabajo")
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        total_sessions = claude_data_s["sessions_count"] + hermes_data_s.get("sessions", 0)
        total_cost = claude_data_s["total_cost_usd"]
        hermes_hours = hermes_data_s.get("active_time_hours", 0)

        intensity = "Alta" if total_sessions > 20 else ("Media" if total_sessions > 5 else "Baja")
        st.markdown(f"""
        <div class="metric-card" style="text-align:left; padding: 20px;">
            <div style="font-size:1.1rem; color:#7C3AED; margin-bottom:12px;">📊 Intensidad de uso: <b>{intensity}</b></div>
            <div style="color:#94A3B8; font-size:0.9rem; line-height:1.8;">
            • <b>{total_sessions}</b> sesiones en 30 días<br>
            • <b>{hermes_hours:.1f}h</b> activo en Hermes<br>
            • <b>${total_cost:.2f}</b> gastado en API Claude<br>
            • <b>{claude_data_s['total_tokens']:,}</b> tokens de Claude Code
            </div>
        </div>""", unsafe_allow_html=True)

    with col_s2:
        projects = {}
        for s in sessions_s:
            p = s["project"].split("/")[-1] if s["project"] else "home"
            projects[p] = projects.get(p, 0) + s["cost_usd"]

        if projects:
            top_project = max(projects, key=projects.get)
            st.markdown(f"""
            <div class="metric-card" style="text-align:left; padding: 20px;">
                <div style="font-size:1.1rem; color:#06B6D4; margin-bottom:12px;">🎯 Proyecto principal</div>
                <div style="color:#E2E8F0; font-size:1.2rem; font-weight:bold;">{top_project}</div>
                <div style="color:#94A3B8; font-size:0.85rem;">${projects[top_project]:.3f} gastados en 30 días</div>
                <br>
                <div style="color:#94A3B8; font-size:0.85rem;">Proyectos activos: {len(projects)}</div>
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### Sugerencias automáticas")

    suggestions = []

    if total_cost > 0 and total_cost < CLAUDE_SUBSCRIPTIONS.get("Pro", 20) * 0.5:
        suggestions.append({
            "icon": "💡",
            "title": "Considerá el plan API",
            "body": f"Gastás ${total_cost:.2f}/mes en Claude — menos del 50% de Pro. La API directa te sale más barata.",
            "priority": "alta",
        })

    if hermes_data_s.get("sessions", 0) > 0 and claude_data_s["sessions_count"] > 0:
        suggestions.append({
            "icon": "🔀",
            "title": "Usás dos agentes en paralelo",
            "body": "Tenés tanto Hermes como Claude Code activos. Considerá definir roles: Hermes para tareas conversacionales, Claude Code para código.",
            "priority": "media",
        })

    vault_data_s = load_obsidian(obsidian_path)
    if not vault_data_s.get("error") and vault_data_s.get("stale_count", 0) > 10:
        suggestions.append({
            "icon": "🧹",
            "title": f"Memoria desactualizada ({vault_data_s['stale_count']} archivos)",
            "body": "Más del 10% de tu vault no se toca hace 3+ meses. Una sesión de limpieza semanal de 15 min puede mejorar la calidad de tus prompts.",
            "priority": "media",
        })

    if hermes_data_s.get("active_time_hours", 0) > 20:
        suggestions.append({
            "icon": "⏰",
            "title": "Alto volumen de uso de Hermes",
            "body": f"Llevás {hermes_data_s['active_time_hours']:.0f}h activo en Hermes. Revisá qué tareas repetitivas podrías empaquetar como skills para ahorrar tiempo.",
            "priority": "alta",
        })

    if not suggestions:
        suggestions.append({
            "icon": "✅",
            "title": "Todo en orden",
            "body": "Tu operación con IA está bien calibrada por ahora. Seguí acumulando datos para obtener sugerencias más precisas.",
            "priority": "baja",
        })

    priority_colors = {"alta": "#EF4444", "media": "#F59E0B", "baja": "#22C55E"}

    for s in suggestions:
        color = priority_colors.get(s["priority"], "#7C3AED")
        st.markdown(f"""
        <div style="background:#1A1A2E; border-left: 4px solid {color}; padding: 16px 20px; border-radius: 8px; margin: 8px 0;">
            <div style="font-size:1.05rem; margin-bottom:6px;">{s['icon']} <b>{s['title']}</b>
                <span style="color:{color}; font-size:0.75rem; margin-left:8px; text-transform:uppercase;">{s['priority']}</span>
            </div>
            <div style="color:#94A3B8; font-size:0.9rem;">{s['body']}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### Proyectos por gasto")
    if projects:
        df_proj = pd.DataFrame(
            [(k, v) for k, v in sorted(projects.items(), key=lambda x: x[1], reverse=True)],
            columns=["Proyecto", "USD"],
        )
        fig_proj = px.bar(
            df_proj, x="Proyecto", y="USD",
            color_discrete_sequence=["#7C3AED"],
            text_auto=".3f",
        )
        fig_proj.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E2E8F0",
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor="#2D2D4E"),
            yaxis=dict(gridcolor="#2D2D4E", tickprefix="$"),
            showlegend=False,
        )
        st.plotly_chart(fig_proj, use_container_width=True)
